#!/usr/bin/env python3
"""
Test script to verify deployment readiness
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test vercel_app.py imports
        print("  Testing vercel_app.py imports...")
        from app.routers.url_router import router as url_router
        from app.routers.api_router import router as api_router
        from app.core.config import settings
        from app.core.dependencies import get_url_service
        print("  ✅ vercel_app.py imports successful")
        
        # Test main.py imports
        print("  Testing main.py imports...")
        import main
        print("  ✅ main.py imports successful")
        
        # Test vercel_app.py directly
        print("  Testing vercel_app.py directly...")
        import vercel_app
        print("  ✅ vercel_app.py direct import successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"  HOST: {settings.HOST}")
        print(f"  PORT: {settings.PORT}")
        print(f"  BASE_URL: {settings.BASE_URL}")
        print(f"  STORAGE_FILE: {settings.STORAGE_FILE}")
        print(f"  VERSION: {settings.VERSION}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_service():
    """Test URL service initialization"""
    print("🛠️ Testing URL service...")
    
    try:
        from app.core.dependencies import get_url_service
        
        service = get_url_service()
        print(f"  Service initialized: {type(service)}")
        print(f"  Storage file: {service.storage_file}")
        print(f"  Base URL: {service.base_url}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service error: {e}")
        return False

def test_routers():
    """Test router initialization"""
    print("🛣️ Testing routers...")
    
    try:
        from app.routers.url_router import router as url_router
        from app.routers.api_router import router as api_router
        
        print(f"  URL router routes: {len(url_router.routes)}")
        print(f"  API router routes: {len(api_router.routes)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Router error: {e}")
        return False

def test_vercel_app():
    """Test vercel_app.py specifically"""
    print("🚀 Testing vercel_app.py...")
    
    try:
        from vercel_app import app, handler
        
        print(f"  App type: {type(app)}")
        print(f"  Handler type: {type(handler)}")
        print(f"  App routes: {len(app.routes)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ vercel_app.py error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting deployment tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_service,
        test_routers,
        test_vercel_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed! Deployment should work.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 