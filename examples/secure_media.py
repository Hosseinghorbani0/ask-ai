from ask_ai import MediaPolicy, download_media

policy = MediaPolicy(
    max_bytes=10 * 1024 * 1024,
    allowed_mime_types={"image/png"},
    allowed_hosts={"example.com"},
)
image_bytes = download_media("https://example.com/image.png", policy)
print(f"Downloaded {len(image_bytes)} bytes")
