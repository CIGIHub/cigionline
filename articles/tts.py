import io
import boto3
from pydub import AudioSegment
from textwrap import wrap
import os
from django.conf import settings

# safe limit for NTTS and SSML text
POLLY_CHAR_LIMIT = 3000
AWS_REGION = getattr(settings, 'AWS_REGION_NAME', None) or os.getenv('AWS_REGION_NAME')


def chunk_text(text: str, limit: int = POLLY_CHAR_LIMIT):
    # Simple chunker on sentence-ish boundaries
    parts = []
    buf = []
    size = 0
    for piece in wrap(text, width=1000, break_long_words=False, replace_whitespace=False):
        if size + len(piece) + 1 > limit:
            parts.append(' '.join(buf))
            buf = [piece]
            size = len(piece) + 1
        else:
            buf.append(piece)
            size += len(piece) + 1
    if buf:
        parts.append(' '.join(buf))
    return [p.strip() for p in parts if p.strip()]


def synthesize_chunk(polly_client, text, voice_id='Joanna', use_ssml=False, format='mp3'):
    kwargs = {
        'OutputFormat': format,
        'VoiceId': voice_id,
    }
    if use_ssml:
        kwargs['TextType'] = 'ssml'
        kwargs['Text'] = f'<speak>{text}</speak>'
    else:
        kwargs['Text'] = text

    resp = polly_client.synthesize_speech(**kwargs)
    audio_bytes = resp['AudioStream'].read()
    return AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)


def synthesize_full_mp3(text, voice_id='Joanna', use_ssml=False):
    polly = boto3.client('polly', region_name=AWS_REGION)
    chunks = chunk_text(text)
    combined = None
    for i, ch in enumerate(chunks):
        seg = synthesize_chunk(polly, ch, voice_id=voice_id, use_ssml=use_ssml, format='mp3')
        combined = seg if combined is None else (combined + seg)
    # Export to MP3 bytes
    out = io.BytesIO()
    combined.export(out, format='mp3')  # uses ffmpeg
    out.seek(0)
    return out.getvalue()
