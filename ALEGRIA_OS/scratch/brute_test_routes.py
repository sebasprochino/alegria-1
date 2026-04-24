import requests

urls = [
    "http://127.0.0.1:8000/api/developer/agent-chat",
    "http://127.0.0.1:8000/developer/agent-chat",
    "http://127.0.0.1:8000/api/developer/chat",
    "http://127.0.0.1:8000/developer/chat"
]

payload = {"messages": [{"role": "user", "content": "test"}], "mode": "chat"}

for url in urls:
    try:
        response = requests.post(url, json=payload, timeout=2)
        print(f"URL: {url} -> Status: {response.status_code}")
        if response.status_code != 404:
            print(f"Response: {response.text[:100]}")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
