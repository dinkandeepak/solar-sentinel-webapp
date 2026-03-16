# Solar Sentinel

Solar Sentinel includes:

- terminal runner (`main.py`)
- Streamlit webapp (`streamlit_app.py`)
- deployment files for Streamlit Cloud and container platforms

## Local Run

Terminal:

```bash
python main.py
```

Webapp:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Public Live URL (Temporary)

For quick public sharing from your local machine:

```bash
cloudflared tunnel --url http://localhost:8501 --no-autoupdate
```

This creates a temporary `trycloudflare.com` URL while your machine stays online.

## Permanent Deployment

### Option 1: Streamlit Community Cloud

1. Create a GitHub repo and upload this folder.
2. Open Streamlit Community Cloud and click **New app**.
3. Select repo/branch and set file path to `streamlit_app.py`.
4. Deploy.

If GitHub CLI auth is already configured on your machine, you can create/push a repo in one command:

```bash
powershell -ExecutionPolicy Bypass -File .\deploy.ps1 -RepoName solar-sentinel-webapp -Visibility public
```

### Option 2: Render/Railway/Fly (Docker)

This repo includes a `Dockerfile` that runs:

```bash
streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501
```

Deploy by connecting the repo and selecting Docker runtime.

## Project Layout

```text
solar_sentinel/
  __init__.py
  models.py
  engine.py
reporting/
  terminal.py
main.py
streamlit_app.py
requirements.txt
Dockerfile
Procfile
```
