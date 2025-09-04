# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import calendar
import copy
import functools
import hashlib
import json
import re
import time

from ..common import InfoExtractor
from ...networking.exceptions import HTTPError, network_exceptions
from ...utils import (
    ExtractorError,
    bug_reports_message,
    datetime_from_str,
    filter_dict,
    get_first,
    int_or_none,
    is_html,
    join_nonempty,
    parse_count,
    qualities,
    str_to_int,
    traverse_obj,
    try_call,
    try_get,
    unified_timestamp,
    url_or_none,
    variadic,
)
from ...compat._legacy import compat_urllib_parse as urllib_parse


class _PoTokenContext(object):
    PLAYER = u'player'
    GVS = u'gvs'
    SUBS = u'subs'


class StreamingProtocol(object):
    HTTPS = u'https'
    DASH = u'dash'
    HLS = u'hls'


class BasePoTokenPolicy(object):
    def __init__(self, required=False, recommended=False, not_required_for_premium=False):
        self.required = required
        self.recommended = recommended
        self.not_required_for_premium = not_required_for_premium


class GvsPoTokenPolicy(BasePoTokenPolicy):
    def __init__(self, not_required_with_player_token=False, **kwargs):
        super(GvsPoTokenPolicy, self).__init__(**kwargs)
        self.not_required_with_player_token = not_required_with_player_token


class PlayerPoTokenPolicy(BasePoTokenPolicy):
    pass


class SubsPoTokenPolicy(BasePoTokenPolicy):
    pass


WEB_PO_TOKEN_POLICIES = {
    u'GVS_PO_TOKEN_POLICY': {
        StreamingProtocol.HTTPS: GvsPoTokenPolicy(
            required=True,
            recommended=True,
            not_required_for_premium=True,
            not_required_with_player_token=False,
        ),
        StreamingProtocol.DASH: GvsPoTokenPolicy(
            required=True,
            recommended=True,
            not_required_for_premium=True,
            not_required_with_player_token=False,
        ),
        StreamingProtocol.HLS: GvsPoTokenPolicy(
            required=False,
            recommended=True,
        ),
    },
    u'PLAYER_PO_TOKEN_POLICY': PlayerPoTokenPolicy(required=False),
    u'SUBS_PO_TOKEN_POLICY': SubsPoTokenPolicy(required=False),
}

# any clients starting with _ cannot be explicitly requested by the user
INNERTUBE_CLIENTS = {
    u'web': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'WEB',
                u'clientVersion': u'2.20250312.04.00',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 1,
        u'SUPPORTS_COOKIES': True,
    },
    u'web_safari': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'WEB',
                u'clientVersion': u'2.20250312.04.00',
                u'userAgent': u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15,gzip(gfe)',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 1,
        u'SUPPORTS_COOKIES': True,
    },
    u'web_embedded': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'WEB_EMBEDDED_PLAYER',
                u'clientVersion': u'1.20250310.01.00',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 56,
        u'SUPPORTS_COOKIES': True,
    },
    u'web_music': {
        u'INNERTUBE_HOST': u'music.youtube.com',
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'WEB_REMIX',
                u'clientVersion': u'1.20250310.01.00',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 67,
        u'GVS_PO_TOKEN_POLICY': {
            StreamingProtocol.HTTPS: GvsPoTokenPolicy(
                required=True,
                recommended=True,
                not_required_for_premium=True,
                not_required_with_player_token=False,
            ),
            StreamingProtocol.DASH: GvsPoTokenPolicy(
                required=True,
                recommended=True,
                not_required_for_premium=True,
                not_required_with_player_token=False,
            ),
            StreamingProtocol.HLS: GvsPoTokenPolicy(
                required=False,
                recommended=True,
            ),
        },
        u'SUPPORTS_COOKIES': True,
    },
    u'web_creator': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'WEB_CREATOR',
                u'clientVersion': u'1.20250312.03.01',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 62,
        u'GVS_PO_TOKEN_POLICY': {
            StreamingProtocol.HTTPS: GvsPoTokenPolicy(
                required=True,
                recommended=True,
                not_required_for_premium=True,
                not_required_with_player_token=False,
            ),
            StreamingProtocol.DASH: GvsPoTokenPolicy(
                required=True,
                recommended=True,
                not_required_for_premium=True,
                not_required_with_player_token=False,
            ),
            StreamingProtocol.HLS: GvsPoTokenPolicy(
                required=False,
                recommended=True,
            ),
        },
        u'REQUIRE_AUTH': True,
        u'SUPPORTS_COOKIES': True,
    },
    u'android': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'ANDROID',
                u'clientVersion': u'20.10.38',
                u'androidSdkVersion': 30,
                u'userAgent': u'com.google.android.youtube/20.10.38 (Linux; U; Android 11) gzip',
                u'osName': u'Android',
                u'osVersion': u'11',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 3,
        u'REQUIRE_JS_PLAYER': False,
        u'GVS_PO_TOKEN_POLICY': {
            StreamingProtocol.HTTPS: GvsPoTokenPolicy(
                required=True,
                recommended=True,
                not_required_with_player_token=True,
            ),
            StreamingProtocol.DASH: GvsPoTokenPolicy(
                required=True,
                recommended=True,
                not_required_with_player_token=True,
            ),
            StreamingProtocol.HLS: GvsPoTokenPolicy(
                required=False,
                recommended=True,
                not_required_with_player_token=True,
            ),
        },
        u'PLAYER_PO_TOKEN_POLICY': PlayerPoTokenPolicy(required=False, recommended=True),
    },
    u'android_vr': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'ANDROID_VR',
                u'clientVersion': u'1.62.27',
                u'deviceMake': u'Oculus',
                u'deviceModel': u'Quest 3',
                u'androidSdkVersion': 32,
                u'userAgent': u'com.google.android.apps.youtube.vr.oculus/1.62.27 (Linux; U; Android 12L; eureka-user Build/SQ3A.220605.009.A1) gzip',
                u'osName': u'Android',
                u'osVersion': u'12L',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 28,
        u'REQUIRE_JS_PLAYER': False,
    },
    u'ios': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'IOS',
                u'clientVersion': u'20.10.4',
                u'deviceMake': u'Apple',
                u'deviceModel': u'iPhone16,2',
                u'userAgent': u'com.google.ios.youtube/20.10.4 (iPhone16,2; U; CPU iOS 18_3_2 like Mac OS X;)',
                u'osName': u'iPhone',
                u'osVersion': u'18.3.2.22D82',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 5,
        u'GVS_PO_TOKEN_POLICY': {
            StreamingProtocol.HTTPS: GvsPoTokenPolicy(
                required=True,
                recommended=True,
                not_required_with_player_token=True,
            ),
            StreamingProtocol.HLS: GvsPoTokenPolicy(
                required=True,
                recommended=True,
                not_required_with_player_token=True,
            ),
        },
        u'PLAYER_PO_TOKEN_POLICY': PlayerPoTokenPolicy(required=False, recommended=True),
        u'REQUIRE_JS_PLAYER': False,
    },
    u'mweb': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'MWEB',
                u'clientVersion': u'2.20250311.03.00',
                u'userAgent': u'Mozilla/5.0 (iPad; CPU OS 16_7_10 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1,gzip(gfe)',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 2,
        u'GVS_PO_TOKEN_POLICY': {
            StreamingProtocol.HTTPS: GvsPoTokenPolicy(
                required=True,
                recommended=True,
                not_required_for_premium=True,
                not_required_with_player_token=False,
            ),
            StreamingProtocol.DASH: GvsPoTokenPolicy(
                required=True,
                recommended=True,
                not_required_for_premium=True,
                not_required_with_player_token=False,
            ),
            StreamingProtocol.HLS: GvsPoTokenPolicy(
                required=False,
                recommended=True,
            ),
        },
        u'SUPPORTS_COOKIES': True,
    },
    u'tv': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'TVHTML5',
                u'clientVersion': u'7.20250312.16.00',
                u'userAgent': u'Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 7,
        u'SUPPORTS_COOKIES': True,
    },
    u'tv_simply': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'TVHTML5_SIMPLY',
                u'clientVersion': u'1.0',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 75,
    },
    u'tv_embedded': {
        u'INNERTUBE_CONTEXT': {
            u'client': {
                u'clientName': u'TVHTML5_SIMPLY_EMBEDDED_PLAYER',
                u'clientVersion': u'2.0',
            },
        },
        u'INNERTUBE_CONTEXT_CLIENT_NAME': 85,
        u'REQUIRE_AUTH': True,
        u'SUPPORTS_COOKIES': True,
    },
}
for client in INNERTUBE_CLIENTS:
    INNERTUBE_CLIENTS[client].update(WEB_PO_TOKEN_POLICIES)


def _split_innertube_client(client_name):
    parts = client_name.rsplit(u'.', 1)
    if len(parts) > 1:
        variant, base = parts
        return variant, base, variant
    parts = client_name.split(u'_', 1)
    base = parts[0]
    variant = parts[1] if len(parts) > 1 else None
    return client_name, base, variant


def short_client_name(client_name):
    main, parts = (_split_innertube_client(client_name)[0].split(u'_', 1) + [[]])[:2]
    return join_nonempty(main[:4], u''.join(x[0] for x in parts)).upper()


def build_innertube_clients():
    THIRD_PARTY = {
        u'embedUrl': u'https://www.youtube.com/',
    }
    BASE_CLIENTS = (u'ios', u'web', u'tv', u'mweb', u'android')
    priority = qualities(BASE_CLIENTS[::-1])

    for client, ytcfg in INNERTUBE_CLIENTS.items():
        ytcfg.setdefault(u'INNERTUBE_HOST', u'www.youtube.com')
        ytcfg.setdefault(u'REQUIRE_JS_PLAYER', True)
        ytcfg.setdefault(u'GVS_PO_TOKEN_POLICY', {})
        for protocol in (StreamingProtocol.HTTPS, StreamingProtocol.DASH, StreamingProtocol.HLS):
            ytcfg[u'GVS_PO_TOKEN_POLICY'].setdefault(protocol, GvsPoTokenPolicy())
        ytcfg.setdefault(u'PLAYER_PO_TOKEN_POLICY', PlayerPoTokenPolicy())
        ytcfg.setdefault(u'SUBS_PO_TOKEN_POLICY', SubsPoTokenPolicy())
        ytcfg.setdefault(u'REQUIRE_AUTH', False)
        ytcfg.setdefault(u'SUPPORTS_COOKIES', False)
        ytcfg.setdefault(u'PLAYER_PARAMS', None)
        ytcfg[u'INNERTUBE_CONTEXT'][u'client'].setdefault(u'hl', u'en')

        _, base_client, variant = _split_innertube_client(client)
        ytcfg[u'priority'] = 10 * priority(base_client)

        if variant == u'embedded':
            ytcfg[u'INNERTUBE_CONTEXT'][u'thirdParty'] = THIRD_PARTY
            ytcfg[u'priority'] -= 2
        elif variant:
            ytcfg[u'priority'] -= 3


build_innertube_clients()


class BadgeType(object):
    AVAILABILITY_UNLISTED = 1
    AVAILABILITY_PRIVATE = 2
    AVAILABILITY_PUBLIC = 3
    AVAILABILITY_PREMIUM = 4
    AVAILABILITY_SUBSCRIPTION = 5
    LIVE_NOW = 6
    VERIFIED = 7


CONFIGURATION_ARG_KEY = u'youtube'


class YoutubeBaseInfoExtractor(InfoExtractor):
    u"""Provide base functions for Youtube extractors"""
    pass
