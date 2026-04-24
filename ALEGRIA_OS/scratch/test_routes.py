import requests

url = "http://127.0.0.1:8000/anima/chat"
payload = {"content": "hola"}
try:
    response = requests.post(url, json=payload)
    print(f"Anima /chat status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")

url_dev = "http://127.0.0.1:8000/api/developer/agent-chat"
payload_dev = {"messages": [], "mode": "chat"}
try:
    response = requests.post(url_dev, json=payload_dev)
    print(f"Dev /agent-chat status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
