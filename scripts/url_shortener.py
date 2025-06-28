#!/usr/bin/env python3
"""
URL Shortener with Customization
A simple Python script to shorten long URLs with custom aliases and expiration options.
"""

import hashlib
import random
import string
import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re

class URLShortener:
    def __init__(self, base_url="https://short.ly", storage_file="urls.json"):
        self.base_url = base_url.rstrip('/')
        self.storage_file = storage_file
        self.urls = self.load_urls()
    
    def load_urls(self):
        """Load URLs from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_urls(self):
        """Save URLs to storage file"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.urls, f, indent=2)
    
    def is_valid_url(self, url):
        """Validate if the URL is properly formatted"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def generate_short_code(self, length=6):
        """Generate a random short code"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def is_valid_alias(self, alias):
        """Check if alias contains only valid characters"""
        return re.match('^[a-zA-Z0-9_-]+$', alias) is not None
    
    def shorten_url(self, long_url, custom_alias=None, expiry_days=None, description=None):
        """
        Shorten a URL with customization options
        
        Args:
            long_url (str): The URL to shorten
            custom_alias (str): Custom alias for the short URL
            expiry_days (int): Number of days until the URL expires
            description (str): Optional description for the URL
        
        Returns:
            dict: Result containing short URL and details
        """
        
        # Validate URL
        if not self.is_valid_url(long_url):
            return {"error": "Invalid URL format"}
        
        # Handle custom alias
        if custom_alias:
            if not self.is_valid_alias(custom_alias):
                return {"error": "Custom alias can only contain letters, numbers, hyphens, and underscores"}
            
            if custom_alias in self.urls:
                return {"error": f"Custom alias '{custom_alias}' is already taken"}
            
            short_code = custom_alias
        else:
            # Generate random short code
            short_code = self.generate_short_code()
            while short_code in self.urls:
                short_code = self.generate_short_code()
        
        # Calculate expiry date
        expiry_date = None
        if expiry_days:
            expiry_date = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        # Create URL record
        url_record = {
            "long_url": long_url,
            "short_code": short_code,
            "created_at": datetime.now().isoformat(),
            "expiry_date": expiry_date,
            "description": description,
            "clicks": 0
        }
        
        # Store the URL
        self.urls[short_code] = url_record
        self.save_urls()
        
        short_url = f"{self.base_url}/{short_code}"
        
        return {
            "success": True,
            "short_url": short_url,
            "short_code": short_code,
            "long_url": long_url,
            "created_at": url_record["created_at"],
            "expiry_date": expiry_date,
            "description": description
        }
    
    def get_url_info(self, short_code):
        """Get information about a shortened URL"""
        if short_code not in self.urls:
            return {"error": "Short URL not found"}
        
        url_record = self.urls[short_code]
        
        # Check if URL has expired
        if url_record.get("expiry_date"):
            expiry = datetime.fromisoformat(url_record["expiry_date"])
            if datetime.now() > expiry:
                return {"error": "URL has expired"}
        
        return {
            "success": True,
            "long_url": url_record["long_url"],
            "short_code": short_code,
            "created_at": url_record["created_at"],
            "expiry_date": url_record.get("expiry_date"),
            "description": url_record.get("description"),
            "clicks": url_record.get("clicks", 0)
        }
    
    def expand_url(self, short_code):
        """Expand a short URL and increment click counter"""
        url_info = self.get_url_info(short_code)
        
        if "error" in url_info:
            return url_info
        
        # Increment click counter
        self.urls[short_code]["clicks"] += 1
        self.save_urls()
        
        return {
            "success": True,
            "long_url": url_info["long_url"],
            "redirecting_to": url_info["long_url"]
        }
    
    def list_urls(self):
        """List all shortened URLs"""
        if not self.urls:
            return {"message": "No URLs found"}
        
        url_list = []
        for short_code, record in self.urls.items():
            url_list.append({
                "short_url": f"{self.base_url}/{short_code}",
                "long_url": record["long_url"],
                "created_at": record["created_at"],
                "clicks": record.get("clicks", 0),
                "description": record.get("description", ""),
                "expiry_date": record.get("expiry_date")
            })
        
        return {"urls": url_list}

def main():
    """Main function to handle command line interface"""
    print("🔗 URL Shortener with Customization")
    print("=" * 40)
    
    shortener = URLShortener()
    
    while True:
        print("\nOptions:")
        print("1. Shorten a URL")
        print("2. Expand a short URL")
        print("3. Get URL info")
        print("4. List all URLs")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            long_url = input("Enter the long URL: ").strip()
            
            # Custom alias
            custom_alias = input("Enter custom alias (optional, press Enter to skip): ").strip()
            if not custom_alias:
                custom_alias = None
            
            # Expiry days
            expiry_input = input("Enter expiry days (optional, press Enter to skip): ").strip()
            expiry_days = None
            if expiry_input:
                try:
                    expiry_days = int(expiry_input)
                except ValueError:
                    print("Invalid expiry days. Using no expiry.")
            
            # Description
            description = input("Enter description (optional, press Enter to skip): ").strip()
            if not description:
                description = None
            
            result = shortener.shorten_url(long_url, custom_alias, expiry_days, description)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Success!")
                print(f"Short URL: {result['short_url']}")
                print(f"Original URL: {result['long_url']}")
                if result.get('description'):
                    print(f"Description: {result['description']}")
                if result.get('expiry_date'):
                    print(f"Expires: {result['expiry_date']}")
        
        elif choice == "2":
            short_code = input("Enter short code (e.g., 'abc123'): ").strip()
            result = shortener.expand_url(short_code)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Redirecting to: {result['long_url']}")
        
        elif choice == "3":
            short_code = input("Enter short code: ").strip()
            result = shortener.get_url_info(short_code)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ URL Information:")
                print(f"Short code: {result['short_code']}")
                print(f"Long URL: {result['long_url']}")
                print(f"Created: {result['created_at']}")
                print(f"Clicks: {result['clicks']}")
                if result.get('description'):
                    print(f"Description: {result['description']}")
                if result.get('expiry_date'):
                    print(f"Expires: {result['expiry_date']}")
        
        elif choice == "4":
            result = shortener.list_urls()
            
            if "message" in result:
                print(f"ℹ️ {result['message']}")
            else:
                print("📋 All URLs:")
                for i, url in enumerate(result['urls'], 1):
                    print(f"\n{i}. {url['short_url']}")
                    print(f"   → {url['long_url']}")
                    print(f"   Created: {url['created_at']}")
                    print(f"   Clicks: {url['clicks']}")
                    if url.get('description'):
                        print(f"   Description: {url['description']}")
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()