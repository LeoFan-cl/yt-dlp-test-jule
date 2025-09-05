from __future__ import absolute_import
import collections
import contextlib
import functools

@contextlib.contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        pass
import importlib
import sys
import types

_NO_ATTRIBUTE = object()

_Package = collections.namedtuple('Package', ('name', 'version'))


def get_package_info(module):
    return _Package(
        name=getattr(module, '_yt_dlp__identifier', module.__name__),
        version=str(next(filter(None, (
            getattr(module, attr, None)
            for attr in ('_yt_dlp__version', '__version__', 'version_string', 'version')
        )), None)))


def _is_package(module):
    return hasattr(module, '__path__')


def _is_dunder(name):
    return name.startswith('__') and name.endswith('__')


class EnhancedModule(types.ModuleType):
    def __bool__(self):
        return vars(self).get('__bool__', lambda: True)()

    def __getattribute__(self, attr):
        try:
            ret = super(EnhancedModule, self).__getattribute__(attr)
        except AttributeError:
            if _is_dunder(attr):
                raise
            getter = getattr(self, '__getattr__', None)
            if not getter:
                raise
            ret = getter(attr)
        return ret.fget() if isinstance(ret, property) else ret


def passthrough_module(parent, child, allowed_attributes=(None, ), callback=lambda _: None):
    """Passthrough parent module into a child module, creating the parent if necessary"""
    def __getattr__(attr):
        if _is_package(sys.modules[parent]):
            with suppress(ImportError):
                return importlib.import_module('.%s' % attr, parent)

        ret = from_child(attr)
        if ret is _NO_ATTRIBUTE:
            raise AttributeError('module %s has no attribute %s' % (parent, attr))
        callback(attr)
        return ret

    # @functools.cache
    def from_child(attr):
        child_ref = [child]
        if attr not in allowed_attributes:
            if None not in allowed_attributes or _is_dunder(attr):
                return _NO_ATTRIBUTE

        if isinstance(child_ref[0], str):
            child_ref[0] = importlib.import_module(child_ref[0], parent)

        if _is_package(child_ref[0]):
            with suppress(ImportError):
                return passthrough_module('%s.%s' % (parent, attr),
                                          importlib.import_module('.%s' % attr, child_ref[0].__name__))

        with suppress(AttributeError):
            return getattr(child_ref[0], attr)

        return _NO_ATTRIBUTE

    original_module = sys.modules.get(parent)
    if original_module and isinstance(original_module, EnhancedModule):
        return original_module

    new_module = EnhancedModule(parent)
    if original_module:
        for attr, value in vars(original_module).items():
            setattr(new_module, attr, value)

    new_module.__getattr__ = __getattr__
    sys.modules[parent] = new_module
    return new_module
