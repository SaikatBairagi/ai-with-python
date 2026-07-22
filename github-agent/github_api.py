from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

headers = {
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    "Accept": "application/vnd.github+json",
}

GITHUB_URL = "https://api.github.com/"
GITHUB_OWNER = os.environ["GITHUB_OWNER"]


# get all repository list
def get_repository_by_user():
    url = f"{GITHUB_URL}user/repos"
    response = requests.get(url, headers=headers)

    repositories = []

    for repo in response.json():
        repositories.append(
            {
                "name": repo["name"],
                "private": repo["private"],
                "default_branch": repo["default_branch"],
                "url": repo["html_url"],
            }
        )

    return repositories


# get a repository details
def get_repository_details(repo_name: str):
    url = f"{GITHUB_URL}repos/{GITHUB_OWNER}/{repo_name}"
    print(url)
    response = requests.get(url, headers=headers)

    repository = []

    repo = response.json()
    repository.append(
        {
            "name": repo["name"],
            "description": repo["description"],
            "forks_url": repo["forks_url"],
            "language": repo["language"],
            "created_at": repo["created_at"],
        }
    )

    return repository


def list_branches(repository: str) -> list[dict]:
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repository}/branches"

    response = requests.get(
        url,
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()

    branches = response.json()

    return [
        {
            "name": branch["name"],
            "commit_sha": branch["commit"]["sha"],
            "protected": branch["protected"],
        }
        for branch in branches
    ]


# print(json.dumps(list_branches("ai-with-python"), indent=4))
