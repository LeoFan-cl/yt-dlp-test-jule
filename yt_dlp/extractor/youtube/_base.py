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
    PLAYER = 'player'
    GVS = 'gvs'
    SUBS = 'subs'


class StreamingProtocol(object):
    HTTPS = 'https'
    DASH = 'dash'
    HLS = 'hls'


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
    'GVS_PO_TOKEN_POLICY': {
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
    'PLAYER_PO_TOKEN_POLICY': PlayerPoTokenPolicy(required=False),
    'SUBS_PO_TOKEN_POLICY': SubsPoTokenPolicy(required=False),
}

# any clients starting with _ cannot be explicitly requested by the user
INNERTUBE_CLIENTS = {
    'web': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'WEB',
                'clientVersion': '2.20250312.04.00',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 1,
        'SUPPORTS_COOKIES': True,
    },
    'web_safari': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'WEB',
                'clientVersion': '2.20250312.04.00',
                'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15,gzip(gfe)',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 1,
        'SUPPORTS_COOKIES': True,
    },
    'web_embedded': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'WEB_EMBEDDED_PLAYER',
                'clientVersion': '1.20250310.01.00',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 56,
        'SUPPORTS_COOKIES': True,
    },
    'web_music': {
        'INNERTUBE_HOST': 'music.youtube.com',
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'WEB_REMIX',
                'clientVersion': '1.20250310.01.00',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 67,
        'GVS_PO_TOKEN_POLICY': {
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
        'SUPPORTS_COOKIES': True,
    },
    'web_creator': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'WEB_CREATOR',
                'clientVersion': '1.20250312.03.01',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 62,
        'GVS_PO_TOKEN_POLICY': {
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
        'REQUIRE_AUTH': True,
        'SUPPORTS_COOKIES': True,
    },
    'android': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'ANDROID',
                'clientVersion': '20.10.38',
                'androidSdkVersion': 30,
                'userAgent': 'com.google.android.youtube/20.10.38 (Linux; U; Android 11) gzip',
                'osName': 'Android',
                'osVersion': '11',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 3,
        'REQUIRE_JS_PLAYER': False,
        'GVS_PO_TOKEN_POLICY': {
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
        'PLAYER_PO_TOKEN_POLICY': PlayerPoTokenPolicy(required=False, recommended=True),
    },
    'android_vr': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'ANDROID_VR',
                'clientVersion': '1.62.27',
                'deviceMake': 'Oculus',
                'deviceModel': 'Quest 3',
                'androidSdkVersion': 32,
                'userAgent': 'com.google.android.apps.youtube.vr.oculus/1.62.27 (Linux; U; Android 12L; eureka-user Build/SQ3A.220605.009.A1) gzip',
                'osName': 'Android',
                'osVersion': '12L',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 28,
        'REQUIRE_JS_PLAYER': False,
    },
    'ios': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'IOS',
                'clientVersion': '20.10.4',
                'deviceMake': 'Apple',
                'deviceModel': 'iPhone16,2',
                'userAgent': 'com.google.ios.youtube/20.10.4 (iPhone16,2; U; CPU iOS 18_3_2 like Mac OS X;)',
                'osName': 'iPhone',
                'osVersion': '18.3.2.22D82',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 5,
        'GVS_PO_TOKEN_POLICY': {
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
        'PLAYER_PO_TOKEN_POLICY': PlayerPoTokenPolicy(required=False, recommended=True),
        'REQUIRE_JS_PLAYER': False,
    },
    'mweb': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'MWEB',
                'clientVersion': '2.20250311.03.00',
                'userAgent': 'Mozilla/5.0 (iPad; CPU OS 16_7_10 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1,gzip(gfe)',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 2,
        'GVS_PO_TOKEN_POLICY': {
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
        'SUPPORTS_COOKIES': True,
    },
    'tv': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'TVHTML5',
                'clientVersion': '7.20250312.16.00',
                'userAgent': 'Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 7,
        'SUPPORTS_COOKIES': True,
    },
    'tv_simply': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'TVHTML5_SIMPLY',
                'clientVersion': '1.0',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 75,
    },
    'tv_embedded': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'TVHTML5_SIMPLY_EMBEDDED_PLAYER',
                'clientVersion': '2.0',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 85,
        'REQUIRE_AUTH': True,
        'SUPPORTS_COOKIES': True,
    },
}
for client in INNERTUBE_CLIENTS:
    INNERTUBE_CLIENTS[client].update(WEB_PO_TOKEN_POLICIES)


def _split_innertube_client(client_name):
    parts = client_name.rsplit('.', 1)
    if len(parts) > 1:
        variant, base = parts
        return variant, base, variant
    parts = client_name.split('_', 1)
    base = parts[0]
    variant = parts[1] if len(parts) > 1 else None
    return client_name, base, variant


def short_client_name(client_name):
    main, parts = (_split_innertube_client(client_name)[0].split('_', 1) + [[]])[:2]
    return join_nonempty(main[:4], ''.join(x[0] for x in parts)).upper()


def build_innertube_clients():
    THIRD_PARTY = {
        'embedUrl': 'https://www.youtube.com/',
    }
    BASE_CLIENTS = ('ios', 'web', 'tv', 'mweb', 'android')
    priority = qualities(BASE_CLIENTS[::-1])

    for client, ytcfg in INNERTUBE_CLIENTS.items():
        ytcfg.setdefault('INNERTUBE_HOST', 'www.youtube.com')
        ytcfg.setdefault('REQUIRE_JS_PLAYER', True)
        ytcfg.setdefault('GVS_PO_TOKEN_POLICY', {})
        for protocol in (StreamingProtocol.HTTPS, StreamingProtocol.DASH, StreamingProtocol.HLS):
            ytcfg['GVS_PO_TOKEN_POLICY'].setdefault(protocol, GvsPoTokenPolicy())
        ytcfg.setdefault('PLAYER_PO_TOKEN_POLICY', PlayerPoTokenPolicy())
        ytcfg.setdefault('SUBS_PO_TOKEN_POLICY', SubsPoTokenPolicy())
        ytcfg.setdefault('REQUIRE_AUTH', False)
        ytcfg.setdefault('SUPPORTS_COOKIES', False)
        ytcfg.setdefault('PLAYER_PARAMS', None)
        ytcfg['INNERTUBE_CONTEXT']['client'].setdefault('hl', 'en')

        _, base_client, variant = _split_innertube_client(client)
        ytcfg['priority'] = 10 * priority(base_client)

        if variant == 'embedded':
            ytcfg['INNERTUBE_CONTEXT']['thirdParty'] = THIRD_PARTY
            ytcfg['priority'] -= 2
        elif variant:
            ytcfg['priority'] -= 3


build_innertube_clients()


class BadgeType(object):
    AVAILABILITY_UNLISTED = 1
    AVAILABILITY_PRIVATE = 2
    AVAILABILITY_PUBLIC = 3
    AVAILABILITY_PREMIUM = 4
    AVAILABILITY_SUBSCRIPTION = 5
    LIVE_NOW = 6
    VERIFIED = 7


CONFIGURATION_ARG_KEY = 'youtube'


class YoutubeBaseInfoExtractor(InfoExtractor):
    """Provide base functions for Youtube extractors"""
    pass
