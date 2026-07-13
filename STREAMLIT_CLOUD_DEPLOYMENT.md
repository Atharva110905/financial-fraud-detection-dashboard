# 🚀 Streamlit Cloud Deployment Guide

## Deploying to Streamlit Cloud

This fraud detection dashboard can be deployed to **Streamlit Community Cloud** for free hosting and instant sharing.

### What You Need
- A GitHub repository with the fraud detection project
- A Streamlit Community Cloud account (https://streamlit.io/cloud)

### Steps to Deploy

#### 1️⃣ Push to GitHub
```bash
git init
git add .
git commit -m "Initial fraud detection dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### 2️⃣ Connect to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your GitHub repository and branch (main)
4. Set main file to `app.py`
5. Click "Deploy"

#### 3️⃣ Wait for Deployment
The app will start installing dependencies and building. First deployment takes ~2-3 minutes.

---

## ⚠️ Important: TensorFlow Removed for Cloud

The **Autoencoder deep learning model has been removed** from this deployment because:

- ❌ TensorFlow-cpu has no wheels for Python 3.14+ (used by Streamlit Cloud)
- ❌ Autoencoder was the weakest performer (94.11% accuracy)
- ✅ Other 6 models work perfectly (XGBoost/LightGBM: 99.5% accuracy)

### Models Now Deployed (6 Total)
🔵 **Supervised** — Logistic Regression, Random Forest, XGBoost, LightGBM  
🟡 **Unsupervised** — Isolation Forest, One-Class SVM

**No functionality lost** — the remaining models still cover supervised, unsupervised, and comparison analysis.

---

## 📊 Expected Behavior

- **First load**: 30-60 seconds (data caching)
- **Model switching**: Instant (models pre-trained, loaded from artifacts/)
- **Predictions**: <1 second per transaction batch

---

## 🔧 Troubleshooting

### "App is not responding"
→ Streamlit Cloud can timeout on large operations. Try:
- Refresh the page
- Reduce the number of alerts shown (Transaction Investigator tab)
- Wait for cache to warm up on first load

### "No such file or directory: fraud_detection.db"
→ The database is included in the repo. If it's missing:
```bash
python generate_dataset.py
python etl_pipeline.py
git add fraud_detection.db
git commit -m "Add fraud detection database"
git push
```

### Dashboard runs locally but not on Cloud
→ Check the logs (Cloud → App menu → Logs). Most common issues:
- Missing Python package (check requirements.txt)
- File path issue (use relative paths, not C:\Users\...)
- Memory limit (keep dataset under 100MB)

---

## 💡 Local Development vs Cloud

**Local (Your Computer)**
- Fastest performance
- Full control of environment
- Can use TensorFlow/Autoencoder
- Accessible only at http://localhost:8501

**Streamlit Cloud**
- Free hosting 24/7
- Shareable link (share.streamlit.io)
- Auto-deploys on git push
- Limited to 1GB RAM, Python 3.14+

---

## 📝 Environment Files

**requirements.txt** — Dependencies for Cloud (TensorFlow removed)  
**.streamlit/config.toml** — Streamlit Cloud settings (theme, toolbar, etc.)

---

## 🎯 Next Steps

After deployment, share the live link with your team:

```
https://share.streamlit.io/YOUR_USERNAME/YOUR_REPO/main/app.py
```

No installation needed — just visit the link and explore!

---

## 📞 Support

- Streamlit Cloud Issues: https://docs.streamlit.io/
- Project Issues: Check app logs via Streamlit Cloud dashboard
- Local Testing: Use `streamlit run app.py` locally before pushing to Cloud
