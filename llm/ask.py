import sys
from google import genai
from llm.helpers import get_api_key

MODEL_NAME = "gemini-3.5-flash-lite"


def main():
    if len(sys.argv) < 3:
        print("Usage: python -m llm.ask a <text>")
        sys.exit(1)

    command = sys.argv[1]
    text = sys.argv[2]

    if command != "a":
        print(f"Unknown command: {command}. Only 'a' is supported currently.")
        sys.exit(1)

    try:
        api_key = get_api_key()
    except ValueError as e:
        print(e)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=text,
    )
    print(response.text)


if __name__ == "__main__":
    main()
