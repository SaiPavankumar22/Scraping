from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

URL = "https://www.etmoney.com/mutual-funds/featured"


@app.route("/")
def index():
    return render_template("index.html")
@app.route("/get-mutual-funds", methods=["GET"])
def scrape_et_money():
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve data"}), 500
    
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("div", class_="feature-category-item-list")
    
    funds = []
    for item in items:
        for fund in item.find_all("div", class_="item"):
            title = fund.find("h4", class_="h4").text.strip()
            image = fund.find("img")["src"]
            link = "https://www.etmoney.com" + fund.find("a")["href"]
            funds.append({"title": title, "image": image, "link": link})
    
    return jsonify(funds)

if __name__ == "__main__":
    app.run(debug=True)
