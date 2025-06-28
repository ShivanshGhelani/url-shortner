#!/usr/bin/env python3
"""
Supabase Image URL Shortener
Optimized for shortening long Supabase storage URLs for clean web integration.
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

class SupabaseURLShortener:
    def __init__(self, base_url="http://localhost:8080", storage_file="supabase_urls.json"):
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
    
    def is_supabase_url(self, url):
        """Check if URL is from Supabase storage"""
        return 'supabase.co/storage/v1/object/public' in url
    
    def extract_filename(self, supabase_url):
        """Extract filename from Supabase URL for smart alias generation"""
        try:
            # Remove the trailing | if present
            url = supabase_url.rstrip('|')
            # Get the last part after the last /
            filename = url.split('/')[-1]
            # Remove file extension and clean up
            name_part = filename.split('.')[0]
            # Remove timestamp-like numbers and clean
            clean_name = re.sub(r'_\d{10,}', '', name_part)
            # Replace underscores with hyphens and make lowercase
            clean_name = clean_name.replace('_', '-').lower()
            return clean_name
        except:
            return None
    
    def generate_smart_alias(self, supabase_url):
        """Generate a smart alias based on the image filename"""
        base_alias = self.extract_filename(supabase_url)
        if not base_alias:
            return self.generate_short_code()
        
        # If the base alias is available, use it
        if base_alias not in self.urls:
            return base_alias
        
        # If taken, add a number
        counter = 1
        while f"{base_alias}-{counter}" in self.urls:
            counter += 1
        
        return f"{base_alias}-{counter}"
    
    def generate_short_code(self, length=6):
        """Generate a random short code"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def is_valid_alias(self, alias):
        """Check if alias contains only valid characters"""
        return re.match('^[a-zA-Z0-9_-]+$', alias) is not None
    
    def shorten_supabase_url(self, supabase_url, custom_alias=None, description=None):
        """
        Shorten a Supabase URL with smart alias generation
        
        Args:
            supabase_url (str): The Supabase URL to shorten
            custom_alias (str): Custom alias for the short URL
            description (str): Optional description for the URL
        
        Returns:
            dict: Result containing short URL and details
        """
        
        # Clean the URL (remove trailing |)
        supabase_url = supabase_url.rstrip('|')
        
        # Validate if it's a Supabase URL
        if not self.is_supabase_url(supabase_url):
            return {"error": "This doesn't appear to be a Supabase storage URL"}
        
        # Handle custom alias
        if custom_alias:
            if not self.is_valid_alias(custom_alias):
                return {"error": "Custom alias can only contain letters, numbers, hyphens, and underscores"}
            
            if custom_alias in self.urls:
                return {"error": f"Custom alias '{custom_alias}' is already taken"}
            
            short_code = custom_alias
        else:
            # Generate smart alias based on filename
            short_code = self.generate_smart_alias(supabase_url)
        
        # Create URL record
        url_record = {
            "long_url": supabase_url,
            "short_code": short_code,
            "created_at": datetime.now().isoformat(),
            "description": description or self.extract_filename(supabase_url),
            "clicks": 0,
            "is_supabase": True,
            "file_type": self.get_file_type(supabase_url)
        }
        
        # Store the URL
        self.urls[short_code] = url_record
        self.save_urls()
        
        short_url = f"{self.base_url}/{short_code}"
        
        return {
            "success": True,
            "short_url": short_url,
            "short_code": short_code,
            "long_url": supabase_url,
            "created_at": url_record["created_at"],
            "description": url_record["description"],
            "file_type": url_record["file_type"]
        }
    
    def get_file_type(self, url):
        """Extract file type from URL"""
        try:
            extension = url.split('.')[-1].lower()
            if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                return 'image'
            elif extension in ['pdf']:
                return 'document'
            elif extension in ['mp4', 'mov', 'avi']:
                return 'video'
            else:
                return 'file'
        except:
            return 'file'
    
    def get_url_info(self, short_code):
        """Get information about a shortened URL"""
        if short_code not in self.urls:
            return {"error": "Short URL not found"}
        
        url_record = self.urls[short_code]
        
        return {
            "success": True,
            "long_url": url_record["long_url"],
            "short_code": short_code,
            "created_at": url_record["created_at"],
            "description": url_record.get("description"),
            "clicks": url_record.get("clicks", 0),
            "file_type": url_record.get("file_type", "file")
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
            "file_type": url_info["file_type"]
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
                "file_type": record.get("file_type", "file")
            })
        
        return {"urls": url_list}
    
    def generate_html_code(self, short_code):
        """Generate HTML code snippet for easy web integration"""
        url_info = self.get_url_info(short_code)
        if "error" in url_info:
            return url_info
        
        short_url = f"{self.base_url}/{short_code}"
        file_type = url_info.get("file_type", "file")
        description = url_info.get("description", "Image")
        
        if file_type == "image":
            html = f'<img src="{short_url}" alt="{description}" />'
        else:
            html = f'<a href="{short_url}" target="_blank">{description}</a>'
        
        return {
            "success": True,
            "html": html,
            "short_url": short_url,
            "file_type": file_type
        }

# Global shortener instance
shortener = SupabaseURLShortener()

class SupabaseURLHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        path = self.path.lstrip('/')
        
        if not path:
            # Serve homepage with Supabase-specific interface
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Supabase URL Shortener</title>
                <style>
                    body { font-family: 'Segoe UI', system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f8fafc; }
                    .header { text-align: center; margin-bottom: 40px; }
                    .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); }
                    h1 { color: #1e293b; margin: 0; font-size: 2.2em; }
                    .subtitle { color: #64748b; margin-top: 8px; }
                    .info { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .url-item { background: #f8fafc; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #3b82f6; }
                    .short-url { font-weight: 600; color: #3b82f6; font-size: 1.1em; }
                    .long-url { color: #64748b; word-break: break-all; margin: 8px 0; font-family: monospace; font-size: 0.9em; }
                    .stats { font-size: 0.85em; color: #94a3b8; display: flex; gap: 15px; }
                    .file-type { background: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
                    .image-preview { max-width: 100px; max-height: 60px; border-radius: 4px; margin-top: 10px; }
                    .copy-btn { background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; margin-left: 10px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🔗 Supabase URL Shortener</h1>
                    <p class="subtitle">Clean, short URLs for your Supabase storage files</p>
                </div>
                
                <div class="container">
                    <div class="info">
                        <strong>📸 Server is running!</strong><br>
                        Perfect for shortening long Supabase image URLs for cleaner web integration.
                        <br><br>
                        <strong>Usage:</strong><br>
                        • Paste your Supabase URLs in the command line<br>
                        • Get clean, short URLs like <code>localhost:8080/shivansh-ghelani</code><br>
                        • Copy the HTML code for easy web integration
                    </div>
            """
            
            # Show existing URLs
            url_list = shortener.list_urls()
            if "urls" in url_list:
                html += f"<h2>📁 Your Shortened URLs ({len(url_list['urls'])} total):</h2>"
                for url in url_list["urls"]:
                    file_type_badge = f'<span class="file-type">{url["file_type"]}</span>'
                    short_code = url['short_url'].split('/')[-1]
                    
                    html += f"""
                    <div class="url-item">
                        <div class="short-url">
                            <a href="/{short_code}" target="_blank">{url['short_url']}</a>
                            <button class="copy-btn" onclick="copyToClipboard('{url['short_url']}')">Copy</button>
                            {file_type_badge}
                        </div>
                        <div class="long-url">{url['long_url']}</div>
                        <div class="stats">
                            <span>👆 {url['clicks']} clicks</span>
                            <span>📅 {url['created_at'][:19]}</span>
                            <span>📝 {url['description']}</span>
                        </div>
                    """
                    
                    # Show image preview for images
                    if url['file_type'] == 'image':
                        html += f'<img src="/{short_code}" class="image-preview" alt="Preview" />'
                    
                    html += "</div>"
            else:
                html += "<p>📭 No URLs created yet. Use the command line to shorten your first Supabase URL!</p>"
            
            html += """
                </div>
                <script>
                    function copyToClipboard(text) {
                        navigator.clipboard.writeText(text).then(() => {
                            alert('URL copied to clipboard!');
                        });
                    }
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
            return
        
        # Handle short URL redirect
        result = shortener.expand_url(path)
        
        if "error" in result:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>File Not Found</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 100px; color: #64748b; }}
                    .error {{ color: #ef4444; font-size: 1.2em; }}
                </style>
            </head>
            <body>
                <h1 class="error">📁 {result['error']}</h1>
                <p>The shortened URL you're looking for doesn't exist.</p>
                <p><a href="/">← Back to dashboard</a></p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode('utf-8'))
        else:
            # For images, serve them directly with proper headers
            if result.get('file_type') == 'image':
                self.send_response(302)
                self.send_header('Location', result['long_url'])
                self.send_header('Cache-Control', 'public, max-age=3600')
                self.end_headers()
                print(f"🖼️  Serving image: /{path} → {result['long_url']}")
            else:
                # Regular redirect
                self.send_response(302)
                self.send_header('Location', result['long_url'])
                self.end_headers()
                print(f"📁 Redirecting: /{path} → {result['long_url']}")
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logs"""
        pass

def start_server():
    """Start the HTTP server"""
    server = HTTPServer(('localhost', 8080), SupabaseURLHandler)
    print("🌐 Supabase URL Shortener server started at http://localhost:8080")
    server.serve_forever()

def main():
    """Main function with Supabase-optimized interface"""
    print("🔗 Supabase Image URL Shortener")
    print("=" * 40)
    print("📸 Optimized for Supabase storage URLs")
    
    # Start web server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    
    print(f"\n🌐 Dashboard: http://localhost:8080")
    print("💡 Perfect for cleaning up messy Supabase URLs in your web projects!")
    
    while True:
        print("\n" + "─" * 45)
        print("Options:")
        print("1. 📸 Shorten Supabase URL")
        print("2. 📋 Get HTML code snippet")
        print("3. 📊 View URL info")
        print("4. 📁 List all URLs")
        print("5. 🌐 Open dashboard")
        print("6. 🚪 Exit")
        
        choice = input(f"\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            print(f"\n📝 Shorten Supabase URL")
            print("─" * 25)
            print("💡 Paste your long Supabase URL below:")
            
            supabase_url = input("URL: ").strip()
            
            # Custom alias
            print(f"\n🏷️  Custom alias (optional):")
            print("   Leave empty for smart auto-generation based on filename")
            custom_alias = input("Alias: ").strip()
            if not custom_alias:
                custom_alias = None
            
            # Description
            description = input("Description (optional): ").strip()
            if not description:
                description = None
            
            result = shortener.shorten_supabase_url(supabase_url, custom_alias, description)
            
            if "error" in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print(f"\n✅ Success! Your clean URL:")
                print(f"🔗 {result['short_url']}")
                print(f"📂 File type: {result['file_type']}")
                print(f"📝 Description: {result['description']}")
                print(f"\n💻 Ready for web integration!")
                print(f"   Original: {len(result['long_url'])} characters")
                print(f"   Shortened: {len(result['short_url'])} characters")
                print(f"   Saved: {len(result['long_url']) - len(result['short_url'])} characters!")
        
        elif choice == "2":
            short_code = input(f"\nEnter short code for HTML snippet: ").strip()
            result = shortener.generate_html_code(short_code)
            
            if "error" in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print(f"\n💻 HTML Code Snippet:")
                print("─" * 25)
                print(f"{result['html']}")
                print(f"\n📋 Copy and paste this into your web page!")
                print(f"🔗 URL: {result['short_url']}")
                print(f"📂 Type: {result['file_type']}")
        
        elif choice == "3":
            short_code = input(f"\nEnter short code: ").strip()
            result = shortener.get_url_info(short_code)
            
            if "error" in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print(f"\n📊 URL Statistics:")
                print("─" * 20)
                print(f"🔗 Short: {shortener.base_url}/{result['short_code']}")
                print(f"📍 Original: {result['long_url']}")
                print(f"📂 File type: {result['file_type']}")
                print(f"📅 Created: {result['created_at'][:19]}")
                print(f"👆 Clicks: {result['clicks']}")
                print(f"📝 Description: {result['description']}")
        
        elif choice == "4":
            result = shortener.list_urls()
            
            if "message" in result:
                print(f"\nℹ️ {result['message']}")
            else:
                print(f"\n📁 All Shortened URLs ({len(result['urls'])} total):")
                print("=" * 50)
                for i, url in enumerate(result['urls'], 1):
                    print(f"\n{i}. 🔗 {url['short_url']}")
                    print(f"   📂 {url['file_type'].upper()} | 👆 {url['clicks']} clicks")
                    print(f"   📝 {url['description']}")
                    print(f"   📍 {url['long_url'][:60]}...")
        
        elif choice == "5":
            print(f"\n🌐 Opening dashboard...")
            webbrowser.open('http://localhost:8080')
        
        elif choice == "6":
            print(f"\n👋 Thanks for using Supabase URL Shortener!")
            break
        
        else:
            print(f"\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure port 8080 is available.")