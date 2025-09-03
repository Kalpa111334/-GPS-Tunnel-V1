# GPS Tunnel - Vercel Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy the Project
```bash
vercel
```

### 4. Set Environment Variables
After deployment, set these environment variables in your Vercel dashboard:

- `MONGO_URL`: Your MongoDB connection string (e.g., `mongodb+srv://username:password@cluster.mongodb.net/`)
- `DB_NAME`: Database name (e.g., `gps_tunnel`)
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key

### 5. Update Frontend Environment
After getting your Vercel URL, update the frontend environment:

1. Go to your Vercel dashboard
2. Find your project
3. Go to Settings > Environment Variables
4. Add: `REACT_APP_BACKEND_URL` = `https://your-project-name.vercel.app`

## 📁 Project Structure for Vercel

```
├── api/                    # Serverless functions
│   ├── index.py           # Main API handler
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/
│   ├── package.json
│   └── .env.production    # Production environment
├── vercel.json           # Vercel configuration
└── DEPLOYMENT.md         # This file
```

## 🔧 Configuration Files

### vercel.json
- Configures builds for both frontend and API
- Sets up routing for API endpoints
- Defines environment variables

### api/index.py
- FastAPI application adapted for Vercel serverless functions
- All backend routes and functionality
- MongoDB and Google Maps integration

### frontend/package.json
- Added `vercel-build` script
- Configured for static build deployment

## 🌐 Environment Variables

### Required Environment Variables:
1. **MONGO_URL**: MongoDB connection string
2. **DB_NAME**: Database name
3. **GOOGLE_MAPS_API_KEY**: Google Maps API key
4. **REACT_APP_BACKEND_URL**: Backend URL (set after deployment)

### Setting Environment Variables:

#### Option 1: Vercel Dashboard
1. Go to your project in Vercel dashboard
2. Navigate to Settings > Environment Variables
3. Add each variable with appropriate values

#### Option 2: Vercel CLI
```bash
vercel env add MONGO_URL
vercel env add DB_NAME
vercel env add GOOGLE_MAPS_API_KEY
vercel env add REACT_APP_BACKEND_URL
```

## 🗄️ Database Setup

### MongoDB Atlas (Recommended)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a new cluster
3. Get your connection string
4. Set `MONGO_URL` environment variable

### Local MongoDB (Development)
- Use `mongodb://localhost:27017` for local development
- Not suitable for production deployment

## 🗺️ Google Maps API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the following APIs:
   - Maps JavaScript API
   - Places API
   - Directions API
   - Geocoding API
4. Create an API key
5. Set `GOOGLE_MAPS_API_KEY` environment variable

## 🚀 Deployment Commands

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (first time)
vercel

# Deploy updates
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs
```

## 🔍 Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check that all dependencies are in package.json
   - Ensure Python requirements are in api/requirements.txt

2. **API Not Working**
   - Verify environment variables are set
   - Check MongoDB connection string
   - Ensure Google Maps API key is valid

3. **Frontend Not Loading**
   - Check REACT_APP_BACKEND_URL is set correctly
   - Verify build completed successfully

4. **CORS Issues**
   - CORS is configured to allow all origins in production
   - Check if API routes are accessible

### Debug Commands:
```bash
# Check environment variables
vercel env ls

# View function logs
vercel logs --follow

# Test API locally
vercel dev
```

## 📱 Features After Deployment

- ✅ Destination search using Google Places API
- ✅ Turn-by-turn navigation with Google Directions
- ✅ Multi-language support (15+ languages)
- ✅ Real-time GPS tracking
- ✅ Amsterdam canal dining tour
- ✅ Interactive maps with custom markers
- ✅ Voice navigation and audio content

## 🔗 Post-Deployment

1. **Test the Application**
   - Visit your Vercel URL
   - Test destination search
   - Try the dining tour feature
   - Verify multi-language support

2. **Custom Domain (Optional)**
   - Add custom domain in Vercel dashboard
   - Update DNS settings
   - Update environment variables if needed

3. **Monitoring**
   - Use Vercel Analytics for performance monitoring
   - Check function logs for errors
   - Monitor API usage and limits

## 📞 Support

If you encounter issues:
1. Check Vercel deployment logs
2. Verify all environment variables are set
3. Test API endpoints individually
4. Check MongoDB and Google Maps API quotas

Happy deploying! 🎉
