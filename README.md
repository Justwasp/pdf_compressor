PDF Compressor
==============

This is a small Streamlit app that compresses PDFs and can also convert uploaded JPEG/PNG images to a one-page PDF and compress them.

Requirements
------------
- Python 3.8+
- See `requirements.txt` (Streamlit, PyMuPDF, Pillow)

How to run locally
------------------
1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run main.py
```

Deploy to Streamlit Cloud
-------------------------
1. Make sure this repository is pushed to GitHub (already done).
2. Go to https://share.streamlit.io and sign in with your GitHub account.
3. Click "New app" → select the `Justwasp/pdf_compressor` repository, branch `main`, and the file `main.py`.
4. Click "Deploy". Streamlit Cloud will install dependencies from `requirements.txt` and launch the app.

Notes & tips
------------
- If the app fails to start on Streamlit Cloud because of package installation errors, check the `requirements.txt` versions and adjust as needed.
- If you need private env vars (API keys etc.), add them in the Streamlit Cloud repository settings (Secrets).
- To preserve color instead of grayscale in compression, edit `compress_pdf_bytes()` in `main.py` and remove `.convert("L")`.

If you'd like, I can also:
- Create a tiny GitHub Actions workflow to run lint/tests on push.
- Add a `.streamlit/config.toml` for app-level config (e.g., enable CORS, set headless server options).
- Directly create the Streamlit app from the repo if you grant access or walk through your Streamlit Cloud dashboard with me.

