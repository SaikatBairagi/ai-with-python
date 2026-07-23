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


def list_commits(
    repository: str,
    branch: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    Return recent commits from a GitHub repository.

    Args:
        owner: GitHub username or organization.
        repository: Repository name.
        branch: Optional branch name, tag, or commit SHA.
        limit: Number of commits to return, between 1 and 100.
    """

    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repository}/commits"

    params = {
        "per_page": limit,
    }

    if branch:
        params["sha"] = branch

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    commits = response.json()

    result = []

    for commit_item in commits:
        commit_details = commit_item["commit"]

        author_details = commit_details.get("author") or {}
        github_author = commit_item.get("author") or {}

        result.append(
            {
                "sha": commit_item["sha"],
                "short_sha": commit_item["sha"][:7],
                "message": commit_details["message"],
                "author_name": author_details.get("name"),
                "author_email": author_details.get("email"),
                "github_username": github_author.get("login"),
                "committed_at": author_details.get("date"),
                "url": commit_item["html_url"],
            }
        )

    return result


def list_repository_files(
    repository: str,
    path: str = "",
    branch: str | None = None,
) -> list[dict]:
    """
    Return files and directories from a GitHub repository path.

    Args:
        owner: GitHub username or organization.
        repository: Repository name.
        path: Directory path. Use an empty string for repository root.
        branch: Optional branch, tag, or commit SHA.
    """

    cleaned_path = path.strip("/")

    if cleaned_path:
        url = (
            f"https://api.github.com/repos/"
            f"{GITHUB_OWNER}/{repository}/contents/{cleaned_path}"
        )
    else:
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repository}/contents"

    params = {}

    if branch:
        params["ref"] = branch

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    items = response.json()

    if not isinstance(items, list):
        raise ValueError(f"The path '{path}' points to a file, not a directory.")

    result = []

    for item in items:
        result.append(
            {
                "name": item["name"],
                "path": item["path"],
                "type": item["type"],
                "size": item.get("size"),
                "sha": item.get("sha"),
                "url": item.get("html_url"),
                "download_url": item.get("download_url"),
            }
        )
    print(json.dumps(result, indent=4))
    return result


# print(json.dumps(list_repository_files("ai-with-python"), indent=4))
