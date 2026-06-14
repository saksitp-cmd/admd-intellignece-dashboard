# Phuket Travel Intelligence Dashboard

Streamlit dashboard for weekly tourism intelligence monitoring for Phuket / Andamanda Phuket.

## Files

- `app.py` - Streamlit dashboard
- `requirements.txt` - Python dependencies
- `.streamlit/secrets.toml.example` - template for Streamlit Secrets

## Deploy on Streamlit Community Cloud

1. Upload `app.py` and `requirements.txt` to a GitHub repository.
2. Go to Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. In Streamlit Cloud, open:
   App > Settings > Secrets
5. Paste your API keys using the format in `.streamlit/secrets.toml.example`.
6. Deploy the app.

Do not commit real API keys to GitHub.
