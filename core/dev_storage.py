"""Local-first, read-only pull-through storage for staging assets."""

import logging
import os
import tempfile
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage

logger = logging.getLogger(__name__)

STAGING_ASSET_BASE = 'https://cigionline-static-staging-2025.s3.amazonaws.com/static/'


class StagingPullThroughStorage(FileSystemStorage):
    def _pull_from_staging(self, name):
        local_path = self.path(name)
        if os.path.exists(local_path):
            return True
        url = STAGING_ASSET_BASE + urllib.parse.quote(name)
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read()
        except (OSError, ValueError) as exc:
            logger.warning('staging asset pull failed for %s: %s', name, exc)
            return False
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(local_path)) as fh:
            fh.write(data)
            fh.flush()
            try:
                os.link(fh.name, local_path)
            except FileExistsError:
                return True
        logger.info('pulled %s from staging (%d bytes)', name, len(data))
        return True

    # _open covers every read path (renditions, focal-point ops, file serves).
    # exists()/size() are deliberately left alone: save() probes exists() to
    # pick free filenames, and pulling there would fetch on every upload.
    def _open(self, name, mode='rb'):
        if 'r' in mode:
            self._pull_from_staging(name)
        return super()._open(name, mode)


class StagingStaticFinder(BaseFinder):
    def check(self, **kwargs):
        return []

    def find(self, path, find_all=False, **kwargs):
        find_all = self._check_deprecated_find_param(find_all=find_all, **kwargs)
        storage = StagingPullThroughStorage(
            location=os.path.join(settings.MEDIA_ROOT, '.staging-static'),
        )
        found = storage._pull_from_staging(path)
        result = storage.path(path) if found else None
        return [result] if find_all and result else ([] if find_all else result)

    def list(self, ignore_patterns):
        return []


def serve_media_pull_through(request, path):
    """Dev /staticmedia/ view: pull a missing file (original OR an already-
    generated rendition) before delegating to the static server.
    """
    from django.views.static import serve

    StagingPullThroughStorage()._pull_from_staging(path)
    return serve(request, path, document_root=settings.MEDIA_ROOT)
