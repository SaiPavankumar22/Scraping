from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

URL = "https://www.bankbazaar.com/gold-rate-india.html"

def scrape_gold_rates():
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find("table", class_="w-full caption-bottom text-sm border")
    rows = table.find("tbody").find_all("tr")

    gold_rates = []
    for row in rows:
        cols = row.find_all("td")
        city = cols[0].text.strip()
        gold_22k = cols[1].text.strip()
        gold_24k = cols[2].text.strip()

        gold_rates.append({
            "city": city,
            "gold_22k": gold_22k,
            "gold_24k": gold_24k
        })

    return gold_rates

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_gold_rates')
def get_gold_rates():
    data = scrape_gold_rates()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
