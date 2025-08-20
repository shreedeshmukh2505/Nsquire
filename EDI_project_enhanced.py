import re
import json
from fuzzywuzzy import process, fuzz
from typing import Dict, List
import cohere
from argostranslate import package, translate
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import werkzeug
from werkzeug.utils import secure_filename
import os
import subprocess
import requests

# Import our custom modules
from pdf_parser import EnhancedCollegeParser
from database import CollegeDatabase

load_dotenv()

# Cohere API setup
cohere_api_key = os.getenv('COHERE_API_KEY')
co = cohere.Client(cohere_api_key) if cohere_api_key else None

# Initialize database and parser
db = CollegeDatabase()
pdf_parser = EnhancedCollegeParser()

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load dataset
def load_data(file_path='dataset1.json'):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None

# Detect language (English vs Hinglish)
def detect_language(sentence):
    hinglish_keywords = {"kya", "ka", "hai", "kyunki", "aur", "kaise", "ki", "ke"}
    words = set(sentence.lower().split())
    if words & hinglish_keywords:
        return "hinglish"
    return "english"

# Enhanced college search from database
def search_colleges_from_database(query, limit=10):
    """Search colleges from the database using the existing search function."""
    try:
        colleges = db.search_colleges(query)
        return colleges[:limit] if colleges else []
    except Exception as e:
        print(f"Error searching colleges: {e}")
        return []

# Get college details from database
def get_college_details_from_database(college_code):
    """Get detailed college information from database."""
    try:
        college_data = db.get_college_data(college_code=college_code)
        return college_data
    except Exception as e:
        print(f"Error getting college details: {e}")
        return None

# Enhanced intent classification for college queries
def classify_college_query(user_query):
    """Classify the type of college-related query."""
    query_lower = user_query.lower()
    
    # College search patterns
    if any(word in query_lower for word in ['find', 'search', 'which', 'what colleges', 'colleges in', 'colleges near']):
        return 'college_search'
    
    # Cutoff patterns
    if any(word in query_lower for word in ['cutoff', 'rank', 'percentage', 'admission', 'eligibility']):
        return 'cutoff_query'
    
    # Branch patterns
    if any(word in query_lower for word in ['branch', 'course', 'stream', 'department']):
        return 'branch_query'
    
    # College info patterns
    if any(word in query_lower for word in ['info', 'details', 'about', 'tell me about']):
        return 'college_info'
    
    # Comparison patterns
    if any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference']):
        return 'comparison_query'
    
    return 'general_query'

# Extract college name from query
def extract_college_name(query):
    """Extract college name from user query."""
    # Common college name patterns
    college_patterns = [
        r'COEP',
        r'PICT',
        r'VIT',
        r'SPIT',
        r'DJ Sanghvi',
        r'Thadomal Shahani',
        r'Government College of Engineering',
        r'Walchand College',
        r'MIT',
        r'Pune University',
        r'University of Mumbai'
    ]
    
    for pattern in college_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return match.group(0)
    
    # Try to extract using Cohere if available
    if co:
        try:
            response = co.chat(
                model="command-r-plus",
                message=f"Extract the college name from this query: '{query}'. Return only the college name or 'None' if not found.",
                max_tokens=20,
                temperature=0.1
            )
            college_name = response.text.strip()
            if college_name.lower() != 'none':
                return college_name
        except:
            pass
    
    return None

# Extract branch name from query
def extract_branch_name(query):
    """Extract branch/course name from user query."""
    branch_patterns = [
        r'Computer Science',
        r'Information Technology',
        r'Mechanical Engineering',
        r'Electrical Engineering',
        r'Electronics',
        r'Civil Engineering',
        r'Chemical Engineering',
        r'Biotechnology',
        r'AI/ML',
        r'Data Science'
    ]
    
    for pattern in branch_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

# Process college search queries with improved formatting
def process_college_search(query):
    """Process queries asking to find/search colleges with clean formatting."""
    # Extract search terms
    search_terms = query.lower()
    
    # Remove common words
    common_words = ['find', 'search', 'which', 'what', 'colleges', 'in', 'near', 'around', 'for']
    for word in common_words:
        search_terms = search_terms.replace(word, '').strip()
    
    # Search in database
    colleges = search_colleges_from_database(search_terms, limit=15)
    
    if not colleges:
        return "I couldn't find any colleges matching your search. Could you please provide more specific details?"
    
    response = f"**Found {len(colleges)} colleges matching your search:**\n\n"
    
    for i, college in enumerate(colleges[:10], 1):
        response += f"{i}. **{college['college_name']}**\n"
        response += f"   Code: {college['college_code']}\n"
        if college.get('branches'):
            response += f"   Branches: {len(college['branches'])} available\n"
        response += "\n"
    
    if len(colleges) > 10:
        response += f"... and {len(colleges) - 10} more colleges available.\n\n"
    
    response += "**How to get more details:**\n"
    response += "• Ask about a specific college: \"Tell me about COEP\"\n"
    response += "• Ask about cutoffs: \"What's the cutoff for COEP?\"\n"
    response += "• Ask about branches: \"COEP Computer Science cutoff\""
    
    return response

# Process cutoff queries with improved formatting
def process_cutoff_query(query, college_name=None, branch_name=None):
    """Process queries about cutoffs, ranks, and eligibility with clean formatting."""
    if not college_name:
        college_name = extract_college_name(query)
    
    if not branch_name:
        branch_name = extract_branch_name(query)
    
    if not college_name:
        return "I'd be happy to help with cutoff information! Please mention the college name you're interested in."
    
    # Search for college in database
    colleges = search_colleges_from_database(college_name, limit=5)
    
    if not colleges:
        return f"I couldn't find information about {college_name}. Could you please check the spelling or try a different college name?"
    
    # Get detailed information for the best match
    best_match = colleges[0]
    college_details = get_college_details_from_database(best_match['college_code'])
    
    if not college_details:
        return f"I found {best_match['college_name']} but couldn't retrieve detailed cutoff information."
    
    # Clean, readable response format
    response = f"**{best_match['college_name']}**\n"
    response += f"College Code: {best_match['college_code']}\n\n"
    
    if college_details.get('branches'):
        response += f"**Available Branches:** {len(college_details['branches'])}\n\n"
        
        # Filter by branch if specified
        relevant_branches = college_details['branches']
        if branch_name:
            relevant_branches = [b for b in relevant_branches if branch_name.lower() in b['branch_name'].lower()]
            if relevant_branches:
                response += f"**Showing results for:** {branch_name}\n\n"
        
        for i, branch in enumerate(relevant_branches[:5], 1):  # Show first 5 branches
            response += f"**{i}. {branch['branch_name']}**\n"
            response += f"Status: {branch.get('status', 'Not specified')}\n"
            
            if branch.get('cutoff_data'):
                response += f"**Cutoff Information:**\n"
                for cutoff in branch['cutoff_data'][:3]:  # Show first 3 cutoffs
                    response += f"• {cutoff['category']} (Stage {cutoff['stage']})\n"
                    response += f"  Rank: {cutoff['rank']:,}\n"
                    response += f"  Percentage: {cutoff['percentage']:.2f}%\n"
                response += "\n"
            else:
                response += "No cutoff data available for this branch.\n\n"
    else:
        response += "No branch information available for this college.\n\n"
    
    # Add helpful suggestions
    response += "**Need more specific information?**\n"
    response += "• Ask for a specific branch: \"COEP Computer Science cutoff\"\n"
    response += "• Ask for a specific category: \"COEP GOPENS cutoff\"\n"
    response += "• Compare branches: \"Compare COEP CS vs Electronics\""
    
    return response

# Process college info queries with improved formatting
def process_college_info_query(query, college_name=None):
    """Process queries asking for general college information with clean formatting."""
    if not college_name:
        college_name = extract_college_name(query)
    
    if not college_name:
        return "I'd be happy to provide college information! Please mention the college name you're interested in."
    
    # Search for college
    colleges = search_colleges_from_database(college_name, limit=3)
    
    if not colleges:
        return f"I couldn't find information about {college_name}. Could you please check the spelling?"
    
    best_match = colleges[0]
    college_details = get_college_details_from_database(best_match['college_code'])
    
    if not college_details:
        return f"I found {best_match['college_name']} but couldn't retrieve detailed information."
    
    response = f"**{best_match['college_name']}**\n"
    response += f"College Code: {best_match['college_code']}\n\n"
    
    if college_details.get('branches'):
        response += f"**Total Branches Available:** {len(college_details['branches'])}\n\n"
        response += "**Available Branches:**\n"
        
        for i, branch in enumerate(college_details['branches'][:8], 1):
            response += f"{i}. {branch['branch_name']}\n"
            if branch.get('status'):
                response += f"   Status: {branch['status']}\n"
            if branch.get('cutoff_data'):
                response += f"   Cutoff data: {len(branch['cutoff_data'])} entries available\n"
            response += "\n"
        
        if len(college_details['branches']) > 8:
            response += f"... and {len(college_details['branches']) - 8} more branches available.\n\n"
    
    response += "**What you can ask me:**\n"
    response += "• Cutoff details: \"What's the cutoff for COEP Computer Science?\"\n"
    response += "• Branch comparison: \"Compare COEP CS vs Electronics\"\n"
    response += "• Admission info: \"What are the admission criteria for COEP?\"\n"
    response += "• Category-specific cutoffs: \"GOPENS cutoff for COEP CS\""
    
    return response

# Llama 3 local integration
def query_llama_local(prompt, max_tokens=200):
    """Query Llama 3 local model using ollama."""
    try:
        # Try using ollama if available
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'gemma3:1b',  # Adjust model name as needed
                'prompt': prompt,
                'stream': False,
                'options': {
                    'num_predict': max_tokens,
                    'temperature': 0.7
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '')
        else:
            return None
            
    except requests.exceptions.RequestException:
        # Fallback to subprocess if ollama API is not available
        try:
            result = subprocess.run(
                ['ollama', 'run', 'gemma3:1b', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    return None

# Enhanced main query processing with improved formatting
def process_user_query_enhanced(user_query):
    """Enhanced main function with clean response formatting."""
    detected_language = detect_language(user_query)
    
    # First, classify the query type
    query_type = classify_college_query(user_query)
    
    print(f"Query type: {query_type}")
    print(f"Language: {detected_language}")
    
    # Handle college-specific queries
    if query_type == 'college_search':
        response = process_college_search(user_query)
        return response
    
    elif query_type == 'cutoff_query':
        college_name = extract_college_name(user_query)
        branch_name = extract_branch_name(user_query)
        response = process_cutoff_query(user_query, college_name, branch_name)
        return response
    
    elif query_type == 'college_info':
        college_name = extract_college_name(user_query)
        response = process_college_info_query(user_query, college_name)
        return response
    
    elif query_type == 'branch_query':
        college_name = extract_college_name(user_query)
        branch_name = extract_branch_name(user_query)
        if college_name and branch_name:
            response = process_cutoff_query(user_query, college_name, branch_name)
        else:
            response = "I'd be happy to help with branch information! Please mention both the college and branch names."
        return response
    
    # For general queries, try Gemma 3 local first
    print("Attempting to use Gemma 3 local for general query...")
    
    # Create a context-aware prompt for Gemma
    context_prompt = f"""You are a helpful AI assistant for engineering college admissions in Maharashtra. 

Answer this question: "{user_query}"

If the question is about engineering colleges, engineering education, or college admissions in Maharashtra, mention that I can provide specific information about 1,393+ colleges from our database.

Give a clear, helpful, and direct answer. Be conversational and friendly."""

    llama_response = query_llama_local(context_prompt)
    
    if llama_response:
        print("Gemma 3 local response generated successfully")
        return llama_response
    
    # Fallback to Cohere if Llama is not available
    if co:
        print("Falling back to Cohere...")
        try:
            response = co.chat(
                model="command-r-plus",
                message=f"Answer this question helpfully: {user_query}",
                max_tokens=150,
                temperature=0.7
            )
            return response.text.strip()
        except Exception as e:
            print(f"Cohere error: {e}")
    
    # Final fallback with clean formatting
    return f"""I understand you're asking about: {user_query}

**I'm here to help!**

**For college questions:** I can provide detailed information about 1,393+ colleges in Maharashtra, including:
• Cutoff ranks and percentages
• Branch details and status
• College comparisons
• Admission information

**For general questions:** I'm happy to assist with any other topics!

**Try asking:**
• "What's the cutoff for COEP Computer Science?"
• "Find colleges in Pune"
• "How to prepare for engineering exams?" """

# Enhanced chat endpoint
@app.route('/chat', methods=['POST'])
def chat_enhanced():
    print("Enhanced chat endpoint hit!")
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        user_query = data.get('message', '')
        print(f"Received query: {user_query}")

        if not user_query:
            return jsonify({"error": "Please enter a valid query."}), 400

        # Process query using enhanced function
        response = process_user_query_enhanced(user_query)
        print(f"Generated response: {response}")

        return jsonify({"response": response})

    except Exception as e:
        print(f"Error in enhanced chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Keep existing endpoints for compatibility
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """Upload and parse PDF file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Parse the PDF
            parsed_data = pdf_parser.parse_pdf(filepath)
            
            if parsed_data.get("parsing_success"):
                # Store in database
                success = db.store_parsed_data(parsed_data)
                
                # Clean up uploaded file
                os.remove(filepath)
                
                if success:
                    return jsonify({
                        "message": "PDF parsed and stored successfully",
                        "total_colleges": parsed_data.get("total_colleges"),
                        "total_branches": parsed_data.get("total_branches"),
                        "total_cutoffs": parsed_data.get("total_cutoffs"),
                        "colleges": parsed_data.get("colleges", [])
                    })
                else:
                    return jsonify({"error": "Failed to store data in database"}), 500
            else:
                return jsonify({"error": "Failed to parse PDF"}), 500
        else:
            return jsonify({"error": "Invalid file type. Only PDF files are allowed."}), 400
        
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
    return jsonify({
        "status": "healthy",
        "message": "Enhanced EDI Chatbot is running",
        "features": [
            "College database queries (1,393+ colleges)",
            "Clean, readable response formatting",
            "Cutoff information",
            "Branch details",
            "Llama 3 local integration",
            "Cohere fallback",
            "PDF parsing and storage"
        ]
    })

# Ensure CORS is configured correctly
CORS(app, resources={r"/*": {"origins": "*"}})

# Run the enhanced chatbot
if __name__ == '__main__':
    print("🚀 Starting Enhanced EDI Chatbot...")
    print("📋 Features:")
    print("   - College database integration (1,393+ colleges)")
    print("   - Clean, readable response formatting")
    print("   - Cutoff and admission queries")
    print("   - Llama 3 local model integration")
    print("   - Cohere fallback")
    print("   - PDF parsing and storage")
    print("🌐 Server will be available at: http://localhost:5002")
    print("💬 Chat endpoint: POST /chat")
    print("❤️ Health check: GET /health")
    
    app.run(debug=True, host='0.0.0.0', port=5002)