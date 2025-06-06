from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_post_office_policies():
    url = "https://www.indiapost.gov.in/Financial/pages/content/post-office-saving-schemes.aspx"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to fetch policies"}

    soup = BeautifulSoup(response.text, "html.parser")
    policies = []

    for item in soup.find_all("li", class_="li_header"):
        title_tag = item.find("a")
        content_tag = item.find("div", class_="li_content")

        if title_tag and content_tag:
            title = title_tag.text.strip()
            content = content_tag.encode_contents().decode()  # Get full HTML content
            policies.append({"title": title, "content": content})

    return policies

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/policies", methods=["GET"])
def policies():
    return jsonify(get_post_office_policies())

if __name__ == "__main__":
    app.run(debug=True)
