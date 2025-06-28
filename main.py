from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
import os
from pathlib import Path

from app.routers import url_router, api_router
from app.core.config import settings
from app.core.dependencies import get_url_service

# Initialize FastAPI app
app = FastAPI(
    title="Universal URL Shortener",
    description="A comprehensive URL shortening service supporting all types of URLs",
    version="1.0.0"
)

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")

# Get shared URL service
url_service = get_url_service()

# Include routers
app.include_router(url_router.router)
app.include_router(api_router.router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with URL shortening interface"""
    recent_urls = url_service.get_recent_urls(limit=10)
    stats = url_service.get_stats()
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "recent_urls": recent_urls,
            "stats": stats
        }
    )

@app.get("/{short_code}")
async def redirect_url(request: Request, short_code: str, password: str = None):
    """Redirect to original URL"""
    print(f"🔍 Looking for short_code: '{short_code}'")
    print(f"📁 Available codes: {list(url_service.urls.keys())}")
    print(f"💾 Storage file: {url_service.storage_file}")
    
    # First check if URL exists and if it needs password
    url_info = url_service.get_url_info(short_code)
    if "error" in url_info:
        print(f"❌ Error: {url_info['error']}")
        raise HTTPException(status_code=404, detail="URL not found")
    
    # If URL requires password but none provided, show password form
    if url_info.get("has_password") and not password:
        print(f"🔒 Password required for '{short_code}', showing password form")
        return templates.TemplateResponse(
            "password_form.html",
            {"request": request, "short_code": short_code}
        )
    
    # Try to expand URL with password (if provided)
    result = url_service.expand_url(short_code, password)
    
    if "error" in result:
        if result["error"] == "Invalid password":
            print(f"🔒 Invalid password for '{short_code}'")
            return templates.TemplateResponse(
                "password_form.html",
                {"request": request, "short_code": short_code, "error": "Invalid password"}
            )
        else:
            print(f"❌ Error: {result['error']}")
            raise HTTPException(status_code=404, detail="URL not found")
    
    print(f"✅ Redirecting to: {result['long_url']}")
    return RedirectResponse(url=result["long_url"], status_code=302)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Universal URL Shortener started!")
    print(f"📊 Dashboard: http://{settings.HOST}:{settings.PORT}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
