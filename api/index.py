import os
import sys

# Ensure backend package is importable when Vercel runs from repo root
BACKEND_DIR = os.path.join(os.getcwd(), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Import the FastAPI `app` object from the existing backend without
# duplicating routes or logic.
from app.main import app  # noqa: E402, F401

# Vercel's Python runtime will use the ASGI `app` variable directly.
from backend.app.main import app

# Vercel serverless entry point for the FastAPI app.
# The imported app object is the same one used locally.
