# app/auth.py
import os
from flask import request, jsonify
from functools import wraps

API_KEY = os.environ.get("API_KEY", "mysecretkey")

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get("X-API-Key") != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
