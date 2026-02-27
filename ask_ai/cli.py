import sys
import argparse
from . import (
    OpenAI,
    Groq,
    Google,
    OpenRouter,
    Azure,
    Anthropic,
    AskAIError
)


def main():
    parser = argparse.ArgumentParser(
        description="ask-ai CLI: Ask AI anything directly from your terminal."
    )
    parser.add_argument("query", help="The text query to ask the AI.")
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "groq", "google", "openrouter", "azure", "anthropic"],
        help="The AI provider to use."
    )
    parser.add_argument("--model", help="Specific model to use (optional).")
    parser.add_argument("--temp", type=float, help="Temperature setting (optional).")

    args = parser.parse_args()

    # Map provider name to class
    provider_map = {
        "openai": OpenAI,
        "groq": Groq,
        "google": Google,
        "openrouter": OpenRouter,
        "azure": Azure,
        "anthropic": Anthropic,
    }

    provider_class = provider_map.get(args.provider.lower())

    if not provider_class:
        print(f"Error: Provider '{args.provider}' not found.")
        sys.exit(1)

    try:
        # Init provider
        kwargs = {}
        if args.model:
            kwargs["model"] = args.model

        ai = provider_class(**kwargs)

        # Ask
        ask_kwargs = {}
        if args.temp is not None:
            ask_kwargs["temperature"] = args.temp

        print(f"[{args.provider.upper()}] Thinking...")
        response = ai.ask(args.query, **ask_kwargs)

        if response.media:
            print(f"Generated Media: {response.media.type}")
            response.media.show()
            # auto save to current directory?
            filename = f"output.{'png' if response.media.type == 'image' else 'mp3'}"
            response.media.save(filename)
            print(f"Saved to {filename}")
        else:
            print(response.text)

    except AskAIError as e:
        print(f"AskAI Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()
