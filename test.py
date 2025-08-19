# test_rotation.py
from app.ai_client import _next_api_key, API_KEYS

print("All API keys:", API_KEYS)
print("Testing rotation:")

for i in range(5):
    key = _next_api_key()
    print(f"Call {i+1}: Using key -> {key}")
