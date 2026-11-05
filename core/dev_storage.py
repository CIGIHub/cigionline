"""Dev-only pull-through media storage.

The local DB references ~11.5k media files (~20 GB) that live in the staging
S3 bucket, not on disk. Rather than mirroring the bucket, this storage
downloads an original from staging the first time something opens it (e.g.
Wagtail generating a rendition), so each page hydrates exactly the images it
uses on first local render. Wired up in settings/dev.py only.
"""

import logging
import os
import urllib.parse
import urllib.request

from django.core.files.storage import FileSystemStorage

logger = logging.getLogger(__name__)

STAGING_MEDIA_BASE = 'https://cigionline-static-staging-2025.s3.amazonaws.com/static/'


class StagingPullThroughStorage(FileSystemStorage):
    def _pull_from_staging(self, name):
        local_path = self.path(name)
        if os.path.exists(local_path):
            return
        url = STAGING_MEDIA_BASE + urllib.parse.quote(name)
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read()
        except Exception as exc:  # missing on staging too — leave it absent
            logger.warning('staging media pull failed for %s: %s', name, exc)
            return
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as fh:
            fh.write(data)
        logger.info('pulled %s from staging (%d bytes)', name, len(data))

    # _open covers every read path (renditions, focal-point ops, file serves).
    # exists()/size() are deliberately left alone: save() probes exists() to
    # pick free filenames, and pulling there would fetch on every upload.
    def _open(self, name, mode='rb'):
        if 'r' in mode:
            self._pull_from_staging(name)
        return super()._open(name, mode)


def serve_media_pull_through(request, path):
    """Dev /staticmedia/ view: pull a missing file (original OR an already-
    generated rendition — the DB dump carries 40k rendition rows whose files
    live only in the staging bucket) before delegating to the static server.
    """
    from django.conf import settings
    from django.views.static import serve

    StagingPullThroughStorage()._pull_from_staging(path)
    return serve(request, path, document_root=settings.MEDIA_ROOT)
