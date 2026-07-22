from openai import OpenAI
from dotenv import load_dotenv

import json
import github_api


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
]

# Initializeing tool list
TOOLS_LIST = {
    "get_repository_by_user": github_api.get_repository_by_user,
    "get_repository_details": github_api.get_repository_details,
    "list_branches": github_api.list_branches,
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


def chat() -> None:
    """A minimal terminal REPL. conversation_memory is the agent's entire
    memory -- a plain list, grown by run_agent() on every turn.
    """
    messages: list[dict] = []
    print("Type a question (Ctrl+C to quit).")

    while True:
        try:
            user_input = input("You: ")
        except KeyboardInterrupt, EOFError:
            print("\nExiting.")
            break

        messages.append({"role": "user", "content": user_input})
        answer = run_agent(messages)
        print(f"Agent: {answer}\n")


if __name__ == "__main__":
    chat()
