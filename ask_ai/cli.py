import sys
import argparse
from . import __version__
from . import (
    OpenAI,
    Groq,
    Google,
    OpenRouter,
    Azure,
    Anthropic,
    AskAIError
)


PROVIDER_MAP = {
    "openai": OpenAI,
    "groq": Groq,
    "google": Google,
    "openrouter": OpenRouter,
    "azure": Azure,
    "anthropic": Anthropic,
}


def main():
    parser = argparse.ArgumentParser(
        description="ask-ai CLI: Ask AI anything directly from your terminal."
    )
    parser.add_argument("query", nargs="?", help="The text query to ask the AI.")
    parser.add_argument(
        "--provider", "-p",
        default="openai",
        choices=list(PROVIDER_MAP.keys()),
        help="The AI provider to use (default: openai)."
    )
    parser.add_argument("--model", "-m", help="Specific model to use.")
    parser.add_argument("--temp", type=float, help="Temperature setting.")
    parser.add_argument("--system", "-s", help="System prompt.")
    parser.add_argument("--json", action="store_true", help="Request JSON output.")
    parser.add_argument("--stream", action="store_true", help="Enable streaming output.")
    parser.add_argument("--version", "-v", action="version", version=f"ask-ai {__version__}")

    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        sys.exit(0)

    provider_class = PROVIDER_MAP.get(args.provider.lower())
    if not provider_class:
        print(f"Error: Provider '{args.provider}' not found.")
        sys.exit(1)

    try:
        # Init provider
        init_kwargs = {}
        if args.model:
            init_kwargs["model"] = args.model

        ai = provider_class(**init_kwargs)

        # Build ask kwargs
        ask_kwargs = {}
        if args.temp is not None:
            ask_kwargs["temperature"] = args.temp
        if args.system:
            ask_kwargs["system_message"] = args.system
        if args.json:
            ask_kwargs["json"] = True

        # Stream or regular
        if args.stream:
            try:
                for chunk in ai.ask_stream(args.query, **ask_kwargs):
                    print(chunk, end="", flush=True)
                print()  # newline at end
            except Exception:
                # Fallback to non-streaming if provider doesn't support it
                response = ai.ask(args.query, **ask_kwargs)
                print(response.text)
        else:
            response = ai.ask(args.query, **ask_kwargs)

            if response.media:
                print(f"Generated Media: {response.media.type}")
                filename = f"output.{'png' if response.media.type == 'image' else 'mp3'}"
                response.media.save(filename)
                print(f"Saved to {filename}")
            elif args.json:
                import json
                print(json.dumps(response.json, indent=2, ensure_ascii=False))
            else:
                print(response.text)

    except AskAIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
