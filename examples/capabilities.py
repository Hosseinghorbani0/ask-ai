from ask_ai import OpenAI

capabilities = OpenAI(api_key="not-used-for-this-example").capabilities()
for name, supported in capabilities.to_dict().items():
    print(f"{name}: {supported}")
