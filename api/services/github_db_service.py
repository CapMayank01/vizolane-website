import os
import base64
import requests
import json
from datetime import datetime

def write_to_github_db(data):
    repo = os.getenv("GITHUB_DB_REPO")
    token = os.getenv("GITHUB_DB_TOKEN")
    
    if not repo or not token:
        print("[WARNING] GITHUB_DB_REPO or GITHUB_DB_TOKEN not set - skipping GitHub DB write.")
        return False
        
    # Generate filename based on timestamp for perfect descending sorting
    timestamp_prefix = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{timestamp_prefix}.json"
    
    url = f"https://api.github.com/repos/{repo}/contents/submissions/{filename}"
    
    # Payload matches the contact form structure + default status "New"
    payload = {
        "name": data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone") or "N/A",
        "message": data.get("message"),
        "timestamp": datetime.now().strftime("%d/%m/%Y, %I:%M:%S %p"),
        "status": "New"
    }
    
    content_bytes = json.dumps(payload, indent=2).encode("utf-8")
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Vizolane-Website-App"
    }
    
    req_body = {
        "message": f"Add contact submission from {data.get('name')}",
        "content": content_b64
    }
    
    try:
        res = requests.put(url, headers=headers, json=req_body)
        if res.status_code in [200, 201]:
            print(f"[SUCCESS] Submission written to GitHub DB: {filename}")
            return True
        else:
            print(f"[ERROR] Failed to write to GitHub DB: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"[ERROR] GitHub DB write exception: {e}")
        return False
