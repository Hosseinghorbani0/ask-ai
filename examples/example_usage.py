from ask_ai import OpenAI

# Ultra-Simple Usage


def simple_demo():
    print("--- Simple Demo ---")
    # Tries to load OPENAI_API_KEY from env
    try:
        ai = OpenAI()
        response = ai.ask("Tell me a one-line joke.")
        print(f"AI: {response.text}")
    except Exception as e:
        print(f"Skipping simple demo: {e}")

# Advanced Usage with Config


def advanced_demo():
    print("\n--- Advanced Demo ---")
    try:
        ai = OpenAI()

        # 1. Set global settings (persistent)
        ai.advanced(temperature=0.7, system_message="You are a poetic assistant.")

        # 2. Ask with global settings
        print("Poem:")
        print(ai.ask("Explain recursion"))

        # 3. Override for one request
        print("\nFacts (Low Temp):")
        print(ai.ask("List 3 facts about Mars", temperature=0.1))

    except Exception as e:
        print(f"Skipping advanced demo: {e}")

# Media Generation (Smart Intent)


def media_demo():
    print("\n--- Media Demo ---")
    try:
        ai = OpenAI()

        # Image
        print("Requesting Image...")
        resp = ai.ask("Draw a pixel art heart")
        if resp.media:
            print(f"Image Generated: {resp.media.type}")
            resp.media.show()
            # resp.media.save("heart.png")
        else:
            print("Model returned text instead (maybe tool not called).")

    except Exception as e:
        print(f"Skipping media demo: {e}")


if __name__ == "__main__":
    # Ensure env var is set or pass api_key manually for testing
    # os.environ["OPENAI_API_KEY"] = "sk-..."

    simple_demo()
    advanced_demo()
    # media_demo() # Uncomment to test if you have credits/key
