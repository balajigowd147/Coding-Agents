import os
import sys
from google import genai
from google.genai import types
from google.genai import errors
from pydantic import ValidationError
from llm.helpers import (
    get_api_key,
    get_prompt_with_today,
    get_prompt_c_with_today,
    IntermediateExpense,
    parse_expense_response,
    monthly_summary,
)

MODEL_NAME = "gemini-3.5-flash-lite"
TOOLS = [monthly_summary]


def call_gemini(prompt: str, schema) -> str:
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )
    return response.text


def call_gemini_with_tools(prompt: str, tools) -> str:
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        tools=tools,
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )
    return response.text


def handle_b(text: str):
    prompt = f"{get_prompt_with_today(text)}\n\nAmount must be in rupees as a number."
    response_text = call_gemini(prompt, IntermediateExpense)
    expense = parse_expense_response(response_text)
    print(expense.model_dump_json())


def handle_c(text: str):
    prompt = f"{get_prompt_c_with_today(text)}\n\nAmounts are in paise (100 paise = 1 rupee) and answers must be in rupees."
    response_text = call_gemini_with_tools(prompt, TOOLS)
    print(response_text)


def main():
    if len(sys.argv) < 3:
        print("Usage: python -m llm.ask <a|b|c> <text>")
        sys.exit(1)

    command = sys.argv[1]
    text = sys.argv[2]

    if command not in ("a", "b", "c"):
        print(f"Unknown command: {command}. Only 'a', 'b', and 'c' are supported currently.")
        sys.exit(1)

    try:
        api_key = get_api_key()
    except ValueError as e:
        print(e)
        sys.exit(1)

    try:
        if command == "a":
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=text,
            )
            print(response.text)
        elif command == "b":
            handle_b(text)
        elif command == "c":
            handle_c(text)
    except errors.APIError as e:
        msg = getattr(e, "message", None) or str(e)
        api_key_val = os.environ.get("GEMINI_API_KEY")
        if api_key_val and api_key_val in msg:
            msg = msg.replace(api_key_val, "[REDACTED]")
        print(f"Gemini request failed: {msg}")
        sys.exit(1)
    except ValidationError as e:
        first_msg = e.errors()[0]["msg"] if e.errors() else str(e)
        print(f"Invalid expense: {first_msg}")
        sys.exit(1)
    except ValueError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
