# Vercel Deployment Guide

This guide will help you deploy your Universal URL Shortener to Vercel with CI/CD pipeline.

## 🚀 Quick Deploy to Vercel

### Option 1: One-Click Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/your-repo)

### Option 2: Manual Deploy

#### Prerequisites
- [Vercel CLI](https://vercel.com/cli) installed
- [Git](https://git-scm.com/) installed
- GitHub account
- Vercel account

#### Step 1: Prepare Your Repository
```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

#### Step 2: Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

#### Step 3: Configure Environment Variables
In your Vercel dashboard, go to your project settings and add:
```
BASE_URL=https://your-app.vercel.app
HOST=0.0.0.0
PORT=8000
```

## 🔄 CI/CD Pipeline Setup

### GitHub Actions Configuration

1. **Get Vercel Tokens:**
   ```bash
   # Get your Vercel token
   vercel --token

   # Get project info
   vercel project list
   ```

2. **Add GitHub Secrets:**
   Go to your GitHub repository → Settings → Secrets and variables → Actions
   
   Add these secrets:
   - `VERCEL_TOKEN`: Your Vercel token
   - `VERCEL_ORG_ID`: Your Vercel team/org ID
   - `VERCEL_PROJECT_ID`: Your Vercel project ID

3. **Automatic Deployment:**
   - Push to `main` branch triggers production deployment
   - Pull requests trigger preview deployments
   - Tests run automatically before deployment

## 🐳 Docker Deployment

### Local Development with Docker
```bash
# Build and run with Docker
docker build -t url-shortener .
docker run -p 8000:8000 url-shortener

# Or use Docker Compose
docker-compose up --build
```

### Production Docker Deployment
```bash
# Build for production
docker build -t url-shortener:latest .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e BASE_URL=https://your-domain.com \
  -e HOST=0.0.0.0 \
  --name url-shortener \
  url-shortener:latest
```

## 🧪 Testing

### Run Tests Locally
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
python -m pytest tests/ -v

# Run with coverage
pip install pytest-cov
python -m pytest tests/ --cov=app --cov-report=html
```

### Continuous Testing
Tests automatically run on:
- Every push to main branch
- Every pull request
- Before deployment

## 📊 Monitoring & Performance

### Vercel Analytics
- Automatic performance monitoring
- Real-time analytics
- Error tracking

### Health Checks
The application includes:
- `/docs` - API documentation
- `/health` - Health check endpoint (if implemented)
- Automatic error reporting

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |
| `BASE_URL` | Base URL for short links | Auto-detected | No |
| `VERCEL_URL` | Vercel deployment URL | Auto-set | No |

### Vercel Configuration (`vercel.json`)
- Python 3.9 runtime
- Static file serving
- 30-second function timeout
- 15MB lambda size limit

## 🚨 Troubleshooting

### Common Issues

1. **Static files not loading:**
   - Check `vercel.json` routes configuration
   - Ensure static files are in correct directory

2. **JSON storage in serverless:**
   - Files are stored in `/tmp` in Vercel
   - Data is ephemeral (resets on cold starts)
   - Consider using external database for production

3. **Function timeout:**
   - Increase timeout in `vercel.json`
   - Optimize slow operations

### Performance Optimization

1. **Cold Start Optimization:**
   ```python
   # Keep functions warm
   @app.middleware("http")
   async def add_cache_headers(request: Request, call_next):
       response = await call_next(request)
       response.headers["Cache-Control"] = "public, max-age=300"
       return response
   ```

2. **Static Asset Optimization:**
   - CSS/JS files are automatically optimized by Vercel
   - Images are automatically compressed
   - CDN distribution worldwide

## 🎯 Production Recommendations

### For Production Use:
1. **Database:** Replace JSON storage with PostgreSQL/MongoDB
2. **Caching:** Add Redis for better performance
3. **Analytics:** Integrate with external analytics service
4. **Rate Limiting:** Add rate limiting for API endpoints
5. **Custom Domain:** Configure custom domain in Vercel
6. **SSL:** Automatic HTTPS with Vercel

### Example Production Architecture:
```
User → Vercel (FastAPI) → PostgreSQL (Database)
                       → Redis (Cache)
                       → Analytics Service
```

## 📝 Notes

- **Storage Limitation:** JSON file storage is temporary in serverless environment
- **Scaling:** Vercel automatically scales based on traffic
- **Monitoring:** Use Vercel Analytics for production monitoring
- **Logs:** Check Vercel dashboard for application logs
