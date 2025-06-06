from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from datetime import datetime
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Column mapping as specified
csv_cols = {
    "NIT/RFP NO": "ref_no",
    "Name of Work / Subwork / Packages": "title",
    "Estimated Cost": "tender_value",
    "Bid Submission Closing Date & Time": "bid_submission_end_date",  
    "EMD Amount": "emd",
    "Bid Opening Date & Time": "bid_open_date"
}

def clean_currency(text):
    """Remove currency symbols and clean numeric values"""
    if not text:
        return ""
    # Remove ₹ symbol and extra spaces
    cleaned = re.sub(r'[₹,\s]', '', text.strip())
    return cleaned

def scrape_tenders():
    """Scrape tender data from CPWD website"""
    url = "https://etender.cpwd.gov.in/TenderswithinOneday.html#"
    
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table with tender data
        table = soup.find('table', {'id': 'awardedDataTable'})
        
        if not table:
            return []
        
        tenders = []
        tbody = table.find('tbody')
        
        if tbody:
            rows = tbody.find_all('tr')[:20]  # Get first 20 tenders
            
            for row in rows:
                cells = row.find_all('td')
                
                if len(cells) >= 8:  # Ensure we have enough columns
                    tender_data = {
                        "NIT/RFP NO": cells[1].get_text(strip=True),
                        "Name of Work / Subwork / Packages": cells[2].get_text(strip=True),
                        "Estimated Cost": clean_currency(cells[4].get_text(strip=True)),
                        "Bid Submission Closing Date & Time": cells[6].get_text(strip=True),
                        "EMD Amount": clean_currency(cells[5].get_text(strip=True)),
                        "Bid Opening Date & Time": cells[7].get_text(strip=True)
                    }
                    tenders.append(tender_data)
        
        return tenders
        
    except Exception as e:
        print(f"Error scraping data: {str(e)}")
        return []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/scrape")
async def scrape_data():
    """API endpoint to scrape tender data"""
    tenders = scrape_tenders()
    return {"success": True, "data": tenders, "count": len(tenders)}

@app.get("/download")
async def download_csv():
    """Generate and download CSV file"""
    tenders = scrape_tenders()
    
    if not tenders:
        return {"success": False, "message": "No data found"}
    
    # Convert to DataFrame
    df = pd.DataFrame(tenders)
    
    # Rename columns according to the mapping
    df = df.rename(columns=csv_cols)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cpwd_tenders_{timestamp}.csv"
    filepath = f"downloads/{filename}"
    
    # Create downloads directory if it doesn't exist
    os.makedirs("downloads", exist_ok=True)
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='text/csv'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)