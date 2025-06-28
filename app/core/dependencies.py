"""
Dependency injection for shared services
"""
from app.services.url_service import URLService

# Global shared URL service instance
_url_service = None

def get_url_service() -> URLService:
    """Get the shared URL service instance"""
    global _url_service
    if _url_service is None:
        _url_service = URLService()
    return _url_service
