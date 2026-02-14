# How to Deploy on Render — Step by Step

## Step 1: Push Your Code to GitHub

1. Open **GitHub** ([github.com](https://github.com)) and sign in.
2. Click the **+** icon → **New repository**.
3. Name it (e.g. `smart-campus-issues`), leave other options default, click **Create repository**.
4. Open your project folder in the terminal and run:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username and `YOUR_REPO_NAME` with the repository name.

---

## Step 2: Sign Up on Render

1. Go to [render.com](https://render.com).
2. Click **Get Started for Free**.
3. Sign up with **GitHub** (recommended so Render can access your repos).

---

## Step 3: Create a New Web Service

1. On the Render dashboard, click **New +**.
2. Click **Web Service**.
3. Under **Connect a repository**, find your project and click **Connect** next to it.
4. If you don’t see it, click **Configure account** and give Render access to the repo.

---

## Step 4: Configure the Service

Fill in these fields:

| Field | Value |
|-------|--------|
| **Name** | `smart-campus-issues` (or any name) |
| **Region** | Choose the closest to your users |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT app:app` |

---

## Step 5: Add Environment Variables

1. Scroll to **Environment Variables**.
2. Click **Add Environment Variable**.
3. Add:
   - **Key:** `SECRET_KEY`
   - **Value:** a long random string (e.g. generate one at [randomkeygen.com](https://randomkeygen.com))

---

## Step 6: Deploy

1. Click **Create Web Service**.
2. Render will build and deploy your app (often 2–5 minutes).
3. When the build completes, you’ll see a URL like: `https://smart-campus-issues-xxxx.onrender.com`

---

## Step 7: Use Your App

1. Open the URL in your browser.
2. You should see the Smart Campus login page.
3. **Admin:** `admin@campus.edu` / `admin123`
4. **Students:** create an account with **Sign up**.

---

## Summary Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created and repo connected
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `gunicorn --bind 0.0.0.0:$PORT app:app`
- [ ] `SECRET_KEY` set in Environment Variables
- [ ] Click **Create Web Service** and wait for the build to finish

---

## Troubleshooting

**Build fails**
- Check the build logs in the Render dashboard.
- Ensure `requirements.txt` and all files are in the repo.

**App crashes or shows 503**
- Check the **Logs** tab on Render.
- Confirm the start command is exactly: `gunicorn --bind 0.0.0.0:$PORT app:app`

**Data or images disappear**
- On Render, the disk is temporary. Data can be lost on restart.
- For real production, you’d add a PostgreSQL database and cloud storage for images.
