# 🚀 Vercel Deployment Guide - ReqGen

## Pre-requisites
1. ✅ Hugging Face Space URL ready (Python backend)
2. ✅ GitHub account
3. ✅ Vercel account (free at https://vercel.com)

---

## Step 1: Update Hugging Face URL

Open `vercel.json` and replace `YOUR-HUGGINGFACE-SPACE-URL` with your actual Hugging Face Space URL:

```json
{
  "rewrites": [
    {
      "source": "/api/python/:path*",
      "destination": "https://prajwal-reqgen.hf.space/api/:path*"
    }
  ]
}
```

**Example**: If your HF Space is `https://prajwal-reqgen.hf.space`, use that URL.

---

## Step 2: Push Code to GitHub

```bash
# Navigate to project folder
cd "c:\Users\USER\Downloads\reqgen Original"

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Vercel deployment ready"

# Add remote (create repo on GitHub first)
git remote add origin https://github.com/YOUR-USERNAME/reqgen.git

# Push
git push -u origin main
```

---

## Step 3: Deploy on Vercel

### Option A: Vercel Dashboard (Easiest)
1. Go to https://vercel.com/new
2. Click "Import Project"
3. Select your GitHub repo
4. Configure:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist/public`
   - **Install Command**: `npm install`
5. Click **Deploy**

### Option B: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

---

## Step 4: Configure Environment Variables (if needed)

In Vercel Dashboard → Your Project → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `NODE_ENV` | `production` |

---

## How It Works

```
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│                 │        │                 │        │                 │
│   Vercel        │  ───►  │   /api/python/* │  ───►  │  Hugging Face   │
│   (Frontend)    │        │   (Proxy)       │        │  (Python AI)    │
│                 │        │                 │        │                 │
└─────────────────┘        └─────────────────┘        └─────────────────┘
```

1. **Frontend** hosted on Vercel (React/Vite)
2. **API calls** to `/api/python/*` are proxied to Hugging Face Space
3. **Audio processing** runs on Hugging Face (16GB RAM, free!)

---

## Troubleshooting

### Error: "Cannot find module '@replit/...'"
✅ Already fixed! We removed Replit plugins from vite.config.ts

### Error: "API calls failing (404 or CORS)"
- Check if Hugging Face Space is running
- Verify URL in `vercel.json` is correct
- Make sure HF Space URL ends with `.hf.space`

### Error: "Build failed"
Run locally first to verify:
```bash
npm install
npm run build
```

---

## Support

- Vercel Docs: https://vercel.com/docs
- Hugging Face Spaces: https://huggingface.co/docs/hub/spaces

**Your app will be live at**: `https://your-project.vercel.app`

---

## Files Modified for Vercel

1. ✅ `vercel.json` - Vercel configuration with API proxy
2. ✅ `vite.config.ts` - Removed Replit-specific plugins
3. ✅ `.vercelignore` - Exclude unnecessary files from deployment
