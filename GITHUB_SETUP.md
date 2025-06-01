# 🚀 GitHub Repository Setup for PrivateSearch

## Step-by-Step Instructions

### 1. Create GitHub Repository

1. **Go to [github.com](https://github.com)** and sign in
2. **Click "+" → "New repository"**
3. **Repository name**: `PrivateSearch`
4. **Description**: `Privacy-focused AI research platform with advanced language models`
5. **Make it Public** (recommended for easier deployment)
6. **Don't check** "Add a README file" (we have our own)
7. **Click "Create repository"**

### 2. Initialize and Push Code

Open terminal/command prompt in the `deer-flow-main` directory and run:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: PrivateSearch - Privacy-focused AI research platform"

# Add your GitHub repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/PrivateSearch.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Verify Upload

Check your GitHub repository to ensure all files are uploaded:

- ✅ `README.md` (updated for PrivateSearch)
- ✅ `vercel.json` (Vercel configuration)
- ✅ `railway.toml` (Railway configuration)
- ✅ `DEPLOYMENT.md` (deployment guide)
- ✅ `VERCEL_DEPLOYMENT.md` (quick start)
- ✅ `web/` directory (frontend code)
- ✅ `src/` directory (backend code)
- ✅ All other project files

### 4. Next Steps

Once your repository is on GitHub:

1. **Deploy Backend to Railway**:
   - Go to [railway.app](https://railway.app)
   - Create new project from GitHub repo
   - Configure environment variables

2. **Deploy Frontend to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import GitHub repository
   - Set root directory to `web`
   - Configure environment variables

### 5. Quick Deploy Commands

If you need to update your repository later:

```bash
# Make changes to your code
git add .
git commit -m "Update: description of changes"
git push origin main
```

Both Railway and Vercel will automatically redeploy when you push changes.

## 🔧 Repository Configuration

### Files Updated for PrivateSearch:
- `README.md` - Updated branding and description
- `package.json` - Updated project name
- `pyproject.toml` - Updated project metadata
- `src/server/app.py` - Updated API title and descriptions
- `.gitignore` - Added deployment-specific ignores

### Deployment Files Added:
- `vercel.json` - Vercel deployment configuration
- `railway.toml` - Railway deployment configuration
- `DEPLOYMENT.md` - Complete deployment guide
- `VERCEL_DEPLOYMENT.md` - Quick deployment guide
- Environment templates for production

## 🆘 Troubleshooting

**Git not found**: Install Git from [git-scm.com](https://git-scm.com/)

**Permission denied**: Make sure you're signed into GitHub and have repository access

**Push rejected**: The repository might already have content. Try:
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

**Large files**: If you get warnings about large files, they'll still upload but consider using Git LFS for files >100MB

## ✅ Success Checklist

- [ ] GitHub repository created
- [ ] Code pushed to repository
- [ ] All deployment files present
- [ ] Ready to deploy to Railway
- [ ] Ready to deploy to Vercel

## 📖 What's Next?

After your repository is set up:

1. **Follow [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)** for quick deployment
2. **Or follow [DEPLOYMENT.md](DEPLOYMENT.md)** for detailed instructions
3. **Configure your API keys** (Tavily, OpenAI, etc.)
4. **Test your deployment** with the health check endpoints

Your PrivateSearch platform will be live and ready to use!
