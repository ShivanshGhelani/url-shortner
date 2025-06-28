from fastapi import APIRouter, HTTPException, Form, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime

from app.models.url_models import URLCreate, URLResponse, URLInfo, URLStats
from app.services.url_service import URLService
from app.core.dependencies import get_url_service

router = APIRouter()
url_service = get_url_service()

@router.post("/shorten", response_model=URLResponse)
async def shorten_url(
    long_url: str = Form(...),
    custom_alias: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    expiry_date: Optional[datetime] = Form(None),
    password: Optional[str] = Form(None)
):
    """API endpoint to shorten a URL"""
    result = url_service.shorten_url(
        long_url=long_url,
        custom_alias=custom_alias,
        description=description,
        expiry_date=expiry_date,
        password=password
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return URLResponse(**result)

@router.get("/info/{short_code}", response_model=URLInfo)
async def get_url_info(short_code: str):
    """Get information about a shortened URL"""
    result = url_service.get_url_info(short_code)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return URLInfo(**result)

@router.get("/expand/{short_code}")
async def expand_url(short_code: str, password: Optional[str] = Query(None)):
    """Expand a shortened URL"""
    result = url_service.expand_url(short_code, password)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.delete("/delete/{short_code}")
async def delete_url(short_code: str):
    """Delete a shortened URL"""
    result = url_service.delete_url(short_code)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/list")
async def list_urls(
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List all shortened URLs with pagination"""
    return url_service.list_urls(limit=limit, offset=offset)

@router.get("/stats", response_model=URLStats)
async def get_stats():
    """Get usage statistics"""
    return URLStats(**url_service.get_stats())

@router.get("/html/{short_code}")
async def get_html_code(short_code: str):
    """Generate HTML code snippet for a shortened URL"""
    result = url_service.generate_html_code(short_code)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.post("/bulk-shorten")
async def bulk_shorten_urls(urls: List[str]):
    """Bulk shorten multiple URLs"""
    results = []
    
    for url in urls:
        result = url_service.shorten_url(url)
        results.append(result)
    
    return {"results": results}
