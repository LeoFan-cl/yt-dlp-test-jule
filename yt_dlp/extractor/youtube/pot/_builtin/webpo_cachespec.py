# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from yt_dlp.extractor.youtube.pot._provider import BuiltinIEContentProvider
from yt_dlp.extractor.youtube.pot.cache import (
    CacheProviderWritePolicy,
    PoTokenCacheSpec,
    PoTokenCacheSpecProvider,
    register_spec,
)
from yt_dlp.extractor.youtube.pot.provider import (
    PoTokenRequest,
)
from yt_dlp.extractor.youtube.pot.utils import ContentBindingType, get_webpo_content_binding
from yt_dlp.utils import traverse_obj


class WebPoPCSP(PoTokenCacheSpecProvider, BuiltinIEContentProvider):
    PROVIDER_NAME = u'webpo'

    def generate_cache_spec(self, request):
        bind_to_visitor_id = self._configuration_arg(
            u'bind_to_visitor_id', default=[u'true'])[0] == u'true'

        content_binding, content_binding_type = get_webpo_content_binding(
            request, bind_to_visitor_id=bind_to_visitor_id)

        if not content_binding or not content_binding_type:
            return None

        write_policy = CacheProviderWritePolicy.WRITE_ALL
        if content_binding_type == ContentBindingType.VIDEO_ID:
            write_policy = CacheProviderWritePolicy.WRITE_FIRST

        return PoTokenCacheSpec(
            key_bindings={
                u't': u'webpo',
                u'cb': content_binding,
                u'cbt': content_binding_type.value,
                u'ip': traverse_obj(request.innertube_context, (u'client', u'remoteHost')),
                u'sa': request.request_source_address,
                u'px': request.request_proxy,
            },
            # Integrity token response usually states it has a ttl of 12 hours (43200 seconds).
            # We will default to 6 hours to be safe.
            default_ttl=21600,
            write_policy=write_policy,
        )

WebPoPCSP = register_spec(WebPoPCSP)
