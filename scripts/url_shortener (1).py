#!/usr/bin/env python3
"""
Local URL Shortener with Web Server
A Python script that creates a working URL shortener with a local web server.
"""

import json
import os
import random
import string
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import webbrowser
import time

class URLShortener:
    def __init__(self, base_url="http://localhost:8080", storage_file="urls.json"):
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
        """Shorten a URL with customization options"""
        
        # Add http:// if no scheme provided
        if not long_url.startswith(('http://', 'https://')):
            long_url = 'https://' + long_url
        
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

# Global shortener instance
shortener = URLShortener()

class URLHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        path = self.path.lstrip('/')
        
        if not path:
            # Serve a simple homepage
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Local URL Shortener</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                    .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
                    h1 { color: #333; text-align: center; }
                    .info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .url-item { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #2196F3; }
                    .short-url { font-weight: bold; color: #2196F3; }
                    .long-url { color: #666; word-break: break-all; }
                    .stats { font-size: 0.9em; color: #888; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔗 Local URL Shortener</h1>
                    <div class="info">
                        <strong>Server is running!</strong><br>
                        Use the command line interface to create short URLs, then test them here.
                        <br><br>
                        <strong>How to use:</strong><br>
                        1. Create short URLs using the Python script<br>
                        2. Click on the generated short URLs to test them<br>
                        3. Short URLs will redirect to the original URLs
                    </div>
            """
            
            # Show existing URLs
            url_list = shortener.list_urls()
            if "urls" in url_list:
                html += "<h2>Your Short URLs:</h2>"
                for url in url_list["urls"]:
                    html += f"""
                    <div class="url-item">
                        <div class="short-url">
                            <a href="/{url['short_url'].split('/')[-1]}" target="_blank">
                                {url['short_url']}
                            </a>
                        </div>
                        <div class="long-url">→ {url['long_url']}</div>
                        <div class="stats">
                            Clicks: {url['clicks']} | Created: {url['created_at'][:19]}
                            {f" | {url['description']}" if url.get('description') else ""}
                        </div>
                    </div>
                    """
            else:
                html += "<p>No URLs created yet. Use the command line to create your first short URL!</p>"
            
            html += """
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
            return
        
        # Handle short URL redirect
        result = shortener.expand_url(path)
        
        if "error" in result:
            # URL not found or expired
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>URL Not Found</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }}
                    .error {{ color: #f44336; }}
                </style>
            </head>
            <body>
                <h1 class="error">❌ {result['error']}</h1>
                <p><a href="/">← Back to homepage</a></p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode('utf-8'))
        else:
            # Redirect to the long URL
            self.send_response(302)
            self.send_header('Location', result['long_url'])
            self.end_headers()
            print(f"✅ Redirecting /{path} → {result['long_url']}")
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logs"""
        pass

def start_server():
    """Start the HTTP server"""
    server = HTTPServer(('localhost', 8080), URLHandler)
    print("🌐 Web server started at http://localhost:8080")
    print("   Visit the URL above to see your shortened URLs")
    server.serve_forever()

def main():
    """Main function with improved interface"""
    print("🔗 Local URL Shortener with Web Server")
    print("=" * 45)
    
    # Start web server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(1)
    
    print("\nThe web server is now running!")
    print("📋 You can view all your URLs at: http://localhost:8080")
    
    while True:
        print("\n" + "─" * 40)
        print("Options:")
        print("1. Shorten a URL")
        print("2. View URL info")
        print("3. List all URLs")
        print("4. Open web interface")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n📝 Create Short URL")
            print("─" * 20)
            long_url = input("Enter the URL to shorten: ").strip()
            
            # Custom alias
            custom_alias = input("Custom alias (optional): ").strip()
            if not custom_alias:
                custom_alias = None
            
            # Expiry days
            expiry_input = input("Expiry days (optional): ").strip()
            expiry_days = None
            if expiry_input:
                try:
                    expiry_days = int(expiry_input)
                except ValueError:
                    print("⚠️  Invalid expiry days. Using no expiry.")
            
            # Description
            description = input("Description (optional): ").strip()
            if not description:
                description = None
            
            result = shortener.shorten_url(long_url, custom_alias, expiry_days, description)
            
            if "error" in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print(f"\n✅ Success! Short URL created:")
                print(f"🔗 {result['short_url']}")
                print(f"📍 Original: {result['long_url']}")
                if result.get('description'):
                    print(f"📝 Description: {result['description']}")
                if result.get('expiry_date'):
                    print(f"⏰ Expires: {result['expiry_date'][:19]}")
                print(f"\n💡 Test it: Click the link above or visit http://localhost:8080")
        
        elif choice == "2":
            short_code = input("\nEnter short code: ").strip()
            result = shortener.get_url_info(short_code)
            
            if "error" in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print(f"\n📊 URL Information:")
                print(f"🔗 Short: {shortener.base_url}/{result['short_code']}")
                print(f"📍 Long: {result['long_url']}")
                print(f"📅 Created: {result['created_at'][:19]}")
                print(f"👆 Clicks: {result['clicks']}")
                if result.get('description'):
                    print(f"📝 Description: {result['description']}")
                if result.get('expiry_date'):
                    print(f"⏰ Expires: {result['expiry_date'][:19]}")
        
        elif choice == "3":
            result = shortener.list_urls()
            
            if "message" in result:
                print(f"\nℹ️ {result['message']}")
            else:
                print(f"\n📋 All URLs ({len(result['urls'])} total):")
                print("─" * 40)
                for i, url in enumerate(result['urls'], 1):
                    print(f"{i}. {url['short_url']}")
                    print(f"   → {url['long_url']}")
                    print(f"   👆 {url['clicks']} clicks | Created: {url['created_at'][:19]}")
                    if url.get('description'):
                        print(f"   📝 {url['description']}")
                    print()
        
        elif choice == "4":
            print("\n🌐 Opening web interface...")
            webbrowser.open('http://localhost:8080')
        
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure port 8080 is available.")