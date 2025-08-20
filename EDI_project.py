# import re
# import json
# from fuzzywuzzy import process, fuzz
# from typing import Dict, List
# import cohere
# from argostranslate import package, translate
# from dotenv import load_dotenv
# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import werkzeug
# from werkzeug.utils import secure_filename
# import os

# # Import our custom modules
# from pdf_parser import EnhancedCollegeParser
# from database import CollegeDatabase

# load_dotenv()
# # Cohere API setup
# cohere_api_key = os.getenv('COHERE_API_KEY')  # Get the API key from the environment variable
# co = cohere.Client(cohere_api_key)

# # Initialize database and parser
# db = CollegeDatabase()
# pdf_parser = EnhancedCollegeParser()

# # Configure upload settings
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'pdf'}

# # Create uploads directory if it doesn't exist
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# app = Flask(__name__)
# CORS(app)  # Enable CORS for cross-origin requests

# # Configure upload folder
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# def allowed_file(filename):
#     """Check if file extension is allowed."""
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# # Load dataset
# def load_data(file_path='dataset1.json'):
#     try:
#         with open(file_path, 'r') as f:
#             data = json.load(f)
#         return data
#     except FileNotFoundError:
#         return None

# # Detect language (English vs Hinglish)
# def detect_language(sentence):
#     hinglish_keywords = {"kya", "ka", "hai", "kyunki", "aur", "kaise", "ki", "ke"}
#     words = set(sentence.lower().split())
#     if words & hinglish_keywords:  # Intersection of sets
#         return "hinglish"
#     return "english"

# # Fuzzy matching for college name
# def match_college_name(college_name, dataset):
#     if not college_name:
#         return None

#     # Attempt exact match first
#     college_data = next((college for college in dataset if college['name'].lower() == college_name.lower()), None)
#     if college_data:
#         return college_data

#     # Use fuzzy matching as a fallback
#     college_names = [college['name'] for college in dataset]
#     best_match, score = process.extractOne(college_name, college_names, scorer=fuzz.token_set_ratio)
#     if score > 75:  # Match threshold
#         return next((college for college in dataset if college['name'] == best_match), None)

#     return None

# # Setup translation languages for Argos Translate
# def setup_translation():
#     package.update_package_index()
#     available_packages = package.get_available_packages()
#     for pkg in available_packages:
#         if pkg.from_code == 'en' and pkg.to_code == 'hi':
#             package.install_from_path(pkg.download())

# def translate_text(from_lang, to_lang, text):
#     installed_languages = translate.get_installed_languages()
#     from_language = next((lang for lang in installed_languages if lang.code == from_lang), None)
#     to_language = next((lang for lang in installed_languages if lang.code == to_lang), None)

#     if from_language and to_language:
#         translation = from_language.get_translation(to_language)
#         return translation.translate(text)
#     else:
#         return "Translation service is not available."

# # Cohere-based intent and entity extraction for eligibility and best college queries
# def cohere_understand_query_eligibility(user_query):
#     prompt = (
#         f"Extract the following details from the user's query: '{user_query}'\n"
#         "Classify the query intent into one of the following categories: [cutoff/fees/highest_package/average_package/info/eligibility/best_college].\n"
#         "Identify the rank and category if the query is about rank-based college eligibility.\n"
#         "If the query asks about the best college from eligible options, classify it as 'best_college'.\n"
#         "Provide the response in the following JSON format:\n"
#         "{"
#         "\"intent\": \"[intent]\"," 
#         "\"college_name\": \"[college_name or 'None']\"," 
#         "\"branch\": \"[branch or 'None']\"," 
#         "\"year\": \"[year or 'None']\"," 
#         "\"rank\": \"[rank or 'None']\"," 
#         "\"category\": \"[category or 'None']\""
#         "}\n"
#     )
    
#     # Use chat API instead of generate
#     response = co.chat(
#         model="command-r-plus",  # Updated model name
#         message=prompt,
#         max_tokens=100,
#         temperature=0.5
#     )
#     return response.text.strip()

# # Cohere-based intent and entity extraction for other queries
# def cohere_understand_query(user_query):
#     prompt = (
#         f"Extract the following details from the user's query: '{user_query}'\n"
#         "Provide the response in the following format:\n"
#         "Intent: [cutoff/fees/highest_package/average_package/info]\n"
#         "College: [the college name, if mentioned, otherwise 'None']\n"
#         "Branch: [the branch name if mentioned, otherwise 'None']\n"
#         "Year: [the year if provided, otherwise 'None']"
#     )
    
#     # Use chat API instead of generate
#     response = co.chat(
#         model="command-r-plus",  # Updated model name
#         message=prompt,
#         max_tokens=50,
#         temperature=0.5
#     )
#     return response.text.strip()

# # Parse Cohere response for eligibility and best college queries
# def parse_cohere_response_eligibility(ai_response):
#     try:
#         entities = json.loads(ai_response)  # Attempt to parse JSON directly
#     except json.JSONDecodeError:
#         # If parsing fails, fallback to manual extraction
#         entities = {'intent': None, 'college_name': None, 'branch': None, 'year': None, 'rank': None, 'category': None}
#         lines = ai_response.split('\n')
#         for line in lines:
#             if ':' in line:
#                 key, value = line.split(':', 1)
#                 key = key.strip().lower()
#                 value = value.strip()
#                 if key in entities and value.lower() != 'none':
#                     entities[key] = value
#     return entities

# # Parse Cohere response for other queries
# def parse_cohere_response(ai_response):
#     entities = {'intent': None, 'college_name': None, 'branch': None, 'year': None}
#     lines = ai_response.split('\n')
#     for line in lines:
#         if ':' in line:
#             key, value = line.split(':', 1)
#             key = key.strip().lower()
#             value = value.strip()
#             if 'intent' in key and value.lower() != 'none':
#                 entities['intent'] = value
#             elif 'college' in key and value.lower() != 'none':
#                 entities['college_name'] = value
#             elif 'branch' in key and value.lower() != 'none':
#                 entities['branch'] = value
#             elif 'year' in key and value.lower() != 'none':
#                 entities['year'] = value
#     return entities

# # Find eligible colleges based on rank and category
# def find_eligible_colleges(rank, category, dataset):
#     eligible_colleges = []
#     for college in dataset:
#         eligible_branches = []
#         for course in college.get('courses', []):
#             cutoffs = course.get('cutoffs', {}).get('2024', {})  # Fetch cutoffs for the year 2024
#             cutoff_rank = cutoffs.get(category, None)  # Use the specified category
#             if cutoff_rank and rank <= cutoff_rank:
#                 eligible_branches.append(course['name'])

#         # Sort branches and take the top 2
#         eligible_branches = sorted(eligible_branches)[:2]
#         if eligible_branches:
#             eligible_colleges.append({
#                 "college": college['name'],
#                 "branches": eligible_branches,
#                 "rating": college['rating']
#             })

#     # Limit to 7 unique colleges
#     return sorted(eligible_colleges, key=lambda x: x['rating'], reverse=True)[:7]


# # Find best college from eligible entries
# def find_best_college_and_branch(eligible_entries):
#     if not eligible_entries:
#         return None
#     # Select the college with the highest rating and its most competitive branch
#     best_entry = eligible_entries[0]
#     return {
#         "college": best_entry["college"],
#         "branch": best_entry["branches"][0],  # Top branch
#         "rating": best_entry["rating"]
#     }

# # Generate best college response
# import re
# def generate_best_college_response(best_entry, language):
#     if not best_entry:
#         if language == 'hinglish':
#             return "Maaf kijiye, mujhe aapke eligible colleges mein se best college nahi mila."
#         else:
#             return "Sorry, I couldn't determine the best college from your eligible entries."

#     # Generate an explanation using Cohere
#     prompt = (
#         f"Why is {best_entry['college']} the best choice for the branch {best_entry['branch']}? "
#         f"The college has a rating of {best_entry['rating']}/5. Use bold text for section headers like 'Academic Reputation:' "
#         f"and highlight its academic reputation, facilities, and other notable features."
#     )
    
#     # Use chat API instead of generate
#     response = co.chat(
#         model="command-r-plus",  # Updated model name
#         message=prompt,
#         max_tokens=300,
#         temperature=0.4
#     )
#     explanation = response.text.strip()

#     # Handle both standard bold markdown (**text**) and section headers
#     explanation = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', explanation)
#     explanation = re.sub(r'##\s*(.*?):', r'<strong>\1:</strong>', explanation)
    
#     # Ensure section headers like "Academic Reputation:" are bold
#     explanation = re.sub(r'([A-Za-z\s]+):', r'<strong>\1:</strong>', explanation)

#     if language == 'hinglish':
#         translated_explanation = translate_text('en', 'hi', explanation)
#         return f"{best_entry['college']} branch {best_entry['branch']} ke saath sabse acha college hai.\n\n{translated_explanation}"
#     else:
#         return f"The best college is {best_entry['college']} with branch {best_entry['branch']}.\n\n{explanation}"

# # Generate eligibility response
# def generate_eligibility_response(eligible_entries, language='english'):
#     if not eligible_entries:
#         if language == 'hinglish':
#             return "Maaf kijiye, aapke rank ke liye koi college nahi mila."
#         else:
#             return "Sorry, no colleges were found for your rank."

#     response = "Eligible colleges and top branches:\n\n" if language == 'english' else "Yogya college aur unke top branch:\n\n"
    
#     for entry in eligible_entries:
#         # Add college name
#         response += f"{entry['college']}\n"
#         # Add branches with indentation and separate them with newlines
#         for branch in entry['branches']:
#             response += f"- {branch}\n"
#         # Add extra newline after each college's complete entry
#         response += "\n"
    
#     return response.rstrip()  # Remove trailing whitespace while preserving intended line breaks

# # Get cutoff details
# def get_cutoff_details(college_data, branch_name=None, year=None):
#     year = year if year else '2024'  # Default to 2024
#     branch_cutoffs = []

#     for course in college_data['courses']:
#         if branch_name and branch_name.lower() not in course['name'].lower():
#             continue
#         cutoff = course['cutoffs'].get(year, {})
#         branch_cutoffs.append({
#             'branch': course['name'],
#             'cutoff': cutoff
#         })

#     return branch_cutoffs

# # Generate cutoff response
# def generate_cutoff_response(branch_cutoffs, college_name, language='english'):
#     if not branch_cutoffs:
#         if language == 'hinglish':
#             return "Maaf kijiye, is branch ke liye cutoff details nahi mili."
#         else:
#             return "Sorry, cutoff details for this branch are not available."

#     # Create response with HTML formatting
#     response = f"""<div class='cutoff-container'>
#     <h3 class='college-name'>Cutoff Details for {college_name}</h3>
#     <div class='branches-container'>"""

#     # Sort branches alphabetically
#     sorted_branches = sorted(branch_cutoffs, key=lambda x: x['branch'])

#     for branch in sorted_branches:
#         response += f"""
#         <div class='branch-item'>
#             <h4 class='branch-name'>{branch['branch']}</h4>
#             <div class='cutoff-details'>"""
        
#         for category, rank in branch['cutoff'].items():
#             formatted_rank = f"{rank:,}"
#             response += f"""
#                 <div class='category-item'>
#                     <span class='category'>{category}:</span>
#                     <span class='rank'>{formatted_rank}</span>
#                 </div>"""
        
#         response += """
#             </div>
#         </div>"""

#     response += """
#     </div>
# </div>"""

#     return response

# # Generate dynamic response for college-specific queries
# def generate_dynamic_response_college(intent, college_data, language='english', branch=None, year=None):
#     if not college_data:
#         if language == 'hinglish':
#             return "Maaf kijiye, mujhe college ke baare mein jaankari nahi mili."
#         else:
#             return "Sorry, I couldn't find information about the college."

#     if intent == 'cutoff':
#         branch_cutoffs = get_cutoff_details(college_data, branch, year)
#         return generate_cutoff_response(branch_cutoffs, college_data['name'], language)

#     elif intent == 'fees':
#         # Fetch the fee of the first course
#         annual_fee = college_data['courses'][0]['annual_fee']
#         if language == 'hinglish':
#             return f"{college_data['name']} ki fees:\nâ‚¹{annual_fee:,}/saal"
#         else:
#             return f"The fees for {college_data['name']} are:\nâ‚¹{annual_fee:,}/year"

#     elif intent == 'highest_package' or intent=='highest_salary':
#         highest_package = college_data['placements']['highest_package']
#         if language == 'hinglish':
#             return f"{college_data['name']} ka highest package â‚¹{highest_package:,}/saal hai."
#         else:
#             return f"The highest package for {college_data['name']} is â‚¹{highest_package:,}/year."

#     elif intent == 'average_package' or intent=='highest_salary':
#         avg_package = college_data['placements']['average_package']
#         if language == 'hinglish':
#             return f"{college_data['name']} ka average package â‚¹{avg_package:,}/saal hai."
#         else:
#             return f"The average package for {college_data['name']} is â‚¹{avg_package:,}/year."

#     elif intent == 'info':
#         location = college_data['location']
#         rating = college_data['rating']
#         facilities = ", ".join(college_data['facilities'])
#         if language == 'hinglish':
#             return (f"{college_data['name']} ki location {location} hai aur rating {rating}/5 hai. Facilities mein shamil hain: {facilities}.")
#         else:
#             return (f"{college_data['name']} is located in {location}, has a rating of {rating}/5. Facilities include: {facilities}.")

#     return "Sorry, I couldn't understand your query."

# # Generate dynamic response for eligibility and best college queries
# def generate_dynamic_response_eligibility(intent, language='english', rank=None, category=None, dataset=None, eligible_entries=None):
#     if intent == 'eligibility':
#         eligible_entries = find_eligible_colleges(rank, category, dataset)
#         return generate_eligibility_response(eligible_entries, language)

#     if intent == 'best_college':
#         best_entry = find_best_college_and_branch(eligible_entries)
#         return generate_best_college_response(best_entry, language)

#     return "Sorry, I couldn't understand your query."

# # Add these methods at the end of the combined.py file
# # Main query processing function for general college queries
# def process_user_query(user_query, dataset):

#     detected_language = detect_language(user_query)

#     # First, try to process as an eligibility/best college query
#     ai_response_eligibility = cohere_understand_query_eligibility(user_query)
#     parsed_data_eligibility = parse_cohere_response_eligibility(ai_response_eligibility)
    
#     intent_eligibility = parsed_data_eligibility.get('intent', None)
    
#     # If it's an eligibility or best_college query, process it accordingly
#     if intent_eligibility in ['eligibility', 'best_college']:
#         rank = int(parsed_data_eligibility['rank']) if parsed_data_eligibility['rank'] and parsed_data_eligibility['rank'] != 'None' else None
#         category = parsed_data_eligibility['category'].upper() if parsed_data_eligibility['category'] and parsed_data_eligibility['category'] != 'None' else 'GOPEN'
        
#         if intent_eligibility == 'eligibility' and rank is not None:
#             eligible_entries = find_eligible_colleges(rank, category, dataset)
#             return generate_dynamic_response_eligibility(
#                 intent_eligibility, 
#                 language=detected_language, 
#                 rank=rank, 
#                 category=category, 
#                 dataset=dataset, 
#                 eligible_entries=eligible_entries
#             )
        
#         if intent_eligibility == 'best_college':
#             eligible_entries = find_eligible_colleges(rank if rank else 0, category, dataset)
#             return generate_dynamic_response_eligibility(
#                 intent_eligibility, 
#                 language=detected_language, 
#                 eligible_entries=eligible_entries
#             )
    
#     casual_response = handle_casual_conversation(user_query)
#     if casual_response:
#         return casual_response
    
#     # If not an eligibility query, process as a regular college query
#     ai_response = cohere_understand_query(user_query)
#     parsed_data = parse_cohere_response(ai_response)

#     intent = parsed_data['intent']
#     college_name = parsed_data['college_name']
#     branch_name = parsed_data['branch']
#     year = parsed_data['year']

#     college_data = match_college_name(college_name, dataset)
    
#     return generate_dynamic_response_college(
#         intent, 
#         college_data, 
#         language=detected_language, 
#         branch=branch_name, 
#         year=year
#     )


# def handle_casual_conversation(user_query):
#     """
#     Handle casual conversational queries using Cohere's generative model
#     """
#     # Predefined conversational intents
#     conversational_intents = [
#         "greeting", "small_talk", "how_are_you", "introduction", 
#         "farewell", "appreciation", "joke", "general_chat"
#     ]

#     # Prompt to classify the intent and generate an appropriate response
#     prompt = (
#         f"Classify the intent of this message: '{user_query}'\n"
#         "Possible intents: " + ", ".join(conversational_intents) + "\n"
#         "If the intent is casual/conversational, generate a friendly, natural response. "
#         "If it doesn't fit a conversational intent, return 'NOT_CONVERSATIONAL'.\n"
#         "Format your response as: 'Intent: [intent]\nResponse: [generated_response]'"
#     )

#     # Use chat API instead of generate
#     response = co.chat(
#         model="command-r-plus",  # Updated model name
#         message=prompt,
#         max_tokens=100,
#         temperature=0.7
#     )

#     # Process the generated response
#     generated_text = response.text.strip()
    
#     # Parse the response
#     lines = generated_text.split('\n')
#     intent = lines[0].split(': ')[1] if len(lines) > 0 and ':' in lines[0] else None
    
#     if intent and intent != 'NOT_CONVERSATIONAL':
#         response_text = lines[1].split(': ')[1] if len(lines) > 1 else generated_text
#         return response_text

#     return None


# # PDF Upload and Parsing Endpoints
# @app.route('/upload-pdf', methods=['POST'])
# def upload_pdf():
#     """Upload and parse PDF file."""
#     try:
#         # Check if file is present in request
#         if 'file' not in request.files:
#             return jsonify({"error": "No file provided"}), 400
        
#         file = request.files['file']
        
#         # Check if file is selected
#         if file.filename == '':
#             return jsonify({"error": "No file selected"}), 400
        
#         # Check if file type is allowed
#         if not allowed_file(file.filename):
#             return jsonify({"error": "Only PDF files are allowed"}), 400
        
#         # Save file securely
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         # Parse the PDF
#         parsed_data = pdf_parser.parse_pdf(filepath)
        
#         if not parsed_data.get("parsing_success"):
#             # Clean up file if parsing failed
#             os.remove(filepath)
#             return jsonify({"error": "Failed to parse PDF", "details": parsed_data.get("error")}), 400
        
#         # Store data in database
#         storage_success = db.store_parsed_data(parsed_data)
        
#         if not storage_success:
#             # Clean up file if storage failed
#             os.remove(filepath)
#             return jsonify({"error": "Failed to store data in database"}), 500
        
#         # Clean up uploaded file
#         os.remove(filepath)
        
#         return jsonify({
#             "message": "PDF parsed and stored successfully",
#             "college_name": parsed_data.get("college_name"),
#             "total_branches": parsed_data.get("total_branches"),
#             "college_code": parsed_data.get("college_code")
#         })
        
#     except Exception as e:
#         print(f"Error in PDF upload: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/colleges', methods=['GET'])
# def get_colleges():
#     """Get list of all colleges in database."""
#     try:
#         query = request.args.get('search', '')
#         if query:
#             colleges = db.search_colleges(query)
#         else:
#             # Get all colleges (you might want to add pagination here)
#             colleges = db.search_colleges('')
        
#         return jsonify({"colleges": colleges})
        
#     except Exception as e:
#         print(f"Error getting colleges: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/college/<college_code>', methods=['GET'])
# def get_college_details(college_code):
#     """Get detailed information about a specific college."""
#     try:
#         college_data = db.get_college_data(college_code=college_code)
        
#         if not college_data:
#             return jsonify({"error": "College not found"}), 404
        
#         return jsonify(college_data)
        
#     except Exception as e:
#         print(f"Error getting college details: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/database-stats', methods=['GET'])
# def get_database_stats():
#     """Get database statistics."""
#     try:
#         stats = db.get_database_stats()
#         return jsonify(stats)
        
#     except Exception as e:
#         print(f"Error getting database stats: {e}")
#         return jsonify({"error": str(e)}), 500

# # Chatbot interaction loop
# @app.route('/chat', methods=['POST'])
# def chat():
#     print("Chat endpoint hit!")  # Debug print
    
#     # Log the incoming request details
#     print("Request method:", request.method)
#     print("Request content type:", request.content_type)
#     print("Request data:", request.get_json())

#     try:
#         # Explicitly parse JSON data
#         data = request.get_json()
#         if not data:
#             print("No JSON data received")
#             return jsonify({"error": "No data provided"}), 400

#         user_query = data.get('message', '')
#         print(f"Received query: {user_query}")

#         if not user_query:
#             return jsonify({"error": "Please enter a valid query."}), 400

#         # Load dataset
#         dataset = load_data('dataset1.json')
#         if dataset is None:
#             return jsonify({"error": "Dataset not found."}), 500

#         # Process query
#         response = process_user_query(user_query, dataset)
#         print(f"Generated response: {response}")

#         return jsonify({"response": response})

#     except Exception as e:
#         print(f"Error in chat endpoint: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# # Ensure CORS is configured correctly
# CORS(app, resources={r"/chat": {"origins": "*"}})

# # Run the chatbot
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5002
#             )



# #Eligibilty is fixed



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

# Process college search queries
def process_college_search(query):
    """Process queries asking to find/search colleges."""
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
    
    response = f"I found {len(colleges)} colleges matching your search:\n\n"
    
    for i, college in enumerate(colleges[:10], 1):
        response += f"{i}. {college['college_name']} ({college['college_code']})\n"
        if college.get('branches'):
            response += f"   Branches: {len(college['branches'])}\n"
        response += "\n"
    
    if len(colleges) > 10:
        response += f"... and {len(colleges) - 10} more colleges.\n\n"
    
    response += "You can ask me for specific details about any college by mentioning its name or code."
    return response

# Process cutoff queries
def process_cutoff_query(query, college_name=None, branch_name=None):
    """Process queries about cutoffs, ranks, and eligibility."""
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
    
    response = f"📊 **Cutoff Information for {best_match['college_name']}**\n\n"
    
    if college_details.get('branches'):
        response += f"**Total Branches:** {len(college_details['branches'])}\n\n"
        
        # Filter by branch if specified
        relevant_branches = college_details['branches']
        if branch_name:
            relevant_branches = [b for b in relevant_branches if branch_name.lower() in b['branch_name'].lower()]
            if relevant_branches:
                response += f"**Filtered by:** {branch_name}\n\n"
        
        for branch in relevant_branches[:5]:  # Show first 5 branches
            response += f"🔧 **{branch['branch_name']}**\n"
            response += f"   Status: {branch.get('status', 'Not specified')}\n"
            
            if branch.get('cutoff_data'):
                response += f"   **Cutoff Data:**\n"
                for cutoff in branch['cutoff_data'][:3]:  # Show first 3 cutoffs
                    response += f"     • Stage {cutoff['stage']} - {cutoff['category']}: Rank {cutoff['rank']} ({cutoff['percentage']:.2f}%)\n"
            else:
                response += f"   No cutoff data available\n"
            response += "\n"
    else:
        response += "No branch information available for this college."
    
    response += "\n💡 **Tip:** You can ask me about specific branches, stages, or categories for more detailed information."
    return response

# Process college info queries
def process_college_info_query(query, college_name=None):
    """Process queries asking for general college information."""
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
    
    response = f"🏫 **College Information: {best_match['college_name']}**\n\n"
    response += f"**College Code:** {best_match['college_code']}\n"
    
    if college_details.get('branches'):
        response += f"**Total Branches:** {len(college_details['branches'])}\n\n"
        response += "**Available Branches:**\n"
        
        for i, branch in enumerate(college_details['branches'][:8], 1):
            response += f"{i}. {branch['branch_name']}\n"
            if branch.get('status'):
                response += f"   Status: {branch['status']}\n"
            if branch.get('cutoff_data'):
                response += f"   Cutoff entries: {len(branch['cutoff_data'])}\n"
            response += "\n"
        
        if len(college_details['branches']) > 8:
            response += f"... and {len(college_details['branches']) - 8} more branches.\n\n"
    
    response += "💡 **Ask me about:**\n"
    response += "• Specific branch details\n"
    response += "• Cutoff information\n"
    response += "• Admission criteria\n"
    response += "• Comparison with other colleges"
    
    return response

# Llama 3 local integration
def query_llama_local(prompt, max_tokens=200):
    """Query Llama 3 local model using ollama."""
    try:
        # Try using ollama if available
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'deepseek-r1:1.5b',  # Adjust model name as needed
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
                ['ollama', 'run', 'deepseek-r1:1.5b', prompt],
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

# Enhanced main query processing function
def process_user_query_enhanced(user_query):
    """Enhanced main function that handles both college and general queries."""
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
    
    # For general queries, try Llama 3 local first
    print("Attempting to use Llama 3 local for general query...")
    
    # Create a context-aware prompt for Llama
    context_prompt = f"""You are a helpful AI assistant. Answer this question directly without thinking out loud: "{user_query}"

If this is about engineering colleges in Maharashtra, mention I can help with specific college information from our database of 1,393+ colleges.

Direct answer:"""

    llama_response = query_llama_local(context_prompt)
    
    if llama_response:
        print("Llama 3 local response generated successfully")
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
    
    # Final fallback
    return f"I understand you're asking about: {user_query}. I'm here to help! For college-specific questions, I can provide detailed information about 1,393+ colleges in Maharashtra. For general questions, I'm happy to assist as well."

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
    print("📍 Features:")
    print("   - College database integration (1,393+ colleges)")
    print("   - Cutoff and admission queries")
    print("   - Llama 3 local model integration")
    print("   - Cohere fallback")
    print("   - PDF parsing and storage")
    print("📍 Server will be available at: http://localhost:5002")
    print("📍 Chat endpoint: POST /chat")
    print("📍 Health check: GET /health")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
