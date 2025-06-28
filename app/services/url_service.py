import json
import os
import random
import string
import re
import hashlib
import base64
import io
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import Optional, List, Dict, Any
import validators
import qrcode
from qrcode.image.styledpil import StyledPilImage

from app.core.config import settings

class URLService:
    def __init__(self, storage_file: str = None):
        self.storage_file = storage_file or settings.STORAGE_FILE
        self.base_url = settings.BASE_URL
        self.urls = self.load_urls()
    
    def load_urls(self) -> Dict[str, Any]:
        """Load URLs from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading URLs: {e}")
                return {}
        return {}
    
    def save_urls(self) -> None:
        """Save URLs to storage file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.urls, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving URLs: {e}")
    
    def is_valid_url(self, url: str) -> bool:
        """Validate if URL is properly formatted"""
        return validators.url(url) is True
    
    def is_supabase_url(self, url: str) -> bool:
        """Check if URL is from Supabase storage"""
        return 'supabase.co/storage/v1/object/public' in url
    
    def get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "unknown"
    
    def extract_filename(self, url: str) -> Optional[str]:
        """Extract filename from URL for smart alias generation"""
        try:
            # Remove trailing characters
            url = url.rstrip('|').rstrip('/')
            
            # Get the last part after the last /
            path = urlparse(url).path
            filename = path.split('/')[-1]
            
            if not filename:
                return None
            
            # Remove file extension and clean up
            name_part = filename.split('.')[0]
            
            # Remove timestamp-like numbers and clean
            clean_name = re.sub(r'[_-]\d{10,}', '', name_part)
            clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', clean_name)
            
            # Replace underscores with hyphens and make lowercase
            clean_name = clean_name.replace('_', '-').lower()
            
            return clean_name if clean_name else None
        except:
            return None
    
    def generate_smart_alias(self, url: str) -> str:
        """Generate a smart alias based on the URL"""
        # Try to extract filename first
        base_alias = self.extract_filename(url)
        
        if not base_alias:
            # If no filename, try to use domain
            domain = self.get_domain(url)
            if domain and domain != "unknown":
                base_alias = domain.replace('.', '-').replace('www-', '')
            else:
                return self.generate_short_code()
        
        # Ensure alias is reasonable length
        if len(base_alias) > 20:
            base_alias = base_alias[:20]
        
        # If the base alias is available, use it
        if base_alias not in self.urls:
            return base_alias
        
        # If taken, add a number
        counter = 1
        while f"{base_alias}-{counter}" in self.urls:
            counter += 1
        
        return f"{base_alias}-{counter}"
    
    def generate_short_code(self, length: int = None) -> str:
        """Generate a random short code"""
        length = length or settings.SHORT_CODE_LENGTH
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def is_valid_alias(self, alias: str) -> bool:
        """Check if alias contains only valid characters"""
        return re.match('^[a-zA-Z0-9_-]+$', alias) is not None
    
    def hash_password(self, password: str) -> str:
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    def get_file_type(self, url: str) -> str:
        """Extract file type from URL"""
        try:
            # Get the path from URL
            parsed_url = urlparse(url)
            path = parsed_url.path.lower()
            
            # Extract extension
            extension = path.split('.')[-1] if '.' in path else ''
            
            # Categorize by extension
            if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico']:
                return 'image'
            elif extension in ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt']:
                return 'document'
            elif extension in ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv']:
                return 'video'
            elif extension in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
                return 'audio'
            elif extension in ['zip', 'rar', '7z', 'tar', 'gz']:
                return 'archive'
            elif extension in ['exe', 'msi', 'dmg', 'pkg', 'deb', 'rpm']:
                return 'software'
            elif extension in ['html', 'htm', 'php', 'asp', 'jsp']:
                return 'webpage'
            else:
                # Check by domain patterns
                domain = self.get_domain(url)
                if any(x in domain for x in ['youtube.com', 'vimeo.com', 'dailymotion.com']):
                    return 'video'
                elif any(x in domain for x in ['soundcloud.com', 'spotify.com']):
                    return 'audio'
                elif any(x in domain for x in ['github.com', 'gitlab.com', 'bitbucket.org']):
                    return 'code'
                else:
                    return 'link'
        except:
            return 'link'
    
    def generate_qr_code(self, url: str) -> str:
        """Generate QR code for URL and return as base64 string"""
        if not settings.ENABLE_QR_CODES:
            return None
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None
    
    def shorten_url(self, long_url: str, custom_alias: str = None, 
                   description: str = None, expiry_date: datetime = None, 
                   password: str = None) -> Dict[str, Any]:
        """
        Shorten a URL with enhanced features
        
        Args:
            long_url (str): The URL to shorten
            custom_alias (str): Custom alias for the short URL
            description (str): Optional description for the URL
            expiry_date (datetime): Optional expiry date
            password (str): Optional password protection
        
        Returns:
            dict: Result containing short URL and details
        """
        
        # Clean the URL
        long_url = long_url.strip()
        
        # Validate URL
        if not self.is_valid_url(long_url):
            return {"error": "Please provide a valid URL"}
        
        # Handle custom alias
        if custom_alias:
            custom_alias = custom_alias.strip()
            if not self.is_valid_alias(custom_alias):
                return {"error": "Custom alias can only contain letters, numbers, hyphens, and underscores"}
            
            if custom_alias in self.urls:
                return {"error": f"Custom alias '{custom_alias}' is already taken"}
            
            short_code = custom_alias
        else:
            # Generate smart alias
            short_code = self.generate_smart_alias(long_url)
        
        # Create URL record
        url_record = {
            "long_url": long_url,
            "short_code": short_code,
            "created_at": datetime.now().isoformat(),
            "description": description or self.extract_filename(long_url) or "Link",
            "clicks": 0,
            "is_supabase": self.is_supabase_url(long_url),
            "file_type": self.get_file_type(long_url),
            "domain": self.get_domain(long_url),
            "expiry_date": expiry_date.isoformat() if expiry_date else None,
            "password_hash": self.hash_password(password) if password else None,
            "last_accessed": None
        }
        
        # Debug: Print URL record being stored
        print(f"🗃️ Storing URL record:")
        print(f"  - password provided: '{password}' (type: {type(password)})")
        print(f"  - password_hash created: {url_record['password_hash']}")
        
        # Store the URL
        self.urls[short_code] = url_record
        self.save_urls()
        
        short_url = f"{self.base_url}/{short_code}"
        qr_code = self.generate_qr_code(short_url)
        
        return {
            "success": True,
            "short_url": short_url,
            "short_code": short_code,
            "long_url": long_url,
            "created_at": url_record["created_at"],
            "description": url_record["description"],
            "file_type": url_record["file_type"],
            "domain": url_record["domain"],
            "qr_code": qr_code
        }
    
    def get_url_info(self, short_code: str) -> Dict[str, Any]:
        """Get information about a shortened URL"""
        if short_code not in self.urls:
            return {"error": "Short URL not found"}
        
        url_record = self.urls[short_code]
        
        # Check if URL has expired
        if url_record.get("expiry_date"):
            expiry = datetime.fromisoformat(url_record["expiry_date"])
            if datetime.now() > expiry:
                return {"error": "Short URL has expired"}
        
        return {
            "success": True,
            "long_url": url_record["long_url"],
            "short_code": short_code,
            "created_at": url_record["created_at"],
            "description": url_record.get("description"),
            "clicks": url_record.get("clicks", 0),
            "file_type": url_record.get("file_type", "link"),
            "domain": url_record.get("domain", "unknown"),
            "expiry_date": url_record.get("expiry_date"),
            "has_password": bool(url_record.get("password_hash")),
            "last_accessed": url_record.get("last_accessed")
        }
    
    def expand_url(self, short_code: str, password: str = None) -> Dict[str, Any]:
        """Expand a short URL and increment click counter"""
        url_info = self.get_url_info(short_code)
        
        if "error" in url_info:
            return url_info
        
        # Check password if required
        if self.urls[short_code].get("password_hash"):
            if not password:
                return {"error": "Password required"}
            
            if not self.verify_password(password, self.urls[short_code]["password_hash"]):
                return {"error": "Invalid password"}
        
        # Increment click counter and update last accessed
        self.urls[short_code]["clicks"] += 1
        self.urls[short_code]["last_accessed"] = datetime.now().isoformat()
        self.save_urls()
        
        return {
            "success": True,
            "long_url": url_info["long_url"],
            "file_type": url_info["file_type"]
        }
    
    def delete_url(self, short_code: str) -> Dict[str, Any]:
        """Delete a shortened URL"""
        if short_code not in self.urls:
            return {"error": "Short URL not found"}
        
        del self.urls[short_code]
        self.save_urls()
        
        return {"success": True, "message": "URL deleted successfully"}
    
    def list_urls(self, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """List all shortened URLs with pagination"""
        if not self.urls:
            return {"urls": [], "total": 0}
        
        url_list = []
        for short_code, record in self.urls.items():
            url_list.append({
                "short_url": f"{self.base_url}/{short_code}",
                "short_code": short_code,
                "long_url": record["long_url"],
                "created_at": record["created_at"],
                "clicks": record.get("clicks", 0),
                "description": record.get("description", ""),
                "file_type": record.get("file_type", "link"),
                "domain": record.get("domain", "unknown"),
                "has_password": bool(record.get("password_hash")),
                "expiry_date": record.get("expiry_date"),
                "last_accessed": record.get("last_accessed")
            })
        
        # Sort by creation date (newest first)
        url_list.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        total = len(url_list)
        if limit:
            url_list = url_list[offset:offset + limit]
        
        return {"urls": url_list, "total": total}
    
    def get_recent_urls(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently created URLs"""
        result = self.list_urls(limit=limit)
        return result["urls"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total_urls = len(self.urls)
        total_clicks = sum(record.get("clicks", 0) for record in self.urls.values())
        
        # Count recent URLs (last 7 days)
        recent_count = 0
        week_ago = datetime.now() - timedelta(days=7)
        
        active_count = 0
        for record in self.urls.values():
            created_at = datetime.fromisoformat(record["created_at"])
            if created_at > week_ago:
                recent_count += 1
            
            # Check if URL is active (not expired)
            if record.get("expiry_date"):
                expiry = datetime.fromisoformat(record["expiry_date"])
                if datetime.now() <= expiry:
                    active_count += 1
            else:
                active_count += 1
        
        return {
            "total_urls": total_urls,
            "total_clicks": total_clicks,
            "recent_urls": recent_count,
            "active_urls": active_count
        }
    
    def generate_html_code(self, short_code: str) -> Dict[str, Any]:
        """Generate HTML code snippet for easy web integration"""
        url_info = self.get_url_info(short_code)
        if "error" in url_info:
            return url_info
        
        short_url = f"{self.base_url}/{short_code}"
        file_type = url_info.get("file_type", "link")
        description = url_info.get("description", "Link")
        
        if file_type == "image":
            html = f'<img src="{short_url}" alt="{description}" />'
        elif file_type == "video":
            html = f'<video controls><source src="{short_url}" /></video>'
        else:
            html = f'<a href="{short_url}" target="_blank">{description}</a>'
        
        return {
            "success": True,
            "html": html,
            "short_url": short_url,
            "file_type": file_type
        }
