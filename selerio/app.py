from flask import Flask, request, jsonify, render_template
import json
import os
import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv, dotenv_values 

class Disease(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]

# Load API key
load_dotenv()
config = dotenv_values(".env")

# Configure generative AI
genai.configure(api_key=config['GEMINI_API_KEY'])

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Get the directory where the script is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "diseases.json")

# Load the disease data from the JSON file
try:
    with open(JSON_FILE, "r") as file:
        diseases = json.load(file)
except FileNotFoundError:
    diseases = []  # If file is missing, start with an empty list


@app.route('/')
def home():
    return render_template('index.html', diseases=diseases)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    results = []

    for d in diseases:
        # Check if the query matches primary name, synonyms, or ICD codes
        if (query in d['primary_name'].lower() or
            any(query in syn.lower() for syn in d.get('synonyms', [])) or
            any(query in code['code'].lower() for code in d.get('icd10cm', []))):
            results.append(d)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)