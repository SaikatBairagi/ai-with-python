from openai import OpenAI
from dotenv import load_dotenv

import json
import github_api
import streamlit as st


# Load Environment
load_dotenv()

# Initialize OpenAI
client = OpenAI()

# Creating tools metadata
tools = [
    {
        "type": "function",
        "name": "get_repository_by_user",
        "description": "Retrieve all GitHub repositories owned by the authenticated user. Returns the repository name, visibility, default branch, and GitHub URL.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "get_repository_details",
        "description": "Retrieve detailed information about a specific GitHub repository owned by the authenticated user.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the GitHub repository. Example: 'ai-with-python'.",
                }
            },
            "required": ["repo_name"],
        },
    },
    {
        "type": "function",
        "name": "list_branches",
        "description": "Retrieve all branches for a GitHub repository. Returns each branch name, latest commit SHA, and whether the branch is protected.",
        "parameters": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": "The name of the GitHub repository. Example: 'ai-with-python'.",
                }
            },
            "required": ["repository"],
        },
    },
    {
        "type": "function",
        "name": "list_commits",
        "description": (
            "List recent commits from a GitHub repository. "
            "Use this when the user asks about recent changes, "
            "commit history, authors, or the latest commit."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": "GitHub repository name.",
                },
                "branch": {
                    "type": ["string", "null"],
                    "description": (
                        "Optional branch name, tag, or commit SHA. "
                        "Use null to use the repository default branch."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of commits to return.",
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            "required": [
                "repository",
                "branch",
                "limit",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_repository_files",
        "description": (
            "List files and folders in a GitHub repository directory. "
            "Use an empty path to list the repository root."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": "GitHub repository name.",
                },
                "path": {
                    "type": "string",
                    "description": (
                        "Directory path inside the repository. "
                        "Use an empty string for the root directory."
                    ),
                },
                "branch": {
                    "type": ["string", "null"],
                    "description": (
                        "Optional branch, tag, or commit SHA. "
                        "Use null for the default branch."
                    ),
                },
            },
            "required": [
                "repository",
                "path",
                "branch",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

# Initializeing tool list
TOOLS_LIST = {
    "get_repository_by_user": github_api.get_repository_by_user,
    "get_repository_details": github_api.get_repository_details,
    "list_branches": github_api.list_branches,
    "list_commits": github_api.list_commits,
    "list_repository_files": github_api.list_repository_files,
}


def call_function(name, args):
    print("********** Inside call_function *********")
    func = TOOLS_LIST.get(name)
    if func is None:
        raise ValueError(f"Unknown tool: {name}")
    return func(**args)


def run_agent(messages: list[dict], max_turns: int = 4) -> str:
    for _ in range(max_turns):
        response = client.responses.create(
            model="gpt-5.6-sol", input=messages, tools=tools
        )
        # ---------------------------------
        # Printing messages
        # ---------------------------------
        print("Printing messages:")
        print(messages)
        messages += response.output

        # ---------------------------------
        # Loop through the Optput of LLM
        # to check if this is a tool call or response
        # ---------------------------------

        for item in response.output:
            print("------ Printing the output [] ------")
            print(item)
            if item.type == "function_call":
                name = item.name
                args = json.loads(item.arguments)
                result = call_function(name, args)
                messages.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result),
                    }
                )
            elif item.type == "message":
                return response.output_text
    return "Decision not achieved in this iteration!!!"


# ---------- Streamlit frontend ----------

st.set_page_config(
    page_title="Project Zero Agent",
    page_icon="🤖",
)

st.title("Project Zero Agent")
st.caption("Weather agent")


# Only user/assistant text displayed on screen
if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []


# Full OpenAI conversation, including tool calls
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous user and assistant messages
for message in st.session_state.ui_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


user_input = st.chat_input("Ask about the weather...")


if user_input:
    # Add user message to UI history
    st.session_state.ui_messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    # Add user message to OpenAI conversation
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = run_agent(st.session_state.messages)

        st.write(answer)

    # Save assistant answer for future Streamlit reruns
    st.session_state.ui_messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
