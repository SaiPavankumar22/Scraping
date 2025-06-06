from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_lic_policies():
    url = "https://licindia.in/insurance-plan"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to fetch LIC policies"}

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Categories to scrape
    target_categories = {"Endowment Plans", "Money Back Plans"}
    policy_categories = {}

    # Find all accordion items which represent categories
    for accordion_item in soup.find_all("div", class_="accordion-item"):
        category_button = accordion_item.find("button", class_="accordion-button")
        if not category_button:
            continue
        
        category_name = category_button.text.strip()
        
        if category_name in target_categories:
            policies = []
            table = accordion_item.find("table", class_="table")
            if table:
                for row in table.find("tbody").find_all("tr"):
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        link_tag = cols[1].find("a")
                        if link_tag:
                            title = link_tag.text.strip()
                            link = link_tag["href"]
                            if not link.startswith("http"):
                                link = "https://licindia.in" + link
                            policies.append({"title": title, "link": link})
            
            policy_categories[category_name] = policies

    return policy_categories

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lic_policies", methods=["GET"])
def lic_policies():
    policies = get_lic_policies()
    return jsonify(policies)

if __name__ == "__main__":
    app.run(debug=True)
