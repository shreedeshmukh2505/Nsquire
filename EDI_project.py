import re
import json
from fuzzywuzzy import process, fuzz
from typing import Dict, List
import cohere
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Cohere API setup
cohere_api_key = 'TsY1cWlAAL00usoIgNEeHLxkiYO9vzSSwzZQKppW'  # Replace with your actual API key
co = cohere.Client(cohere_api_key)


# Load dataset
def load_data(file_path='dataset1.json'):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None

# Cohere-based intent and entity extraction
def cohere_understand_query(user_query):
    prompt = (
        f"Extract the following details from the user's query: '{user_query}'\n"
        "Provide the response in the following format:\n"
        "Intent: [cutoff/fees/package/info]\n"
        "College: [the college name, if mentioned, otherwise 'None']\n"
        "Year: [the year if provided, otherwise 'None']"
    )
    response = co.generate(
        model="command-xlarge-nightly",
        prompt=prompt,
        max_tokens=50,
        temperature=0.5
    )
    return response.generations[0].text.strip()

# Parse Cohere response
def parse_cohere_response(ai_response):
    entities = {'intent': None, 'college_name': None, 'year': None}
    lines = ai_response.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if 'intent' in key and value.lower() != 'none':
                entities['intent'] = value
            elif 'college' in key and value.lower() != 'none':
                entities['college_name'] = value
            elif 'year' in key and value.lower() != 'none':
                entities['year'] = value
    return entities

# Detect language (English vs Hinglish)
def detect_language(sentence):
    hinglish_keywords = ["kya", "ka", "hai", "kyunki", "aur", "kaise", "ki", "ke"]
    for word in hinglish_keywords:
        if word in sentence.lower():
            return "hinglish"
    return "english"

# Fuzzy matching to ensure college name detection
def match_college_name(college_name, dataset):
    if not college_name:
        return None

    # Attempt exact match first
    college_data = next((college for college in dataset if college['name'].lower() == college_name.lower()), None)
    if college_data:
        return college_data

    # Use fuzzy matching as a fallback
    college_names = [college['name'] for college in dataset]
    best_match, score = process.extractOne(college_name, college_names, scorer=fuzz.token_set_ratio)
    if score > 75:  # Match threshold
        return next((college for college in dataset if college['name'] == best_match), None)

    return None

# Response generation based on intent and language
def generate_dynamic_response(intent, college_data, language='english', year=None):
    if not college_data:
        if language == 'hinglish':
            return "Maaf kijiye, mujhe college ke baare mein jaankari nahi mili."
        else:
            return "Sorry, I couldn't find information about the college."

    if intent == 'cutoff':
        year = year if year else '2023'  # Default year is 2023
        cutoff = college_data['admission']['cutoff'].get(year, 'N/A')
        if language == 'hinglish':
            return f"{college_data['name']} ka {year} ka cutoff {cutoff} hai."
        else:
            return f"The cutoff for {college_data['name']} in {year} is {cutoff}."

    elif intent == 'fees':
        fees_info = "\n".join([f"{course['name']}: ₹{course['annual_fee']:,}/year" for course in college_data['courses']])
        if language == 'hinglish':
            return f"{college_data['name']} ki fees:\n{fees_info}"
        else:
            return f"The fees for {college_data['name']} are:\n{fees_info}"

    elif intent == 'package':
        avg_package = college_data['placements']['average_package']
        highest_package = college_data['placements']['highest_package']
        if language == 'hinglish':
            return f"{college_data['name']} ka average package ₹{avg_package:,}/saal aur highest package ₹{highest_package:,}/saal hai."
        else:
            return f"The average package for {college_data['name']} is ₹{avg_package:,}/year, and the highest package is ₹{highest_package:,}/year."

    elif intent == 'info':
        location = college_data['location']
        rating = college_data['rating']
        facilities = ", ".join(college_data['facilities'])
        if language == 'hinglish':
            return (f"{college_data['name']} ki location {location} hai aur rating {rating}/5 hai. Facilities mein shamil hain: {facilities}.")
        else:
            return (f"{college_data['name']} is located in {location}, has a rating of {rating}/5. Facilities include: {facilities}.")

    return "Sorry, I couldn't understand your query."

def process_user_query(user_query, dataset):
    detected_language = detect_language(user_query)

    # Step 1: Extract intent and entities using Cohere
    ai_response = cohere_understand_query(user_query)
    parsed_data = parse_cohere_response(ai_response)

    intent = parsed_data['intent']
    college_name = parsed_data['college_name']
    year = parsed_data['year']

    # Step 2: Match college name using fuzzy matching
    college_data = match_college_name(college_name, dataset)

    # Step 3: Generate response
    return generate_dynamic_response(intent, college_data, language=detected_language, year=year)


# Flask API endpoint
@app.route('/chat', methods=['POST'])
def chat():
    dataset = load_data('dataset1.json')
    if dataset is None:
        return jsonify({"error": "Dataset not found."}), 500

    user_query = request.json.get('message', '')
    if not user_query:
        return jsonify({"response": "Please enter a valid query."}), 400

    response = process_user_query(user_query, dataset)
    print(f"User Query: {user_query}")  # Log the user query
    print(f"Bot Response: {response}")  # Log the chatbot's response
    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True,port=5001)
