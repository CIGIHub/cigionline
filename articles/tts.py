import io
import boto3
from pydub import AudioSegment
from textwrap import wrap
import os
from django.conf import settings
from django.utils.html import strip_tags
import re


POLLY_CHAR_LIMIT = 3000
AWS_REGION = getattr(settings, 'AWS_REGION_NAME', None) or os.getenv('AWS_REGION_NAME')


def extract_title_text(page):
    return (getattr(page, 'title', '') or '').strip()


def extract_meta_text(page):
    subtitle = (getattr(page, 'subtitle', '') or '').strip()

    authors = getattr(page, 'authors', None)
    if authors:
        names = [a.author.title for a in authors.all()]
        if names:
            if len(names) == 1:
                authors_text = f'By {names[0]}'
            else:
                authors_text = f'By {', '.join(names[:-1])} and {names[-1]}'
    return strip_tags(f'{subtitle} {authors_text}')


def _block_html_to_text_with_para_spaces(html):
    if html:
        # Normalize paragraph boundaries and line breaks before stripping tags
        # Ensure a separator after closing </p>, and treat <br> as a soft break.
        html = re.sub(r'(?is)</p\s*>', '</p>\n', html)      # mark paragraph ends
        html = re.sub(r'(?is)<br\s*/?>', '\n', html)        # line breaks → newline

        text = strip_tags(html)

        # Split into paragraphs/lines, keep non-empty ones
        paragraphs = [p.strip() for p in re.split(r'\n+', text) if p.strip()]
        if paragraphs:
            pieces = []
            for p in paragraphs:
                if not p.endswith(' '):
                    p = p + ' '
                pieces.append(p)

        # Collapse any internal runs of whitespace except the deliberate trailing space
        block_text = re.sub(r'\s+', ' ', ''.join(pieces))
        return block_text


def extract_body_text(page):
    parts = []
    body_text = []

    if getattr(page, 'body', None):
        for block in page.body:
            val = getattr(block, 'value', None)
            html = None
            if isinstance(val, str):
                html = val
            elif hasattr(val, 'source'):   # RichText
                html = val.source
            elif hasattr(val, 'get') and val.get('text'):
                html = val.get('text')
            if html:
                block_text = _block_html_to_text_with_para_spaces(html)
                if block_text:
                    body_text.append(block_text)

    if body_text:
        body_clean = re.sub(r'\s+', ' ', ' '.join(body_text)).strip()
        parts.append(body_clean)

    print(' '.join(p.strip() for p in parts if p and p.strip()))
    return ' '.join(p.strip() for p in parts if p and p.strip())


def chunk_text(text: str, limit: int = POLLY_CHAR_LIMIT):
    # Split on ~1000-char wraps to stay under limit
    out, buf, size = [], [], 0
    for piece in wrap(text, width=1000, break_long_words=False, replace_whitespace=False):
        if size + len(piece) + 1 > limit:
            out.append(' '.join(buf))
            buf, size = [piece], len(piece) + 1
        else:
            buf.append(piece)
            size += len(piece) + 1
    if buf:
        out.append(' '.join(buf))
    return [c.strip() for c in out if c.strip()]


def synthesize_chunk(polly_client, text, voice_id='Joanna', use_ssml=False, format='mp3'):
    resp = polly_client.synthesize_speech(
        Text=text,
        OutputFormat=format,
        VoiceId=voice_id
    )
    audio_bytes = resp['AudioStream'].read()
    return AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)


def synthesize_plain_with_title_pause(page, voice_id='Joanna', title_pause_ms=800):
    # Plain-text synthesis with a precise silence inserted right after the title.
    polly = boto3.client('polly', region_name=AWS_REGION)
    title_text = extract_title_text(page)
    meta_text = extract_meta_text(page)
    body_text = extract_body_text(page)
    combined = None

    # 1) request title
    if title_text:
        title_seg = synthesize_chunk(polly, title_text, voice_id=voice_id, format='mp3')
        combined = title_seg
        # Insert exact silence after title
        if title_pause_ms and title_pause_ms > 0:
            combined += AudioSegment.silent(duration=int(title_pause_ms))

    # 2) request meta
    if meta_text:
        meta_seg = synthesize_chunk(polly, meta_text, voice_id=voice_id, format='mp3')
        combined = meta_seg if combined is None else (combined + meta_seg)
        if title_pause_ms and title_pause_ms > 0:
            combined += AudioSegment.silent(duration=int(title_pause_ms))

    # 3) request body
    if body_text:
        for ch in chunk_text(body_text):
            seg = synthesize_chunk(polly, ch, voice_id=voice_id, format='mp3')
            combined = seg if combined is None else (combined + seg)

    out = io.BytesIO()
    combined.export(out, format='mp3')
    out.seek(0)
    return out.getvalue()
