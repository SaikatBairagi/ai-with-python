from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

import json

# load .env file
load_dotenv()

# create OPENAI client
client = OpenAI()


# --------------------------------------------------------------
# Step 1: Define the response format in a Pydantic model
# --------------------------------------------------------------


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


# ---------------------------------------------
# Check if the event is valid
# ---------------------------------------------


def is_empty_event(event):
    return event.name == "" and event.date == "" and len(event.participants) == 0


response = client.responses.parse(
    model="gpt-5.6",
    input=[
        {"role": "system", "content": "Extract the event information."},
        {
            "role": "user",
            "content": "My favourite color is blue",
        },
    ],
    text_format=CalendarEvent,
)

print(json.dumps(response.model_dump(), indent=2))
print(type(response.output_parsed))
event = response.output_parsed
print(is_empty_event(event))
