from __future__ import annotations

from dataclasses import dataclass

from django.shortcuts import get_object_or_404

from .models import Registrant, RegistrationGroup


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


def get_group_for_manage_link(*, group_id: int, token: str) -> RegistrationGroup:
    """Lookup a RegistrationGroup for a group-manage link (sha256(token) stored)."""

    token_hash = RegistrationGroup.hash_manage_token(token)
    return get_object_or_404(RegistrationGroup, pk=group_id, manage_token_hash=token_hash)


def get_registrant_for_group_manage_link(*, group_id: int, registrant_id: int, token: str) -> Registrant:
    """Lookup a Registrant within a group given the group manage token."""

    group = get_group_for_manage_link(group_id=group_id, token=token)
    return get_object_or_404(Registrant, pk=registrant_id, group=group)
