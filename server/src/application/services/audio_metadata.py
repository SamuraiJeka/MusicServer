from mutagen.mp3 import MP3
from io import BytesIO
from datetime import timedelta


def get_mp3_duration(content: bytes) -> timedelta | None:
    audio = MP3(BytesIO(content))
    length = getattr(audio.info, "length", None)
    if length is None:
        return None
    return timedelta(seconds=int(length))
