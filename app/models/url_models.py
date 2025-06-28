from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class URLCreate(BaseModel):
    long_url: str
    custom_alias: Optional[str] = None
    description: Optional[str] = None
    expiry_date: Optional[datetime] = None
    password: Optional[str] = None

class URLResponse(BaseModel):
    success: bool
    short_url: Optional[str] = None
    short_code: Optional[str] = None
    long_url: Optional[str] = None
    description: Optional[str] = None
    file_type: Optional[str] = None
    created_at: Optional[str] = None
    clicks: Optional[int] = None
    error: Optional[str] = None
    qr_code: Optional[str] = None

class URLInfo(BaseModel):
    short_code: str
    long_url: str
    description: Optional[str] = None
    file_type: str
    created_at: str
    clicks: int
    is_supabase: bool
    expiry_date: Optional[str] = None
    has_password: bool = False

class URLStats(BaseModel):
    total_urls: int
    total_clicks: int
    recent_urls: int
    active_urls: int
