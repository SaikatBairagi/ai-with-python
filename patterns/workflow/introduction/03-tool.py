from openai import OpenAI
from dotenv import load_dotenv
import requests
import json

# Load Environment
load_dotenv()

# Initialize OpenAI
client = OpenAI()

# -----------------------------
# Declare weather function
# -----------------------------


def get_weather(latitude, longitude):
    """This is a publically available API that returns the weather for a given location."""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]


def call_function(name, args):
    print("********** Inside the call_function *********")
    if name == "get_weather":
        return get_weather(**args)


# --------------------------------------------------------------
# Step 1: Call model with get_weather tool defined
# --------------------------------------------------------------

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

system_prompt = "You are a helpful weather assistant."

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What's the weather like in Toronto today?"},
]

# -----------------------------
# Calling the Model
# ----------------------------
response = client.responses.create(model="gpt-3.5-turbo", input=messages, tools=tools)

messages += response.output

for item in response.output:
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

print("Final input:")
print(messages)

response = client.responses.create(
    model="gpt-5.6",
    instructions="Response only when Tool gives response",
    tools=tools,
    input=messages,
)

# 5. The model should be able to give a response!
print("Final output:")
print(response.model_dump_json(indent=2))
print("\n" + response.output_text)
