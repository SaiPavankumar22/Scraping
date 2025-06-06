import csv
import io
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

scraped_tenders = []

@app.get("/")
async def home(request: Request):
    # Just show empty page initially
    return templates.TemplateResponse("index.html", {"request": request, "tenders": [], "error": None})

@app.get("/scrape")
async def scrape(request: Request):
    global scraped_tenders
    url = "https://etender.cpwd.gov.in/TenderswithinOneday.html"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_grdTenderswithinOneday")))

        tenders = []
        rows = driver.find_elements(By.CSS_SELECTOR, "#ContentPlaceHolder1_grdTenderswithinOneday tbody tr")
        for row in rows[:20]:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 5:
                tender = {
                    "tender_no": cols[0].text.strip(),
                    "description": cols[1].text.strip(),
                    "date": cols[2].text.strip(),
                    "closing_date": cols[3].text.strip(),
                    "status": cols[4].text.strip()
                }
                tenders.append(tender)

        scraped_tenders = tenders
        return templates.TemplateResponse("index.html", {"request": request, "tenders": tenders, "error": None})

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "tenders": [], "error": f"Scraping failed: {str(e)}"})

    finally:
        if driver:
            driver.quit()

@app.get("/download")
async def download_csv():
    global scraped_tenders

    if not scraped_tenders:
        return StreamingResponse(iter(["No data available. Please scrape first."]), media_type="text/plain")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["tender_no", "description", "date", "closing_date", "status"])
    writer.writeheader()
    for tender in scraped_tenders:
        writer.writerow(tender)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tenders.csv"},
    )
