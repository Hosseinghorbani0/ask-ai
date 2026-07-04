import os
import platform
import subprocess
import tempfile
from typing import Optional


class MediaObject:
    """Base class for media objects (image, audio)."""

    def __init__(self, data: bytes, media_type: str):
        self.data = data
        self.type = media_type

    @property
    def bytes(self) -> bytes:
        return self.data

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} size={len(self.data)} bytes>"


class ImageObject(MediaObject):
    """Represents a generated image."""

    def __init__(self, data: bytes):
        super().__init__(data, "image")

    def save(self, path: str) -> None:
        """Save the image to a file."""
        with open(path, "wb") as f:
            f.write(self.data)

    def show(self) -> None:
        """Display the image using the default OS viewer."""
        try:
            from PIL import Image
            from io import BytesIO
            image = Image.open(BytesIO(self.data))
            image.show()
        except ImportError:
            # Fallback: save to temp and open with OS
            self._open_with_os(".png")
        except Exception as e:
            raise RuntimeError(f"Error showing image: {e}") from e

    def _open_with_os(self, suffix: str) -> None:
        """Open a temp file with the OS default handler."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(self.data)
            temp_path = f.name
        _open_file(temp_path)


class AudioObject(MediaObject):
    """Represents generated audio."""

    def __init__(self, data: bytes, format: str = "mp3"):
        super().__init__(data, "audio")
        self.format = format

    def save(self, path: str) -> None:
        """Save the audio to a file."""
        with open(path, "wb") as f:
            f.write(self.data)

    def play(self) -> None:
        """Play the audio using the default OS player."""
        suffix = f".{self.format}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(self.data)
            temp_path = f.name
        _open_file(temp_path)


def _open_file(path: str) -> None:
    """Cross-platform file opener."""
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        raise RuntimeError(f"Could not open file '{path}': {e}") from e
