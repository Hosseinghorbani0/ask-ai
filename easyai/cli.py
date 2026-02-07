import sys
import argparse
from .providers import OpenAI
from .exceptions import EasyAIError

def main():
    parser = argparse.ArgumentParser(description="easyai CLI: Ask AI anything directly from your terminal.")
    parser.add_argument("query", help="The text query to ask the AI.")
    parser.add_argument("--provider", default="openai", choices=["openai", "groq", "google", "openrouter", "azure", "anthropic"], help="The AI provider to use.")
    parser.add_argument("--model", help="Specific model to use (optional).")
    parser.add_argument("--temp", type=float, help="Temperature setting (optional).")
    
    args = parser.parse_args()

    # Map provider name to class
    providers = {
        "openai": OpenAI,
        # Lazy load others to avoid unnecessary imports if cli is used often? 
        # But we already imported OpenAI. 
        # Let's import dynamically or just map if already imported in __init__.
    }
    
    # We need to import others dynamically or statically. 
    # Since __init__ exposes them, let's use that.
    import easyai
    
    provider_class = getattr(easyai, args.provider.capitalize(), None)
    if args.provider == "openrouter": # naming case mismatch
        provider_class = easyai.OpenRouter
    elif args.provider == "openai":
         provider_class = easyai.OpenAI
    elif args.provider == "groq":
         provider_class = easyai.Groq
    elif args.provider == "google":
         provider_class = easyai.Google
    elif args.provider == "azure":
         provider_class = easyai.Azure
    elif args.provider == "anthropic":
         provider_class = easyai.Anthropic

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

    except EasyAIError as e:
        print(f"EasyAI Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    main()
