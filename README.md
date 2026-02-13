# ReqGen - AI Document Generator

![ReqGen Dashboard](client/public/favicon.png)

A comprehensive requirement generation tool powered by AI.

---

## 🚀 One-Click Deployment

### Step 1: Deploy Backend (Login & Database)

Click the button below to deploy the Node.js backend to Koyeb for free:

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=prajwal-kadam12/ReqGen-Vercel&branch=main&name=reqgen-backend&env[NODE_ENV]=production&env[PYTHON_BACKEND_URL]=https%3A%2F%2Fprajwalk12-reqgen-api.hf.space)

**Instructions:**
1. Click the button above.
2. Sign in to Koyeb (GitHub).
3. Review the settings (Environment variables are pre-filled!).
4. Click **"Deploy"**.
5. Copy the **App URL** (e.g., `https://reqgen-backend.koyeb.app`) once it's healthy.

---

### Step 2: Connect Frontend

1. Open your code locally.
2. Open `vercel.json`.
3. Replace `YOUR-KOYEB-APP-URL` with your new Koyeb URL.
4. Run:
   ```bash
   git add vercel.json
   git commit -m "Update backend URL"
   git push
   ```

---

## Features

- **AI Audio Transcription**: Powered by OpenAI Whisper
- **Requirement Refinement**: Powered by T5 Large
- **Document Generation**: Automatic BRD/PO creation
- **Speech-to-Text**: Vakyansh integration
- **Google Login**: Secure authentication

## Tech Stack

- **Frontend**: React + Vite + Tailwind (Deployed on Vercel)
- **Backend (API)**: Express + Node.js (Deployed on Koyeb)
- **AI Engine**: Python (Deployed on Hugging Face Spaces)
