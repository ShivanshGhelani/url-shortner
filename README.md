# Universal URL Shortener

A modern, full-featured URL shortening service built with FastAPI, Jinja2, and TailwindCSS.

## Features

### 🔗 Universal URL Support
- **All URL Types**: Works with any valid URL - web pages, images, documents, videos, etc.
- **Supabase Optimized**: Special handling for Supabase storage URLs with smart filename extraction
- **Smart Aliases**: Automatically generates meaningful short codes based on filenames or domains
- **Custom Aliases**: Create your own memorable short codes

### 🎨 Modern Web Interface
- **Beautiful UI**: Clean, responsive design with TailwindCSS
- **Dark Mode Ready**: Modern gradient designs and hover effects
- **Mobile Friendly**: Optimized for all device sizes
- **Interactive Elements**: Real-time feedback and smooth transitions

### 🚀 Advanced Features
- **Bulk Shortening**: Process multiple URLs at once with progress tracking
- **Analytics Dashboard**: Track clicks, performance metrics, and usage statistics
- **QR Code Generation**: Automatic QR codes for easy sharing
- **Password Protection**: Secure your links with password protection
- **HTML Snippets**: Ready-to-use HTML code for web integration
- **Export Options**: Download your data as CSV

### 🛡️ Security & Management
- **URL Validation**: Comprehensive URL validation and sanitization
- **Click Tracking**: Monitor link performance and usage
- **Expiry Dates**: Set automatic link expiration

## 🚀 Deployment

### Quick Deploy to Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/your-repo)

### Local Development
```bash
# Clone the repository
git clone <your-repo-url>
cd web_service

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn main:app --reload
```

### Production Deployment Options

1. **Vercel (Recommended)**
   ```bash
   npm i -g vercel
   vercel --prod
   ```

2. **Docker**
   ```bash
   docker build -t url-shortener .
   docker run -p 8000:8000 url-shortener
   ```

3. **Docker Compose**
   ```bash
   docker-compose up --build
   ```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Environment Variables
```bash
HOST=0.0.0.0
PORT=8000
BASE_URL=https://your-domain.com
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**
   ```bash
   cd s:\Projects\FastAPI\OnGIT\URL-Shortner\web_service
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Project Structure

```
web_service/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py      # Application configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── url_models.py  # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── api_router.py  # REST API endpoints
│   │   └── url_router.py  # Web interface routes
│   ├── services/
│   │   ├── __init__.py
│   │   └── url_service.py # Core URL shortening logic
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── analytics.html
│   │   ├── bulk.html
│   │   ├── result.html
│   │   └── url_info.html
│   └── static/           # CSS, JS, images
│       ├── css/
│       └── js/
└── urls.json            # URL storage (created automatically)
```

## Usage

### Web Interface

1. **Home Page** (`/`)
   - Enter any URL to shorten
   - Optional custom alias and description
   - Advanced options: password protection, expiry dates

2. **Dashboard** (`/dashboard`)
   - View all your shortened URLs
   - Click tracking and statistics
   - Quick actions: copy, view details, delete

3. **Analytics** (`/analytics`)
   - Performance metrics and charts
   - Top performing URLs
   - Content type distribution

4. **Bulk Shortener** (`/bulk`)
   - Process multiple URLs at once
   - Progress tracking and results export
   - CSV download of results

### API Endpoints

- `POST /api/shorten` - Shorten a URL
- `GET /api/info/{short_code}` - Get URL information
- `GET /api/expand/{short_code}` - Expand a short URL
- `DELETE /api/delete/{short_code}` - Delete a URL
- `GET /api/list` - List all URLs (with pagination)
- `GET /api/stats` - Get usage statistics

### URL Redirection

- `GET /{short_code}` - Redirect to original URL

## Configuration

Edit `app/core/config.py` to customize:

- **Server Settings**: Host, port, base URL
- **Features**: Enable/disable QR codes, analytics
- **Security**: Allowed hosts, CORS settings
- **Storage**: File paths, database settings

## Features in Detail

### Smart Alias Generation
The system automatically creates meaningful short codes:
- **Filenames**: Extracts and cleans filenames from URLs
- **Domains**: Uses domain names when filenames aren't available
- **Conflict Resolution**: Adds numbers for duplicate aliases
- **Validation**: Ensures aliases contain only valid characters

### File Type Detection
Automatically categorizes URLs by content type:
- **Images**: jpg, png, gif, svg, webp, etc.
- **Videos**: mp4, mov, avi, mkv, etc.
- **Documents**: pdf, doc, txt, etc.
- **Audio**: mp3, wav, flac, etc.
- **Archives**: zip, rar, 7z, etc.
- **Special**: GitHub repos, YouTube videos, etc.

### Analytics & Tracking
- **Click Counting**: Track how many times each link is accessed
- **Last Accessed**: Monitor recent activity
- **Performance Metrics**: Calculate average clicks per URL
- **Time-based Stats**: Weekly activity summaries

### Security Features
- **URL Validation**: Prevents malicious or invalid URLs
- **Password Protection**: Optional password gates for sensitive links
- **Input Sanitization**: Protects against XSS and injection attacks
- **Safe Redirects**: Validates destination URLs before redirecting

## Deployment

### Development
```bash
python main.py
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please visit the project repository or contact the development team.

---

**Built with ❤️ using FastAPI, Jinja2, and TailwindCSS**
