from dotenv import load_dotenv
import os
import requests

load_dotenv()

headers = {
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    "Accept": "application/vnd.github+json",
}

response = requests.get(
    "https://api.github.com/user",
    headers=headers,
)

print(response.status_code)
print(response.json()["login"])
