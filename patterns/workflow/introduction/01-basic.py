from dotenv import load_dotenv
from openai import OpenAI

import json

# load .env file
load_dotenv()

# create OPENAI client
client = OpenAI()

# -------------------------------------------
# Used latest API of OpenAI
# Previous: client.chat.completions.create
# ------------------------------------------
response = client.responses.create(
    model="gpt-5.6",
    input=[
        {"role": "system", "content": "You're a helpful assistant."},
        {
            "role": "user",
            "content": "Write a limerick about the Python programming language.",
        },
    ],
)

print(json.dumps(response.model_dump(), indent=2))

# ----------------------------------------
# Used Open AI API method output_text()
# Previously used to do response parsing
# ---------------------------------------

print(response.output_text)
