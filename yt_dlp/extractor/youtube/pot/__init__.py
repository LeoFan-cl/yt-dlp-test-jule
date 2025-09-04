# Trigger import of built-in providers
from __future__ import absolute_import
from ._builtin.memory_cache import MemoryLRUPCP as _MemoryLRUPCP  # noqa: F401
from ._builtin.webpo_cachespec import WebPoPCSP as _WebPoPCSP  # noqa: F401
