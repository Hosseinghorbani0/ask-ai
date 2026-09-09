import os
import sys
import platform
import subprocess
import tempfile
import base64
import hashlib
import struct
import logging
import atexit
from pathlib import Path
from io import BytesIO
from typing import Union, Tuple, Dict, Any, Optional, BinaryIO, TypeVar, Type

# Setup structured logger for the media library
logger = logging.getLogger("media_engine")
logger.addHandler(logging.NullHandler())

# Type variable for fluent builder pattern methods
T = TypeVar("T", bound="MediaObject")


class MediaError(Exception):
    """Base exception class for media processing and playback errors."""
    pass


class MediaFormatError(MediaError):
    """Raised when media data format is invalid or corrupted."""
    pass


class MediaPlaybackError(MediaError):
    """Raised when cross-platform media playback fails."""
    pass


class TempFileManager:
    """Tracks and safely cleans up temporary media files upon process exit."""
    _tracked_files: set = set()

    @classmethod
    def create_temp_file(cls, data: bytes, suffix: str) -> Path:
        """Creates a temporary file, registers it for cleanup, and writes bytes."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(data)
                temp_path = Path(temp_file.name)
                cls._tracked_files.add(temp_path)
                return temp_path
        except Exception as e:
            raise MediaError(f"Failed to create temporary file: {e}") from e

    @classmethod
    def cleanup(cls) -> None:
        """Removes all registered temporary files from disk."""
        for path in list(cls._tracked_files):
            try:
                if path.exists():
                    path.unlink()
                cls._tracked_files.remove(path)
            except Exception as e:
                logger.debug(f"Could not remove temp file '{path}': {e}")


# Register automatic temp file cleanup at application exit
atexit.register(TempFileManager.cleanup)


class HeaderInspector:
    """Inspects magic byte headers to accurately detect media formats and MIME types."""

    @staticmethod
    def detect_type(data: bytes) -> Tuple[str, str, str]:
        """
        Detects (category, format, mime_type) from binary header signature.
        Returns ('generic', 'bin', 'application/octet-stream') if unrecognized.
        """
        if not data or len(data) < 4:
            return ("generic", "bin", "application/octet-stream")

        # Image Signatures
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return ("image", "png", "image/png")
        if data.startswith(b"\xff\xd8\xff"):
            return ("image", "jpg", "image/jpeg")
        if data.startswith((b"GIF87a", b"GIF89a")):
            return ("image", "gif", "image/gif")
        if data.startswith(b"BM"):
            return ("image", "bmp", "image/bmp")
        if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            return ("image", "webp", "image/webp")

        # Audio Signatures
        if data.startswith(b"RIFF") and data[8:12] == b"WAVE":
            return ("audio", "wav", "audio/wav")
        if data.startswith(b"ID3") or (len(data) > 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
            return ("audio", "mp3", "audio/mpeg")
        if data.startswith(b"OggS"):
            return ("audio", "ogg", "audio/ogg")
        if data.startswith(b"fLaC"):
            return ("audio", "flac", "audio/flac")

        # Video Signatures
        if len(data) >= 12 and data[4:8] == b"ftyp":
            return ("video", "mp4", "video/mp4")
        if data.startswith(b"\x1a\x45\xdf\xa3"):
            return ("video", "webm", "video/webm")

        return ("generic", "bin", "application/octet-stream")


class ImageHeaderParser:
    """Extracts image dimensions directly from binary header chunks."""

    @staticmethod
    def parse_dimensions(data: bytes, image_format: str) -> Tuple[Optional[int], Optional[int]]:
        """Extracts (width, height) without requiring external dependencies like Pillow."""
        try:
            if image_format == "png" and len(data) >= 24:
                w, h = struct.unpack(">II", data[16:24])
                return w, h
            elif image_format == "gif" and len(data) >= 10:
                w, h = struct.unpack("<HH", data[6:10])
                return w, h
            elif image_format == "bmp" and len(data) >= 26:
                w, h = struct.unpack("<ii", data[18:26])
                return w, abs(h)
            elif image_format == "jpg":
                # Scan JPEG segments for SOF0/SOF2 frame header
                idx = 2
                while idx < len(data) - 9:
                    if data[idx] != 0xFF:
                        idx += 1
                        continue
                    marker = data[idx + 1]
                    if marker in (0xC0, 0xC1, 0xC2, 0xC3):  # Start of Frame
                        h, w = struct.unpack(">HH", data[idx + 5:idx + 9])
                        return w, h
                    length = struct.unpack(">H", data[idx + 2:idx + 4])[0]
                    idx += 2 + length
        except Exception as e:
            logger.debug(f"Header dimensions parsing failed: {e}")
        return None, None


class AudioHeaderParser:
    """Parses audio metadata (duration, sample rate, channels) from raw audio frames."""

    @staticmethod
    def parse_wav_info(data: bytes) -> Dict[str, Any]:
        """Extracts duration, channels, and sample rate from WAV header."""
        info = {"duration": None, "sample_rate": None, "channels": None}
        try:
            if data.startswith(b"RIFF") and data[8:12] == b"WAVE" and len(data) >= 44:
                channels = struct.unpack("<H", data[22:24])[0]
                sample_rate = struct.unpack("<I", data[24:28])[0]
                byte_rate = struct.unpack("<I", data[28:32])[0]
                
                info["channels"] = channels
                info["sample_rate"] = sample_rate
                
                if byte_rate > 0:
                    info["duration"] = round(len(data) / byte_rate, 2)
        except Exception as e:
            logger.debug(f"WAV header parsing failed: {e}")
        return info


class MediaObject:
    """
    Enterprise base class representing immutable binary media payload.
    Provides memory-efficient byte handling, hash fingerprints, and serialization.
    """

    def __init__(self, data: Union[bytes, bytearray], media_type: str = "generic", mime_type: Optional[str] = None):
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f"Media data must be bytes or bytearray, got {type(data).__name__}")
        
        if len(data) == 0:
            raise ValueError("Media data payload cannot be empty.")

        self._data = bytes(data)
        self._media_type = media_type

        # Auto-detect category, format, and mime if missing
        cat, fmt, auto_mime = HeaderInspector.detect_type(self._data)
        self._format = fmt
        self._mime_type = mime_type or auto_mime

    @property
    def bytes(self) -> bytes:
        """Returns the raw binary media payload."""
        return self._data

    @property
    def size(self) -> int:
        """Returns size of the media object in bytes."""
        return len(self._data)

    @property
    def format(self) -> str:
        """Returns detected file extension/format (e.g., 'png', 'mp3')."""
        return self._format

    @property
    def mime_type(self) -> str:
        """Returns the MIME type string (e.g., 'image/png')."""
        return self._mime_type

    @property
    def md5(self) -> str:
        """Calculates MD5 hash fingerprint of the media data."""
        return hashlib.md5(self._data).hexdigest()

    @property
    def sha256(self) -> str:
        """Calculates SHA256 cryptographic hash of the media data."""
        return hashlib.sha256(self._data).hexdigest()

    def save(self, destination: Union[str, Path, BinaryIO]) -> Path:
        """
        Saves media payload to a file path or binary stream.
        
        Args:
            destination: File path (str/Path) or writeable binary stream object.
        Returns:
            Path object pointing to saved location, or Path('stream') if saved to IO.
        """
        try:
            if hasattr(destination, "write"):
                destination.write(self._data)
                destination.flush()
                return Path("stream")
            
            out_path = Path(destination).expanduser().resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(out_path, "wb") as f:
                f.write(self._data)
            return out_path
        except Exception as e:
            raise MediaError(f"Failed to save media payload to '{destination}': {e}") from e

    def to_base64(self) -> str:
        """Encodes media payload as a Base64 string."""
        return base64.b64encode(self._data).decode("utf-8")

    def to_data_uri(self) -> str:
        """Generates an inline Data URI (e.g. data:image/png;base64,...)."""
        return f"data:{self._mime_type};base64,{self.to_base64()}"

    @classmethod
    def from_file(cls: Type[T], path: Union[str, Path]) -> T:
        """Constructs a MediaObject instance from a local file path."""
        file_path = Path(path).expanduser().resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"Media file not found: {file_path}")
        with open(file_path, "rb") as f:
            data = f.read()
        return cls(data)

    @classmethod
    def from_base64(cls: Type[T], base64_str: str) -> T:
        """Constructs a MediaObject instance from a Base64 string or Data URI."""
        clean_b64 = base64_str
        if "," in base64_str:
            clean_b64 = base64_str.split(",", 1)[1]
        decoded_bytes = base64.b64decode(clean_b64)
        return cls(decoded_bytes)

    def __len__(self) -> int:
        return len(self._data)

    def __bytes__(self) -> bytes:
        return self._data

    def __bool__(self) -> bool:
        return len(self._data) > 0

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MediaObject):
            return self.sha256 == other.sha256
        return False

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} format='{self._format}' "
            f"mime='{self._mime_type}' size={len(self._data)} bytes "
            f"sha256='{self.sha256[:8]}...'>"
        )


class ImageObject(MediaObject):
    """Represents image media with dimension parsing, PIL and NumPy interoperability."""

    def __init__(self, data: Union[bytes, bytearray], format_hint: Optional[str] = None):
        super().__init__(data, media_type="image")
        if format_hint:
            self._format = format_hint.lower().strip(".")

        # Extract dimensions directly from raw header
        self._width, self._height = ImageHeaderParser.parse_dimensions(self._data, self._format)

    @property
    def dimensions(self) -> Tuple[Optional[int], Optional[int]]:
        """Returns (width, height) tuple if dimensions are available."""
        if self._width is None or self._height is None:
            # Fallback to PIL if binary header inspection missed it
            try:
                pil_img = self.to_pil()
                self._width, self._height = pil_img.size
            except Exception:
                pass
        return self._width, self._height

    @property
    def width(self) -> Optional[int]:
        """Returns image width in pixels."""
        return self.dimensions[0]

    @property
    def height(self) -> Optional[int]:
        """Returns image height in pixels."""
        return self.dimensions[1]

    def to_pil(self):
        """Converts raw image bytes to a Pillow Image object."""
        try:
            from PIL import Image
            return Image.open(BytesIO(self._data))
        except ImportError:
            raise MediaError("Pillow is not installed. Install via `pip install Pillow` to use to_pil().")
        except Exception as e:
            raise MediaFormatError(f"Failed to decode image data into PIL: {e}") from e

    def to_numpy(self):
        """Converts image bytes to a NumPy RGB array."""
        try:
            import numpy as np
            pil_img = self.to_pil().convert("RGB")
            return np.array(pil_img)
        except ImportError:
            raise MediaError("NumPy is not installed. Install via `pip install numpy` to use to_numpy().")

    def show((self) -> None:
        """Displays the image using Pillow UI or default OS application viewer."""
        try:
            pil_img = self.to_pil()
            pil_img.show()
        except Exception:
            # Fallback to native OS handler via temporary file
            suffix = f".{self._format}" if self._format != "bin" else ".png"
            temp_path = TempFileManager.create_temp_file(self._data, suffix=suffix)
            _open_file_with_os(temp_path)

    def resize(self, width: int, height: int) -> "ImageObject":
        """Resizes image to target dimensions and returns a new ImageObject instance."""
        pil_img = self.to_pil()
        resized = pil_img.resize((width, height))
        output_buffer = BytesIO()
        save_format = self._format.upper() if self._format.lower() != "jpg" else "JPEG"
        resized.save(output_buffer, format=save_format)
        return ImageObject(output_buffer.getvalue(), format_hint=self._format)


class AudioObject(MediaObject):
    """Represents audio media with metadata extraction and cross-platform playback."""

    def __init__(self, data: Union[bytes, bytearray], format_hint: Optional[str] = None):
        super().__init__(data, media_type="audio")
        if format_hint:
            self._format = format_hint.lower().strip(".")

        self._duration: Optional[float] = None
        self._sample_rate: Optional[int] = None
        self._channels: Optional[int] = None

        if self._format == "wav":
            info = AudioHeaderParser.parse_wav_info(self._data)
            self._duration = info["duration"]
            self._sample_rate = info["sample_rate"]
            self._channels = info["channels"]

    @property
    def duration_seconds(self) -> Optional[float]:
        """Estimated audio duration in seconds."""
        return self._duration

    def play(self) -> None:
        """
        Plays the audio using cross-platform system audio playback engines.
        Supports native Windows winsound, macOS afplay, Linux aplay/paplay, or system default.
        """
        suffix = f".{self._format}"
        temp_path = TempFileManager.create_temp_file(self._data, suffix=suffix)
        sys_name = platform.system()

        try:
            # 1. Native Windows WAV Playback via winsound
            if sys_name == "Windows" and self._format == "wav":
                import winsound
                winsound.PlaySound(str(temp_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                return

            # 2. macOS Playback via afplay
            if sys_name == "Darwin":
                subprocess.Popen(["afplay", str(temp_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return

            # 3. Linux Playback via aplay/paplay/pw-play
            if sys_name == "Linux":
                for player in ["paplay", "pw-play", "aplay", "ffplay"]:
                    if _is_command_available(player):
                        args = [player, str(temp_path)]
                        if player == "ffplay":
                            args.extend(["-nodisp", "-autoexit"])
                        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return

            # 4. Fallback to OS default application
            _open_file_with_os(temp_path)

        except Exception as e:
            raise MediaPlaybackError(f"Audio playback failed for format '{self._format}': {e}") from e


class VideoObject(MediaObject):
    """Represents video media with playback capabilities."""

    def __init__(self, data: Union[bytes, bytearray], format_hint: Optional[str] = None):
        super().__init__(data, media_type="video")
        if format_hint:
            self._format = format_hint.lower().strip(".")

    def play(self) -> None:
        """Plays video using system default video player."""
        suffix = f".{self._format}"
        temp_path = TempFileManager.create_temp_file(self._data, suffix=suffix)
        _open_file_with_os(temp_path)


def _is_command_available(cmd: str) -> bool:
    """Checks if a command-line utility exists on the current system PATH."""
    from shutil import which
    return which(cmd) is not None


def _open_file_with_os(path: Path) -> None:
    """Opens a file path using the native OS default application handler."""
    str_path = str(path)
    try:
        sys_name = platform.system()
        if sys_name == "Windows":
            os.startfile(str_path)
        elif sys_name == "Darwin":
            subprocess.Popen(["open", str_path])
        else:
            subprocess.Popen(["xdg-open", str_path])
    except Exception as e:
        raise MediaError(f"Could not open file '{path}' with system default application: {e}") from e
