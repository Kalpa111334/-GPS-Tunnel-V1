# Vercel Quick Setup Guide

## 🚀 Quick Build & Output Settings

### **1. Vercel Dashboard Settings**

Navigate to: **Project Settings > General > Build & Development Settings**

```
Framework Preset: Other
Build Command: npm run vercel-build
Output Directory: frontend/build
Install Command: npm install --legacy-peer-deps
Root Directory: ./
```

### **2. Environment Variables**

Go to: **Settings > Environment Variables**

#### **Add These Variables:**
```
MONGO_URL = mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME = gps_tunnel
GOOGLE_MAPS_API_KEY = AIzaSyARSoKujCNX2odk8wachQyz0DIjBCqJNd4
REACT_APP_BACKEND_URL = https://your-project-name.vercel.app
```

### **3. Project Structure**
```
GPS-Tunnel-V1/
├── api/
│   ├── index.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── build/ (generated)
│   ├── package.json
│   └── .npmrc
├── vercel.json
└── README.md
```

### **4. Build Commands**
```bash
# Frontend Build
npm run vercel-build

# Install Dependencies
npm install --legacy-peer-deps

# API (handled by Vercel)
# Uses api/requirements.txt
```

### **5. Deployment Steps**
1. Connect GitHub repository to Vercel
2. Set build settings (above)
3. Add environment variables
4. Deploy automatically on push to main

### **6. Verification**
- ✅ Frontend loads at your Vercel URL
- ✅ API responds at `/api/`
- ✅ Maps load correctly
- ✅ Database connection works

---

**Quick Fix for Build Issues:**
```bash
# If build fails, try:
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```
