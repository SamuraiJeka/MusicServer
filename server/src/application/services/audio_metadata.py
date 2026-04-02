from mutagen.mp3 import MP3
from io import BytesIO
from datetime import timedelta


def get_mp3_duration(content: bytes) -> timedelta:
    audio = MP3(BytesIO(content))
    return timedelta(seconds=int(audio.info.length))
