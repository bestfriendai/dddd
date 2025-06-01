# Quick Vercel + Railway Deployment Guide

## 🚀 Quick Start

### 1. Deploy Backend to Railway

1. **Sign up** at [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. **Select** your DeerFlow repository
4. **Add Environment Variables**:
   ```
   APP_ENV=production
   SEARCH_API=tavily
   TAVILY_API_KEY=your_tavily_key_here
   OPENAI_API_KEY=your_openai_key_here
   ```
5. **Deploy** - Railway will use the `railway.toml` configuration
6. **Copy** your Railway URL (e.g., `https://your-app.railway.app`)

### 2. Deploy Frontend to Vercel

1. **Sign up** at [vercel.com](https://vercel.com)
2. **New Project** → **Import** your DeerFlow repository
3. **Configure Project**:
   - **Root Directory**: `web`
   - **Framework**: Next.js (auto-detected)
4. **Add Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app/api
   ```
5. **Deploy**

### 3. Update CORS

1. **Go back to Railway**
2. **Add Environment Variable**:
   ```
   FRONTEND_URL=https://your-vercel-app.vercel.app
   ```
3. **Redeploy** (automatic)

## ✅ Test Your Deployment

1. Visit your Vercel URL
2. Try a research query
3. Check that it connects to your Railway backend

## 🔧 Required API Keys

- **TAVILY_API_KEY**: Get from [tavily.com](https://app.tavily.com/home)
- **OPENAI_API_KEY**: Get from [openai.com](https://platform.openai.com/api-keys)

## 📁 Files Created for Deployment

- `vercel.json` - Vercel configuration
- `railway.toml` - Railway configuration  
- `.env.production` - Backend environment template
- `web/.env.production` - Frontend environment template
- `DEPLOYMENT.md` - Detailed deployment guide

## 🆘 Troubleshooting

**CORS Error**: Check `FRONTEND_URL` in Railway matches your Vercel URL
**API Connection Failed**: Check `NEXT_PUBLIC_API_URL` in Vercel matches your Railway URL
**Build Failed**: Check logs in respective platform dashboards

## 📖 Need More Help?

See the detailed [DEPLOYMENT.md](DEPLOYMENT.md) guide for complete instructions.
