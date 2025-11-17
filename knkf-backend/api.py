"""
FastAPI Backend for KNKF Scraper
Production-ready API that can be deployed separately
"""

from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime, timedelta
import asyncio

# Import your existing scraper
import sys
sys.path.append(os.path.dirname(__file__))
from scraper import KNKFScraper

app = FastAPI(title="KNKF Competition Scraper API")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
last_scrape_time = None
RATE_LIMIT_SECONDS = 300 # 5 minutes

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    count: Optional[int] = None
    error: Optional[str] = None

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key if configured"""
    expected_key = os.getenv("API_KEY")
    if expected_key and x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

async def run_scraper():
    """Background task to run the scraper"""
    global last_scrape_time
    
    try:
        import subprocess
        import re
        result = subprocess.run([
            sys.executable, os.path.join(os.path.dirname(__file__), "main.py")
        ], capture_output=True, text=True)
        last_scrape_time = datetime.now()
        if result.returncode == 0:
            stdout = result.stdout
            # Parse for count
            count_match = re.search(r"Total competitions found: (\\d+)", stdout)
            db_count_match = re.search(r"Saved to database: (\\d+)/(\\d+)", stdout)
            count = int(db_count_match.group(1)) if db_count_match else (
                int(count_match.group(1)) if count_match else 0
            )
            return {"success": True, "count": count, "message": stdout}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "KNKF Scraper API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/api/scrape", response_model=ScrapeResponse)
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    authorized: bool = Depends(verify_api_key)
):
    """
    Trigger the KNKF scraper
    
    - Requires API key if configured via API_KEY env var
    - Rate limited to once per minute
    - Runs scraping in background
    """
    global last_scrape_time
    
    # Rate limiting
    if last_scrape_time:
        time_since_last = (datetime.now() - last_scrape_time).total_seconds()
        if time_since_last < RATE_LIMIT_SECONDS:
            wait_time = int(RATE_LIMIT_SECONDS - time_since_last)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit: Please wait {wait_time} seconds before scraping again"
            )
    
    # Run scraper
    result = await run_scraper()
    if result["success"]:
        return ScrapeResponse(
            success=True,
            message=f"Successfully scraped and saved {result['count']} competitions" if result["count"] is not None else "Scrape completed.",
            count=result["count"]
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Unknown error occurred")
        )

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "last_scrape": last_scrape_time.isoformat() if last_scrape_time else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
