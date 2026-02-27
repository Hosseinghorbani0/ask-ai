import os

target_dir = "docs"
print(f"Updating documentation in {target_dir}...")

for filename in os.listdir(target_dir):
    if filename.endswith(".md"):
        path = os.path.join(target_dir, filename)
        print(f"Processing {filename}...")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Update Branding/Pip name
        new_content = content.replace("ask-ai", "askai-python")

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

print("Documentation update complete.")
