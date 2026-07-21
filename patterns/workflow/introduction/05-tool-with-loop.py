from dotenv import load_dotenv
from openai import OpenAI

import requests
import json

# Loading environment
load_dotenv()

# Getting the Chat Client
client = OpenAI()

print(client)


# -----------------------------
# Declare weather function
# -----------------------------


def get_weather(latitude, longitude):
    """This is a publically available API that returns the weather for a given location."""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    # print("Output from get_weather:")
    # print(data)
    return data["current"]


def call_function(name, args):
    print("********** Inside the call_function *********")
    if name == "get_weather":
        return get_weather(**args)


tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a location using its latitude and longitude.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude of the location. Example: 48.8566 for Paris.",
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude of the location. Example: 2.3522 for Paris.",
                },
            },
            "required": ["latitude", "longitude"],
        },
    }
]

TOOLS_BY_NAME = {"get_weather": get_weather}


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

    print("Goodbye! \n\n\n")
    print(messages)


if __name__ == "__main__":
    chat()
