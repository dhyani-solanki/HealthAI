import requests
import streamlit as st

BASE_URL = "http://localhost:8000"


def get_headers():
    token = st.session_state.get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


def signup(name: str, email: str, password: str):
    r = requests.post(f"{BASE_URL}/auth/signup", json={"name": name, "email": email, "password": password})
    return r.json(), r.status_code


def login(email: str, password: str):
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    return r.json(), r.status_code


def get_health_record():
    r = requests.get(f"{BASE_URL}/health/record", headers=get_headers())
    return r.json() if r.ok else None


def save_health_record(data: dict):
    r = requests.post(f"{BASE_URL}/health/record", json=data, headers=get_headers())
    return r.json(), r.status_code


def get_family_history():
    r = requests.get(f"{BASE_URL}/health/family-history", headers=get_headers())
    return r.json() if r.ok else []


def add_family_history(data: dict):
    r = requests.post(f"{BASE_URL}/health/family-history", json=data, headers=get_headers())
    return r.json(), r.status_code


def delete_family_history(entry_id: int):
    r = requests.delete(f"{BASE_URL}/health/family-history/{entry_id}", headers=get_headers())
    return r.ok


def get_reminders():
    r = requests.get(f"{BASE_URL}/reminders/", headers=get_headers())
    return r.json() if r.ok else []


def add_reminder(data: dict):
    r = requests.post(f"{BASE_URL}/reminders/", json=data, headers=get_headers())
    return r.json(), r.status_code


def delete_reminder(reminder_id: int):
    r = requests.delete(f"{BASE_URL}/reminders/{reminder_id}", headers=get_headers())
    return r.ok


def chat_medigenius(message: str):
    r = requests.post(f"{BASE_URL}/ai/chat", json={"message": message}, headers=get_headers())
    return r.json(), r.status_code


def get_chat_history():
    r = requests.get(f"{BASE_URL}/ai/chat/history", headers=get_headers())
    return r.json() if r.ok else []


def mediscan_by_name(medicine_name: str):
    r = requests.post(f"{BASE_URL}/ai/mediscan/text?medicine_name={medicine_name}", headers=get_headers())
    return r.json(), r.status_code


def mediscan_by_image(image_file):
    files = {"file": (image_file.name, image_file, image_file.type)}
    r = requests.post(f"{BASE_URL}/ai/mediscan/image", files=files, headers=get_headers())
    return r.json(), r.status_code
