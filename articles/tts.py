import io
import boto3
from pydub import AudioSegment
from textwrap import wrap
import os
from django.conf import settings
from django.utils.html import strip_tags
from wagtail.rich_text import RichText
import re


POLLY_CHAR_LIMIT = 3000
AWS_REGION = getattr(settings, 'AWS_REGION_NAME', None) or os.getenv('AWS_REGION_NAME')
default_voice = getattr(settings, 'POLLY_DEFAULT_VOICE_ID', None) or os.getenv('POLLY_DEFAULT_VOICE_ID')

_TERMINALS = '.!?…'
_CLOSERS = '\'"”’»)]}'


def _ensure_terminal_punct(text, terminal_mark='.'):
    trimmed_text = text.rstrip()
    result_text = ''
    if trimmed_text:
        last_char = trimmed_text[-1]
        if last_char in _TERMINALS:
            result_text = trimmed_text
        elif last_char in _CLOSERS:
            scan_index = len(trimmed_text) - 1
            while scan_index >= 0 and trimmed_text[scan_index] in _CLOSERS + ' ':
                scan_index -= 1
            if scan_index >= 0 and trimmed_text[scan_index] in _TERMINALS:
                result_text = trimmed_text
            else:
                leading_text = trimmed_text[:scan_index + 1]
                trailing_closers = trimmed_text[scan_index + 1:]
                result_text = leading_text + terminal_mark + trailing_closers
        else:
            result_text = trimmed_text + terminal_mark
    return result_text


def extract_title_text(page):
    text = (getattr(page, 'title', '') or '').strip()
    if not text:
        return ''
    # If last character is already terminal punctuation, leave it
    if text[-1] in '.!?…':
        return text
    return text + '.'


def extract_meta_text(page):
    authors_text = ''
    author_relation = getattr(page, 'authors', None)
    if author_relation:
        author_names = [
            author_item.author.title
            for author_item in author_relation.all()
            if getattr(author_item, 'author', None) and getattr(author_item.author, 'title', None)
        ]
        if author_names:
            if len(author_names) == 1:
                authors_text = f'By {author_names[0]}'
            else:
                authors_text = f'By {", ".join(author_names[:-1])} and {author_names[-1]}.'
    disclaimer = 'This CG article is being read by an AI-generated voice. — .'
    return strip_tags(f'{authors_text} {disclaimer}').strip()


def _block_html_to_text(html_string):
    output_text = ''
    if html_string:
        block_closers_pattern = r'(p|h[1-6]|li|blockquote|pre|div|section|article|figure|figcaption)'
        html_string = re.sub(rf'(?is)</{block_closers_pattern}\s*>', r'</\1>\n', html_string)
        html_string = re.sub(r'(?is)<br\s*/?>', '\n', html_string)
        html_string = re.sub(r'(?is)<hr\s*/?>', '\n\n', html_string)

        stripped_text = strip_tags(html_string)
        paragraph_list = [para for para in re.split(r'\n+', stripped_text) if para and para.strip()]

        paragraph_pieces = []
        for paragraph in paragraph_list:
            normalized_paragraph = re.sub(r'\s+', ' ', paragraph).strip()
            punctuated_paragraph = _ensure_terminal_punct(normalized_paragraph, '.')
            paragraph_with_space = re.sub(r'\s*$', ' ', punctuated_paragraph)
            paragraph_pieces.append(paragraph_with_space)

        output_text = re.sub(r' {2,}', ' ', ''.join(paragraph_pieces))
    return output_text


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
                text_value = val.get('text')
                if isinstance(text_value, RichText):
                    html = text_value.source
                else:
                    html = text_value
            if html:
                block_text = _block_html_to_text(html)
                if block_text:
                    body_text.append(block_text)

    if body_text:
        body_clean = re.sub(r'\s+', ' ', ' '.join(body_text)).strip()
        parts.append(body_clean)

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


def synthesize_chunk(polly_client, text, voice_id=default_voice, use_ssml=False, format='mp3'):
    voice_engine = {
        'danielle_longform': {'voice': 'Danielle', 'engine': 'long-form'},
        'ruth_generative': {'voice': 'Ruth', 'engine': 'generative'},
        'danielle_generative': {'voice': 'Danielle', 'engine': 'generative'},
    }

    if voice_id in voice_engine:
        resp = polly_client.synthesize_speech(
            Text=text,
            OutputFormat=format,
            VoiceId=voice_engine[voice_id]['voice'],
            Engine=voice_engine[voice_id]['engine'],
        )
    else:
        resp = polly_client.synthesize_speech(
            Text=text,
            OutputFormat=format,
            VoiceId=voice_id,
        )
    audio_bytes = resp['AudioStream'].read()
    return AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)


def synthesize_plain_with_title_pause(page, voice_id=default_voice):
    polly = boto3.client('polly', region_name=AWS_REGION)
    article_text = f'{extract_title_text(page)} {extract_meta_text(page)} {extract_body_text(page)}'
    combined = None

    if not article_text:
        return None

    for ch in chunk_text(article_text):
        seg = synthesize_chunk(polly, ch, voice_id=voice_id, format='mp3')
        combined = seg if combined is None else (combined + seg)

    out = io.BytesIO()
    combined.export(out, format='mp3')
    out.seek(0)
    return out.getvalue()


# def synthesize_plain_with_title_pause(page, voice_id=default_voice):
#     # Plain-text synthesis with a precise silence inserted right after the title.
#     polly = boto3.client('polly', region_name=AWS_REGION)
#     title_text = extract_title_text(page)
#     meta_text = extract_meta_text(page)
#     body_text = extract_body_text(page)
#     combined = None

#     # 1) request title
#     if title_text:
#         title_seg = synthesize_chunk(polly, title_text, voice_id=voice_id, format='mp3')
#         combined = title_seg

#     # 2) request meta
#     if meta_text:
#         meta_seg = synthesize_chunk(polly, meta_text, voice_id=voice_id, format='mp3')
#         combined = meta_seg if combined is None else (combined + meta_seg)

#     # 3) request body
#     if body_text:
#         for ch in chunk_text(body_text):
#             seg = synthesize_chunk(polly, ch, voice_id=voice_id, format='mp3')
#             combined = seg if combined is None else (combined + seg)

#     out = io.BytesIO()
#     combined.export(out, format='mp3')
#     out.seek(0)
#     return out.getvalue()
