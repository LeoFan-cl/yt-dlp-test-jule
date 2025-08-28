from __future__ import absolute_import, division, print_function, unicode_literals
from itertools import ifilter

from ..compat.compat_utils import passthrough_module
from ..globals import extractors as _extractors_context
from ..globals import plugin_ies as _plugin_ies_context
from ..plugins import PluginSpec, register_plugin_spec

passthrough_module(__name__, '._extractors')
del passthrough_module

register_plugin_spec(PluginSpec(
    module_name='extractor',
    suffix='IE',
    destination=_extractors_context,
    plugin_destination=_plugin_ies_context,
))


def import_extractors():
    from . import _extractors  # noqa: F401


def gen_extractor_classes():
    """ Return a list of supported extractors.
    The order does matter; a matched extractor is the one handling the URL.
    """
    if not _extractors_context.value:
        from . import _extractors
        for name, klass in _extractors.__dict__.items():
            if name.endswith('IE') and isinstance(klass, type):
                _extractors_context.value[name] = klass
    return list(_extractors_context.value.values())


def gen_extractors():
    """ Return a list of an instance of every supported extractor.
    The order does matter; a matched extractor is the one handling the URL.
    """
    return [klass() for klass in gen_extractor_classes()]


def list_extractor_classes(age_limit=None):
    """Return a list of extractors that are suitable for the given age, sorted by extractor name"""
    for ie in sorted(ifilter(
            lambda ie: ie.is_suitable(age_limit),
            gen_extractor_classes()), key=lambda ie: ie.IE_NAME.lower()):
        yield ie


def list_extractors(age_limit=None):
    """Return a list of extractor instances that are suitable for the given age, sorted by extractor name"""
    return [ie() for ie in list_extractor_classes(age_limit)]


def get_info_extractor(ie_name):
    """Returns the info extractor class with the given ie_name"""
    import_extractors()
    return _extractors_context.value['{0}IE'.format(ie_name)]
