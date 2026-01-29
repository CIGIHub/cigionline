from __future__ import annotations

from dataclasses import dataclass

from django.shortcuts import get_object_or_404

from .models import Registrant


@dataclass(frozen=True)
class ManageLinkResult:
    registrant: Registrant
    ok: bool


def get_registrant_for_manage_link(*, registrant_id: int, token: str) -> Registrant:
    """Lookup registrant for a self-service manage link.

    Security model:
    - confirmation email contains a random token
    - DB stores only sha256(token)
    - URL contains raw token

    If token doesn't match, raise 404.
    """

    token_hash = Registrant.hash_manage_token(token)
    return get_object_or_404(Registrant, pk=registrant_id, manage_token_hash=token_hash)
