from fastapi import APIRouter, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime
from pathlib import Path

from ..services.url_service import URLService
from app.core.dependencies import get_url_service

router = APIRouter()
url_service = get_url_service()

# Initialize templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, page: int = Query(1, ge=1)):
    """Dashboard page with URL management"""
    limit = 20
    offset = (page - 1) * limit
    
    urls_data = url_service.list_urls(limit=limit, offset=offset)
    stats = url_service.get_stats()
    
    total_pages = (urls_data["total"] + limit - 1) // limit
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "urls": urls_data["urls"],
            "stats": stats,
            "page": page,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
    )

@router.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    """Analytics page"""
    stats = url_service.get_stats()
    recent_urls = url_service.get_recent_urls(limit=20)
    
    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "stats": stats,
            "recent_urls": recent_urls
        }
    )

@router.get("/bulk", response_class=HTMLResponse)
async def bulk_shortener(request: Request):
    """Bulk URL shortening page"""
    return templates.TemplateResponse(
        "bulk.html",
        {"request": request}
    )

@router.post("/shorten-form")
async def shorten_url_form(
    request: Request,
    long_url: str = Form(...),
    custom_alias: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    """Handle form submission for URL shortening"""
    
    # Debug: Print raw form data
    print(f"🐛 Raw form data received:")
    print(f"  - long_url: '{long_url}' (type: {type(long_url)})")
    print(f"  - custom_alias: '{custom_alias}' (type: {type(custom_alias)})")
    print(f"  - description: '{description}' (type: {type(description)})")
    print(f"  - password: '{password}' (type: {type(password)})")
    
    # Clean up form data
    if custom_alias and not custom_alias.strip():
        custom_alias = None
    if description and not description.strip():
        description = None
    if password and not password.strip():
        password = None
    
    # Debug: Print cleaned form data
    print(f"🧹 Cleaned form data:")
    print(f"  - long_url: '{long_url}'")
    print(f"  - custom_alias: '{custom_alias}'")
    print(f"  - description: '{description}'")
    print(f"  - password: '{password}'")
    
    result = url_service.shorten_url(
        long_url=long_url,
        custom_alias=custom_alias,
        description=description,
        password=password
    )
    
    print(f"🔨 URL Creation Result: {result}")
    print(f"📁 Current URLs in storage: {list(url_service.urls.keys())}")
    print(f"💾 Storage file path: {url_service.storage_file}")
    
    if "error" in result:
        # Return to home page with error
        recent_urls = url_service.get_recent_urls(limit=10)
        stats = url_service.get_stats()
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "recent_urls": recent_urls,
                "stats": stats,
                "error": result["error"],
                "form_data": {
                    "long_url": long_url,
                    "custom_alias": custom_alias,
                    "description": description
                }
            }
        )
    
    # Success - redirect to result page
    return RedirectResponse(
        url=f"/result/{result['short_code']}",
        status_code=303
    )

@router.get("/result/{short_code}", response_class=HTMLResponse)
async def show_result(request: Request, short_code: str):
    """Show result page after URL shortening"""
    url_info = url_service.get_url_info(short_code)
    
    if "error" in url_info:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Generate QR code and HTML snippet
    qr_code = url_service.generate_qr_code(f"{url_service.base_url}/{short_code}")
    html_result = url_service.generate_html_code(short_code)
    
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "url_info": url_info,
            "short_url": f"{url_service.base_url}/{short_code}",
            "qr_code": qr_code,
            "html_code": html_result.get("html", "")
        }
    )

@router.get("/info/{short_code}", response_class=HTMLResponse)
async def url_info_page(request: Request, short_code: str):
    """Detailed information page for a URL"""
    url_info = url_service.get_url_info(short_code)
    
    if "error" in url_info:
        raise HTTPException(status_code=404, detail="URL not found")
    
    qr_code = url_service.generate_qr_code(f"{url_service.base_url}/{short_code}")
    html_result = url_service.generate_html_code(short_code)
    
    return templates.TemplateResponse(
        "url_info.html",
        {
            "request": request,
            "url_info": url_info,
            "short_url": f"{url_service.base_url}/{short_code}",
            "qr_code": qr_code,
            "html_code": html_result.get("html", "")
        }
    )

@router.post("/delete/{short_code}")
async def delete_url_form(short_code: str):
    """Delete URL via form submission"""
    result = url_service.delete_url(short_code)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return RedirectResponse(url="/dashboard", status_code=303)
