#!/usr/bin/env python3
"""
Simplified Flask server for PDF parsing functionality.
This server provides the core PDF upload and parsing endpoints.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import werkzeug
from werkzeug.utils import secure_filename

# Import our custom modules
from pdf_parser import EnhancedCollegeParser
from database import CollegeDatabase

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database and parser
db = CollegeDatabase()
pdf_parser = EnhancedCollegeParser()

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Home endpoint with server information."""
    return jsonify({
        "message": "PDF Parser Server is running!",
        "endpoints": {
            "upload_pdf": "/upload-pdf (POST)",
            "get_colleges": "/colleges (GET)",
            "get_college": "/college/<code> (GET)",
            "database_stats": "/database-stats (GET)"
        }
    })

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """Upload and parse PDF file."""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Save file securely
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"Processing PDF: {filename}")
        
        # Parse the PDF
        parsed_data = pdf_parser.parse_pdf(filepath)
        
        if not parsed_data.get("parsing_success"):
            # Clean up file if parsing failed
            os.remove(filepath)
            return jsonify({"error": "Failed to parse PDF", "details": parsed_data.get("error")}), 400
        
        print(f"PDF parsed successfully: {parsed_data.get('college_name')}")
        
        # Store data in database
        storage_success = db.store_parsed_data(parsed_data)
        
        if not storage_success:
            # Clean up file if storage failed
            os.remove(filepath)
            return jsonify({"error": "Failed to store data in database"}), 500
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            "message": "PDF parsed and stored successfully",
            "total_colleges": parsed_data.get("total_colleges"),
            "total_branches": parsed_data.get("total_branches"),
            "total_cutoffs": parsed_data.get("total_cutoffs"),
            "colleges": parsed_data.get("colleges", [])
        })
        
    except Exception as e:
        print(f"Error in PDF upload: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/colleges', methods=['GET'])
def get_colleges():
    """Get list of all colleges in database."""
    try:
        query = request.args.get('search', '')
        if query:
            colleges = db.search_colleges(query)
        else:
            # Get all colleges (you might want to add pagination here)
            colleges = db.search_colleges('')
        
        return jsonify({"colleges": colleges})
        
    except Exception as e:
        print(f"Error getting colleges: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/college/<college_code>', methods=['GET'])
def get_college_details(college_code):
    """Get detailed information about a specific college."""
    try:
        college_data = db.get_college_data(college_code=college_code)
        
        if not college_data:
            return jsonify({"error": "College not found"}), 404
        
        return jsonify(college_data)
        
    except Exception as e:
        print(f"Error getting college details: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/database-stats', methods=['GET'])
def get_database_stats():
    """Get database statistics."""
    try:
        stats = db.get_database_stats()
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        stats = db.get_database_stats()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting PDF Parser Server...")
    print("📍 Server will be available at: http://localhost:5002")
    print("📚 Available endpoints:")
    print("   - GET  /              - Server information")
    print("   - POST /upload-pdf    - Upload and parse PDF")
    print("   - GET  /colleges      - List all colleges")
    print("   - GET  /college/<id>  - Get college details")
    print("   - GET  /database-stats - Database statistics")
    print("   - GET  /health        - Health check")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5002)
