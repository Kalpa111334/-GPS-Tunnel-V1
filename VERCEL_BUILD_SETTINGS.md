# Vercel Build and Output Settings Guide

## 🏗️ Build Settings Configuration

### 1. **Project Settings in Vercel Dashboard**

Navigate to your project in Vercel dashboard and go to **Settings > General**.

#### **Build & Development Settings**

```
Framework Preset: Other
Build Command: npm run vercel-build
Output Directory: frontend/build
Install Command: npm install --legacy-peer-deps
Development Command: npm start
```

#### **Root Directory**
```
Root Directory: ./
```

### 2. **Environment Variables**

Go to **Settings > Environment Variables** and add:

#### **Production Environment Variables**
```
MONGO_URL = mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME = gps_tunnel
GOOGLE_MAPS_API_KEY = AIzaSyARSoKujCNX2odk8wachQyz0DIjBCqJNd4
REACT_APP_BACKEND_URL = https://your-project-name.vercel.app
```

#### **Development Environment Variables**
```
MONGO_URL = mongodb://localhost:27017
DB_NAME = gps_tunnel
GOOGLE_MAPS_API_KEY = AIzaSyARSoKujCNX2odk8wachQyz0DIjBCqJNd4
REACT_APP_BACKEND_URL = http://localhost:3000
```

### 3. **Build Configuration Details**

#### **Frontend Build Settings**
```json
{
  "buildCommand": "cd frontend && npm run vercel-build",
  "outputDirectory": "frontend/build",
  "installCommand": "cd frontend && npm install --legacy-peer-deps"
}
```

#### **API Build Settings**
```json
{
  "functions": {
    "api/index.py": {
      "runtime": "python3.9"
    }
  }
}
```

## 📁 Project Structure for Vercel

```
GPS-Tunnel-V1/
├── api/                          # Serverless Functions
│   ├── index.py                 # Main API handler
│   └── requirements.txt         # Python dependencies
├── frontend/                     # React Application
│   ├── src/                     # Source code
│   ├── public/                  # Static assets
│   ├── build/                   # Build output (generated)
│   ├── package.json             # Dependencies & scripts
│   ├── .env                     # Environment variables
│   ├── .env.production          # Production env vars
│   └── .npmrc                   # NPM configuration
├── backend/                      # Local development backend
│   ├── server.py                # FastAPI server
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Local environment
├── vercel.json                  # Vercel configuration
├── DEPLOYMENT.md                # Deployment guide
└── README.md                    # Project documentation
```

## ⚙️ Vercel Configuration (vercel.json)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "env": {
    "DB_NAME": "gps_tunnel"
  }
}
```

## 🚀 Build Process Flow

### **Step 1: Install Dependencies**
```bash
# Frontend dependencies
cd frontend
npm install --legacy-peer-deps

# API dependencies (handled by Vercel)
pip install -r api/requirements.txt
```

### **Step 2: Build Frontend**
```bash
cd frontend
npm run vercel-build
# Creates: frontend/build/ directory
```

### **Step 3: Deploy API Functions**
```bash
# Vercel automatically handles Python functions
# Based on api/index.py and api/requirements.txt
```

## 📋 Build Commands Reference

### **Frontend Build Commands**
```bash
# Development
npm start

# Production build
npm run vercel-build
# or
npm run build

# Install with legacy peer deps
npm install --legacy-peer-deps
```

### **Backend Commands (Local Development)**
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run server
python -m uvicorn backend.server:app --reload
```

## 🔧 Troubleshooting Build Issues

### **Common Build Errors & Solutions**

#### **1. Dependency Conflicts**
```bash
# Error: ERESOLVE could not resolve
# Solution: Use legacy peer deps
npm install --legacy-peer-deps
```

#### **2. Module Not Found (ajv)**
```bash
# Error: Cannot find module 'ajv/dist/compile/codegen'
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

#### **3. Python Import Errors**
```bash
# Error: ModuleNotFoundError
# Solution: Check requirements.txt includes all dependencies
pip install -r api/requirements.txt
```

### **Build Log Analysis**

#### **Successful Build Output**
```
✓ Installing dependencies
✓ Building frontend
✓ Deploying API functions
✓ Deployment complete
```

#### **Failed Build Indicators**
```
✗ Command "npm install" exited with 1
✗ Command "npm run vercel-build" exited with 1
✗ Module not found
```

## 🌐 Output Directory Structure

### **Frontend Build Output**
```
frontend/build/
├── static/
│   ├── css/
│   ├── js/
│   └── media/
├── index.html
├── manifest.json
└── robots.txt
```

### **API Function Output**
```
api/
├── index.py          # Deployed as serverless function
└── requirements.txt  # Dependencies for function
```

## 📊 Performance Optimization

### **Build Optimization Settings**
```json
{
  "buildCommand": "npm run vercel-build",
  "outputDirectory": "frontend/build",
  "installCommand": "npm ci --legacy-peer-deps",
  "devCommand": "npm start"
}
```

### **Caching Configuration**
```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

## 🔄 Deployment Workflow

### **Automatic Deployment (GitHub Integration)**
1. Push to main branch
2. Vercel detects changes
3. Runs build process
4. Deploys to production

### **Manual Deployment**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# Deploy with specific settings
vercel --prod --build-env NODE_ENV=production
```

## 📱 Post-Deployment Verification

### **Check Deployment Status**
1. Visit your Vercel dashboard
2. Check deployment logs
3. Verify environment variables
4. Test API endpoints
5. Test frontend functionality

### **Health Check Endpoints**
```
GET /api/                    # API health check
GET /api/languages          # Supported languages
GET /api/tour-routes        # Tour routes
```

## 🛠️ Advanced Configuration

### **Custom Build Scripts**
```json
{
  "scripts": {
    "vercel-build": "react-scripts build",
    "build": "react-scripts build",
    "start": "react-scripts start",
    "test": "react-scripts test"
  }
}
```

### **Environment-Specific Builds**
```json
{
  "build": {
    "env": {
      "NODE_ENV": "production",
      "REACT_APP_ENV": "production"
    }
  }
}
```

## 📞 Support & Resources

### **Vercel Documentation**
- [Vercel Build Settings](https://vercel.com/docs/build-step)
- [Environment Variables](https://vercel.com/docs/environment-variables)
- [Serverless Functions](https://vercel.com/docs/serverless-functions)

### **Troubleshooting Resources**
- [Vercel Build Logs](https://vercel.com/docs/build-logs)
- [Common Build Errors](https://vercel.com/docs/build-errors)
- [Performance Optimization](https://vercel.com/docs/performance)

---

**Note**: Make sure to replace placeholder values (like MongoDB connection strings and API keys) with your actual production values before deploying.
