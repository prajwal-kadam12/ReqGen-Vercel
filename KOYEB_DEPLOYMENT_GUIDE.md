# 🚀 Final Step: Deploy Node.js Backend to Koyeb

Since you need the `Login` and `Database` features, you must deploy the Node.js backend. We will use **Koyeb** (Free & Reliable).

---

## Step 1: Push Code to GitHub (Important)

Run these commands in your terminal:

```bash
git add .
git commit -m "Ready for Koyeb deployment"
git push
```

---

## Step 2: Deploy on Koyeb

1. **Sign up/Login**: Go to [https://app.koyeb.com/](https://app.koyeb.com/)
2. **Create App**:
   - Click **Create Web Service**
   - Select **GitHub** as source
   - Choose your repository: `prajwal-kadam12/ReqGen-Vercel`
   - Branch: `main`
3. **Configure Builder**:
   - Builder: **Dockerfile** (it will auto-detect the Dockerfile we created)
4. **Environment Variables** (Add these):
   - `NODE_ENV` = `production`
   - `PYTHON_BACKEND_URL` = `https://prajwalk12-reqgen-api.hf.space`
5. **Instance Size**:
   - Select **Free** (Nano)
6. **Click Deploy** 🚀

---

## Step 3: Connect Vercel to Koyeb

1. Once Koyeb deployment finishes, copy your **Public App URL** (e.g., `https://reqgen-backend-prajwal.koyeb.app`).
2. Open `vercel.json` in your local code.
3. Replace the placeholder with your **actual Koyeb URL**:

```json
"destination": "https://YOUR-KOYEB-NAME.koyeb.app/api/:path*"
```
*(Make sure to keep `/api/:path*` at the end)*

4. **Update Vercel**:
```bash
git add vercel.json
git commit -m "Linked Vercel to Koyeb backend"
git push
```

---

## 🎉 Done!
- **Frontend**: Vercel
- **Backend (Login/API)**: Koyeb
- **AI Engine**: Hugging Face

Now everything will work, including Login, Document Generation, and Audio Processing!
