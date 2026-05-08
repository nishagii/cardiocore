from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)

client = OpenAI(
    base_url=os.getenv("GEMMA_BASE_URL"),
    api_key="not-needed"
)

MODEL_NAME = os.getenv("MODEL_NAME")


def ask_gemma(
    prompt: str,
    max_tokens: int = 300,
    temperature: float = 0.2
) -> str:
    """
    Send a prompt to Gemma and return the response text.
    """

    try:
        logging.info("Sending request to Gemma")

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )

        content = response.choices[0].message.content

        logging.info("Gemma response received")

        return content

    except Exception as e:
        logging.error(f"Gemma request failed: {e}")
        raise
