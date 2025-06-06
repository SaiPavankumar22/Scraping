from flask import Flask, jsonify, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/fetch-mf-data', methods=['GET'])
def fetch_mf_data():
    url = "URL_OF_ET_MONEY_PAGE"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all elements from 'mfExplore-body' class
    elements = soup.find_all(class_="mfExplore-body")
    data = []

    for element in elements:
        # Remove unwanted sections
        for excluded in element.find_all(class_="trust-builder-wrapper tb-sidebar-section trust-builder-left loadAnimation"):
            excluded.extract()
        
        # Append cleaned text to list
        data.append(element.get_text(strip=True, separator="\n"))
    
    return jsonify({"data": data})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
