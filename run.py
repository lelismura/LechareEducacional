# run.py
import os, sys, uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    # se existir a variável PORT (no Cloud Run), usa ela
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    reload = not bool(os.environ.get("PORT"))  # reload só em local

    uvicorn.run("app.main:app", host=host, port=port, reload=reload)