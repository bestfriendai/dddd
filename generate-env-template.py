#!/usr/bin/env python3
"""
Generate environment variable templates for deployment platforms.
"""

import sys
from pathlib import Path

def generate_railway_env():
    """Generate Railway environment variables template."""
    template = """# Copy these environment variables to your Railway project dashboard
# Go to your Railway project > Variables tab and add these:

# Required - Application Configuration
APP_ENV=production
DEBUG=False
AGENT_RECURSION_LIMIT=30

# Required - Search API (choose one)
SEARCH_API=tavily
TAVILY_API_KEY=your_tavily_api_key_here
# BRAVE_SEARCH_API_KEY=your_brave_api_key_here

# Required - LLM Configuration (example for OpenAI)
OPENAI_API_KEY=your_openai_api_key_here

# Required - CORS Configuration (update with your Vercel URL)
FRONTEND_URL=https://your-app.vercel.app

# Optional - Additional APIs
JINA_API_KEY=your_jina_api_key_here

# Optional - TTS for Podcast Generation
VOLCENGINE_TTS_APPID=your_volcengine_appid
VOLCENGINE_TTS_ACCESS_TOKEN=your_volcengine_token

# Optional - LangSmith Tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=your_project_name

# Optional - RAG Provider
RAG_PROVIDER=ragflow
RAGFLOW_API_URL=http://localhost:9388
RAGFLOW_API_KEY=ragflow-xxx
RAGFLOW_RETRIEVAL_SIZE=10

# System Configuration (Railway will set PORT automatically)
PYTHONUNBUFFERED=1
UV_SYSTEM_PYTHON=1
"""
    return template

def generate_vercel_env():
    """Generate Vercel environment variables template."""
    template = """# Copy these environment variables to your Vercel project dashboard
# Go to your Vercel project > Settings > Environment Variables and add these:

# Required - API URL (update with your Railway URL)
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app/api

# Optional - Analytics
AMPLITUDE_API_KEY=your_amplitude_key

# Optional - GitHub Integration
GITHUB_OAUTH_TOKEN=your_github_token

# System Configuration
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
"""
    return template

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['railway', 'vercel']:
        print("Usage: python generate-env-template.py [railway|vercel]")
        print("  railway - Generate Railway environment variables")
        print("  vercel  - Generate Vercel environment variables")
        sys.exit(1)
    
    platform = sys.argv[1]
    
    if platform == 'railway':
        print("🚂 Railway Environment Variables Template")
        print("=" * 50)
        print(generate_railway_env())
        
        # Save to file
        with open('railway-env-template.txt', 'w') as f:
            f.write(generate_railway_env())
        print(f"\n💾 Template saved to: railway-env-template.txt")
        
    elif platform == 'vercel':
        print("▲ Vercel Environment Variables Template")
        print("=" * 50)
        print(generate_vercel_env())
        
        # Save to file
        with open('vercel-env-template.txt', 'w') as f:
            f.write(generate_vercel_env())
        print(f"\n💾 Template saved to: vercel-env-template.txt")

if __name__ == "__main__":
    main()
