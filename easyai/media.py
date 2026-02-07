import os
import base64
from PIL import Image
from io import BytesIO
import platform
import subprocess

class MediaObject:
    def __init__(self, data: bytes, media_type: str):
        self.data = data
        self.type = media_type

    @property
    def bytes(self) -> bytes:
        return self.data

class ImageObject(MediaObject):
    def __init__(self, data: bytes):
        super().__init__(data, "image")

    def save(self, path: str):
        """Save the image to a file."""
        with open(path, "wb") as f:
            f.write(self.data)
        print(f"Image saved to {path}")

    def show(self):
        """Display the image using the default OS viewer."""
        try:
            image = Image.open(BytesIO(self.data))
            image.show()
        except Exception as e:
            print(f"Error showing image: {e}")

class AudioObject(MediaObject):
    def __init__(self, data: bytes):
        super().__init__(data, "audio")

    def save(self, path: str):
        """Save the audio to a file."""
        with open(path, "wb") as f:
            f.write(self.data)
        print(f"Audio saved to {path}")

    def play(self):
        """Play the audio using the default OS player."""
        # Simple cross-platform play attempt
        import tempfile
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(self.data)
            temp_path = f.name
            
        try:
            if platform.system() == "Windows":
                 os.startfile(temp_path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", temp_path])
            else:
                subprocess.call(["xdg-open", temp_path])
        except Exception as e:
            print(f"Error playing audio: {e}")
