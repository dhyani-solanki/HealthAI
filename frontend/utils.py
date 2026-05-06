import requests
import streamlit as st

BASE_URL = "http://localhost:8000"


def get_auth_header() -> dict:
    """Returns JWT auth header from session state"""
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def api_post(endpoint: str, data: dict = None, authenticated: bool = True):
    headers = get_auth_header() if authenticated else {}
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers=headers,
            timeout=120  # MediGenius can take time
        )
        return response
    except requests.exceptions.ConnectionError:
        return None
def api_post(endpoint: str, data: dict = None, authenticated: bool = True, files=None):
    headers = get_auth_header() if authenticated else {}
    try:
        if files:
            # For file uploads, don't set Content-Type (requests sets multipart automatically)
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                files=files,
                headers=headers,
                timeout=120
            )
        else:
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json=data,
                headers=headers,
                timeout=120
            )
        return response
    except requests.exceptions.ConnectionError:
        return None

def api_get(endpoint: str, authenticated: bool = True):
    headers = get_auth_header() if authenticated else {}
    try:
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            timeout=30
        )
        return response
    except requests.exceptions.ConnectionError:
        return None


def api_put(endpoint: str, data: dict = None, authenticated: bool = True):
    headers = get_auth_header() if authenticated else {}
    try:
        response = requests.put(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers=headers,
            timeout=30
        )
        return response
    except requests.exceptions.ConnectionError:
        return None


def api_delete(endpoint: str, authenticated: bool = True):
    headers = get_auth_header() if authenticated else {}
    try:
        response = requests.delete(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            timeout=30
        )
        return response
    except requests.exceptions.ConnectionError:
        return None


def is_logged_in() -> bool:
    return bool(st.session_state.get("access_token"))


def require_login():
    """Call at top of any protected page"""
    if not is_logged_in():
        st.warning("⚠️ Please login first!")
        st.stop()


def handle_response_error(response):
    """Handle common API errors"""
    if response is None:
        st.error("❌ Cannot connect to server. Is the backend running?")
        return True
    if response.status_code == 401:
        st.error("⏰ Session expired. Please login again.")
        st.session_state.access_token = None
        st.session_state.user_name = None
        st.rerun()
        return True
    if response.status_code >= 400:
        detail = response.json().get("detail", "Something went wrong")
        st.error(f"❌ {detail}")
        return True
    return False