# flake8: noqa: F401
from __future__ import absolute_import
import warnings

from .common import (
    HEADRequest,
    Request,
    Response,
    RetryManager,
    http_head,
    urlopen,
)
from ..utils import bug_reports_message

# Import request handlers
try:
    from . import _requests
except ImportError:
    pass
except Exception, e:
    warnings.warn('Failed to import "requests" request handler: %s' % e + bug_reports_message())

try:
    from . import _websockets
except ImportError:
    pass
except Exception, e:
    warnings.warn('Failed to import "websockets" request handler: %s' % e + bug_reports_message())

try:
    from . import _curlcffi
except ImportError:
    pass
except Exception, e:
    warnings.warn('Failed to import "curl_cffi" request handler: %s' % e + bug_reports_message())
