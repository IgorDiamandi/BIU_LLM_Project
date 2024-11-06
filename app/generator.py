import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_response(query, context_chunks):
    context = " ".join(context_chunks)
    prompt = f"Based on the following context: {context}\nAnswer the following query: {query}"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()
