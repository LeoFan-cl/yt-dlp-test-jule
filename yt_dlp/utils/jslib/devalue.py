b'--- ./yt_dlp/utils/jslib/devalue.py\t(original)'
b'+++ ./yt_dlp/utils/jslib/devalue.py\t(refactored)'
b'@@ -1,3 +1,5 @@'
b'+from __future__ import division'
b'+from __future__ import absolute_import'
b' from __future__ import annotations'
b' '
b' import array'
b'@@ -7,33 +9,36 @@'
b' import re'
b' '
b' from .._utils import parse_iso8601'
b'+from itertools import izip'
b' '
b' TYPE_CHECKING = False'
b' if TYPE_CHECKING:'
b'     import collections.abc'
b'     import typing'
b' '
b"-    T = typing.TypeVar('T')"
b"+    T = typing.TypeVar(u'T')"
b' '
b' '
b' _ARRAY_TYPE_LOOKUP = {'
b"-    'Int8Array': 'b',"
b"-    'Uint8Array': 'B',"
b"-    'Uint8ClampedArray': 'B',"
b"-    'Int16Array': 'h',"
b"-    'Uint16Array': 'H',"
b"-    'Int32Array': 'i',"
b"-    'Uint32Array': 'I',"
b"-    'Float32Array': 'f',"
b"-    'Float64Array': 'd',"
b"-    'BigInt64Array': 'l',"
b"-    'BigUint64Array': 'L',"
b"-    'ArrayBuffer': 'B',"
b"+    u'Int8Array': u'b',"
b"+    u'Uint8Array': u'B',"
b"+    u'Uint8ClampedArray': u'B',"
b"+    u'Int16Array': u'h',"
b"+    u'Uint16Array': u'H',"
b"+    u'Int32Array': u'i',"
b"+    u'Uint32Array': u'I',"
b"+    u'Float32Array': u'f',"
b"+    u'Float64Array': u'd',"
b"+    u'BigInt64Array': u'l',"
b"+    u'BigUint64Array': u'L',"
b"+    u'ArrayBuffer': u'B',"
b' }'
b' '
b' '
b'-def parse_iter(parsed: typing.Any, /, *, revivers: dict[str, collections.abc.Callable[[list], typing.Any]] | None = None):'
b'+def parse_iter(parsed, /, **_3to2kwargs):'
b'     # based on https://github.com/Rich-Harris/devalue/blob/f3fd2aa93d79f21746555671f955a897335edb1b/src/parse.js'
b"+    if 'revivers' in _3to2kwargs: revivers = _3to2kwargs['revivers']; del _3to2kwargs['revivers']"
b'+    else: revivers =  None'
b'     resolved = {'
b'         -1: None,'
b'         -2: None,'
b'@@ -45,12 +50,12 @@'
b' '
b'     if isinstance(parsed, int) and not isinstance(parsed, bool):'
b'         if parsed not in resolved or parsed == -2:'
b"-            raise ValueError('invalid integer input')"
b"+            raise ValueError(u'invalid integer input')"
b'         return resolved[parsed]'
b'     elif not isinstance(parsed, list):'
b"-        raise ValueError('expected int or list as input')"
b"+        raise ValueError(u'expected int or list as input')"
b'     elif not parsed:'
b"-        raise ValueError('expected a non-empty list as input')"
b"+        raise ValueError(u'expected a non-empty list as input')"
b' '
b'     if revivers is None:'
b'         revivers = {}'
b'@@ -63,7 +68,7 @@'
b'             name, source, reviver = source'
b'             try:'
b'                 resolved[source] = target[index] = reviver(target[index])'
b'-            except Exception as error:'
b'+            except Exception, error:'
b"                 yield TypeError(f'failed to parse {source} as {name!r}: {error}')"
b'                 resolved[source] = target[index] = None'
b'             continue'
b'@@ -79,12 +84,12 @@'
b' '
b'         try:'
b'             value = parsed[source]'
b'-        except IndexError as error:'
b'+        except IndexError, error:'
b'             yield error'
b'             continue'
b' '
b'         if isinstance(value, list):'
b'-            if value and isinstance(value[0], str):'
b'+            if value and isinstance(value[0], unicode):'
b'                 # TODO: implement zips `strict=True`'
b'                 if reviver := revivers.get(value[0]):'
b'                     if value[1] == source:'
b'@@ -96,40 +101,40 @@'
b'                     stack.append((target, index, value[1]))'
b'                     continue'
b' '
b"-                elif value[0] == 'Date':"
b"+                elif value[0] == u'Date':"
b'                     try:'
b'                         result = dt.datetime.fromtimestamp(parse_iso8601(value[1]), tz=dt.timezone.utc)'
b'                     except Exception:'
b"                         yield ValueError(f'invalid date: {value[1]!r}')"
b'                         result = None'
b' '
b"-                elif value[0] == 'Set':"
b"+                elif value[0] == u'Set':"
b'                     result = [None] * (len(value) - 1)'
b'                     for offset, new_source in enumerate(value[1:]):'
b'                         stack.append((result, offset, new_source))'
b' '
b"-                elif value[0] == 'Map':"
b"+                elif value[0] == u'Map':"
b'                     result = []'
b'-                    for key, new_source in zip(*(iter(value[1:]),) * 2):'
b'+                    for key, new_source in izip(*(iter(value[1:]),) * 2):'
b'                         pair = [None, None]'
b'                         stack.append((pair, 0, key))'
b'                         stack.append((pair, 1, new_source))'
b'                         result.append(pair)'
b' '
b"-                elif value[0] == 'RegExp':"
b"+                elif value[0] == u'RegExp':"
b'                     # XXX: use jsinterp to translate regex flags'
b'                     #      currently ignores `value[2]`'
b'                     result = re.compile(value[1])'
b' '
b"-                elif value[0] == 'Object':"
b"+                elif value[0] == u'Object':"
b'                     result = value[1]'
b' '
b"-                elif value[0] == 'BigInt':"
b"+                elif value[0] == u'BigInt':"
b'                     result = int(value[1])'
b' '
b"-                elif value[0] == 'null':"
b"+                elif value[0] == u'null':"
b'                     result = {}'
b'-                    for key, new_source in zip(*(iter(value[1:]),) * 2):'
b'+                    for key, new_source in izip(*(iter(value[1:]),) * 2):'
b'                         stack.append((result, key, new_source))'
b' '
b'                 elif value[0] in _ARRAY_TYPE_LOOKUP:'
b'@@ -158,10 +163,12 @@'
b'     return return_value[0]'
b' '
b' '
b'-def parse(parsed: typing.Any, /, *, revivers: dict[str, collections.abc.Callable[[typing.Any], typing.Any]] | None = None):'
b'+def parse(parsed, /, **_3to2kwargs):'
b"+    if 'revivers' in _3to2kwargs: revivers = _3to2kwargs['revivers']; del _3to2kwargs['revivers']"
b'+    else: revivers =  None'
b'     generator = parse_iter(parsed, revivers=revivers)'
b'     while True:'
b'         try:'
b'             raise generator.send(None)'
b'-        except StopIteration as error:'
b'+        except StopIteration, error:'
b'             return error.value'
