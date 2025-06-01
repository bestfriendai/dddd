# DeerFlow Deployment Guide

This guide will help you deploy DeerFlow using a hybrid approach with Vercel for the frontend and Railway for the backend.

## Architecture Overview

- **Frontend**: Next.js app deployed on Vercel
- **Backend**: Python FastAPI server deployed on Railway
- **Communication**: Frontend communicates with backend via API calls

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **API Keys**: Obtain necessary API keys (Tavily, OpenAI, etc.)
4. **GitHub Repository**: Fork or clone this repository to your GitHub account

## Step 1: Deploy Backend to Railway

### 1.1 Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your DeerFlow repository
5. Railway will automatically detect the `railway.toml` configuration

### 1.2 Configure Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add:

```bash
# Required
APP_ENV=production
SEARCH_API=tavily
TAVILY_API_KEY=your_tavily_api_key_here

# Your LLM configuration (copy from conf.yaml)
# Add your model configuration as environment variables
# Example for OpenAI:
OPENAI_API_KEY=your_openai_key_here

# Optional but recommended
FRONTEND_URL=https://your-app.vercel.app
JINA_API_KEY=your_jina_api_key_here

# Optional: TTS for podcast generation
VOLCENGINE_TTS_APPID=your_volcengine_appid
VOLCENGINE_TTS_ACCESS_TOKEN=your_volcengine_token

# Optional: LangSmith tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=your_project_name
```

### 1.3 Deploy

1. Railway will automatically build and deploy your backend
2. Note the deployment URL (e.g., `https://your-app.railway.app`)
3. Test the health endpoint: `https://your-app.railway.app/api/health`

## Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Project

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your DeerFlow repository
4. Vercel will automatically detect it's a Next.js project

### 2.2 Configure Build Settings

1. **Root Directory**: Set to `web`
2. **Build Command**: `pnpm run build`
3. **Output Directory**: `.next`
4. **Install Command**: `pnpm install`

### 2.3 Configure Environment Variables

In your Vercel project dashboard, go to "Settings" > "Environment Variables" and add:

```bash
# Required: Point to your Railway backend
NEXT_PUBLIC_API_URL=https://your-app.railway.app/api

# Optional
NEXT_TELEMETRY_DISABLED=1
AMPLITUDE_API_KEY=your_amplitude_key_here
GITHUB_OAUTH_TOKEN=your_github_token_here
```

### 2.4 Deploy

1. Click "Deploy" in Vercel
2. Vercel will build and deploy your frontend
3. Note your deployment URL (e.g., `https://your-app.vercel.app`)

## Step 3: Update CORS Configuration

### 3.1 Update Railway Environment Variables

Go back to your Railway project and update the `FRONTEND_URL` variable:

```bash
FRONTEND_URL=https://your-actual-vercel-app.vercel.app
```

### 3.2 Redeploy Railway

Railway will automatically redeploy with the updated CORS configuration.

## Step 4: Configure LLM Models

### 4.1 Create conf.yaml

You need to configure your LLM models. Create a `conf.yaml` file based on `conf.yaml.example`:

```yaml
BASIC_MODEL:
  base_url: https://api.openai.com/v1
  model: "gpt-4"
  api_key: your_openai_api_key_here
```

### 4.2 Environment Variables Alternative

Instead of `conf.yaml`, you can use environment variables in Railway:

```bash
BASIC_MODEL_BASE_URL=https://api.openai.com/v1
BASIC_MODEL_MODEL=gpt-4
BASIC_MODEL_API_KEY=your_openai_api_key_here
```

## Step 5: Test Deployment

1. Visit your Vercel URL
2. Try creating a research query
3. Check that the frontend communicates with the Railway backend
4. Monitor logs in both Vercel and Railway dashboards

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure `FRONTEND_URL` is correctly set in Railway
2. **API Connection Failed**: Verify `NEXT_PUBLIC_API_URL` in Vercel
3. **Build Failures**: Check build logs in respective platforms
4. **Missing API Keys**: Ensure all required environment variables are set

### Debugging

1. **Railway Logs**: Check the "Deployments" tab in Railway
2. **Vercel Logs**: Check the "Functions" tab in Vercel
3. **Health Check**: Test `https://your-app.railway.app/api/health`

## Optional Enhancements

### Custom Domain

1. **Vercel**: Add custom domain in project settings
2. **Railway**: Add custom domain in project settings
3. Update CORS configuration accordingly

### Monitoring

1. Enable LangSmith tracing for AI workflow monitoring
2. Set up Vercel Analytics for frontend monitoring
3. Use Railway metrics for backend monitoring

## Security Considerations

1. **Environment Variables**: Never commit API keys to version control
2. **CORS**: Use specific domains instead of wildcards in production
3. **Rate Limiting**: Consider implementing rate limiting for API endpoints
4. **Authentication**: Add authentication if needed for your use case

## Cost Optimization

1. **Railway**: Monitor usage and consider upgrading plan if needed
2. **Vercel**: Optimize build times and function execution
3. **API Calls**: Monitor LLM API usage and costs

## Support

If you encounter issues:

1. Check the [FAQ](docs/FAQ.md)
2. Review the [Configuration Guide](docs/configuration_guide.md)
3. Open an issue on GitHub
4. Check Railway and Vercel documentation
