#!/bin/bash

# DeerFlow Deployment Helper Script
# This script helps prepare your DeerFlow project for deployment

set -e

echo "🦌 DeerFlow Deployment Helper"
echo "=============================="

# Check if required files exist
echo "📋 Checking required files..."

if [ ! -f ".env.example" ]; then
    echo "❌ .env.example not found"
    exit 1
fi

if [ ! -f "conf.yaml.example" ]; then
    echo "❌ conf.yaml.example not found"
    exit 1
fi

echo "✅ Required files found"

# Check if production environment files exist
echo "🔧 Checking production configuration..."

if [ ! -f ".env.production" ]; then
    echo "⚠️  .env.production not found (this is normal for first-time setup)"
else
    echo "✅ .env.production found"
fi

if [ ! -f "web/.env.production" ]; then
    echo "⚠️  web/.env.production not found (this is normal for first-time setup)"
else
    echo "✅ web/.env.production found"
fi

# Check if configuration files are set up
echo "⚙️  Checking configuration..."

if [ ! -f ".env" ]; then
    echo "⚠️  .env not found. Please copy .env.example to .env and configure it."
    echo "   cp .env.example .env"
else
    echo "✅ .env found"
fi

if [ ! -f "conf.yaml" ]; then
    echo "⚠️  conf.yaml not found. Please copy conf.yaml.example to conf.yaml and configure it."
    echo "   cp conf.yaml.example conf.yaml"
else
    echo "✅ conf.yaml found"
fi

# Check if web dependencies are installed
echo "📦 Checking web dependencies..."

if [ ! -d "web/node_modules" ]; then
    echo "⚠️  Web dependencies not installed. Installing..."
    cd web
    if command -v pnpm &> /dev/null; then
        pnpm install
    elif command -v npm &> /dev/null; then
        npm install
    else
        echo "❌ Neither pnpm nor npm found. Please install Node.js and pnpm."
        exit 1
    fi
    cd ..
    echo "✅ Web dependencies installed"
else
    echo "✅ Web dependencies found"
fi

# Check if Python dependencies are installed
echo "🐍 Checking Python dependencies..."

if command -v uv &> /dev/null; then
    echo "✅ uv found"
    if [ ! -d ".venv" ]; then
        echo "⚠️  Virtual environment not found. Creating..."
        uv sync
        echo "✅ Virtual environment created"
    else
        echo "✅ Virtual environment found"
    fi
else
    echo "⚠️  uv not found. Please install uv: https://docs.astral.sh/uv/getting-started/installation/"
fi

echo ""
echo "🚀 Deployment Checklist:"
echo "========================"
echo ""
echo "Backend (Railway):"
echo "  1. ✅ railway.toml configuration file created"
echo "  2. ✅ Health check endpoint added"
echo "  3. ✅ CORS configuration updated"
echo "  4. ✅ Production environment template created"
echo "  5. 📝 Configure environment variables in Railway dashboard"
echo "  6. 📝 Deploy to Railway from GitHub"
echo ""
echo "Frontend (Vercel):"
echo "  1. ✅ vercel.json configuration file created"
echo "  2. ✅ Production environment template created"
echo "  3. 📝 Set root directory to 'web' in Vercel"
echo "  4. 📝 Configure NEXT_PUBLIC_API_URL in Vercel dashboard"
echo "  5. 📝 Deploy to Vercel from GitHub"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo ""
echo "🔑 Required Environment Variables:"
echo "   - TAVILY_API_KEY (for search)"
echo "   - OpenAI/LLM API keys (for AI models)"
echo "   - FRONTEND_URL (Railway - your Vercel URL)"
echo "   - NEXT_PUBLIC_API_URL (Vercel - your Railway URL)"
echo ""
echo "✨ Ready for deployment! Follow the DEPLOYMENT.md guide."
