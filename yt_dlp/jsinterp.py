b'--- ./yt_dlp/jsinterp.py\t(original)'
b'+++ ./yt_dlp/jsinterp.py\t(refactored)'
b'@@ -1,3 +1,6 @@'
b'+from __future__ import division'
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import collections'
b' import contextlib'
b' import itertools'
b'@@ -16,6 +19,8 @@'
b'     unified_timestamp,'
b'     write_string,'
b' )'
b'+from itertools import izip'
b'+from itertools import imap'
b' '
b' '
b' def _js_bit_op(op):'
b'@@ -37,7 +42,7 @@'
b' '
b'     def wrapped(a, b):'
b'         if JS_Undefined in (a, b):'
b"-            return float('nan')"
b"+            return float(u'nan')"
b'         return op(a or 0, b or 0)'
b' '
b'     return wrapped'
b'@@ -45,13 +50,13 @@'
b' '
b' def _js_div(a, b):'
b'     if JS_Undefined in (a, b) or not (a or b):'
b"-        return float('nan')"
b"-    return (a or 0) / b if b else float('inf')"
b"+        return float(u'nan')"
b"+    return (a or 0) / b if b else float(u'inf')"
b' '
b' '
b' def _js_mod(a, b):'
b'     if JS_Undefined in (a, b) or not b:'
b"-        return float('nan')"
b"+        return float(u'nan')"
b'     return (a or 0) % b'
b' '
b' '
b'@@ -59,14 +64,14 @@'
b'     if not b:'
b'         return 1  # even 0 ** 0 !!'
b'     elif JS_Undefined in (a, b):'
b"-        return float('nan')"
b"+        return float(u'nan')"
b'     return (a or 0) ** b'
b' '
b' '
b' def _js_eq_op(op):'
b' '
b'     def wrapped(a, b):'
b'-        if {a, b} <= {None, JS_Undefined}:'
b'+        if set([a, b]) <= set([None, JS_Undefined]):'
b'             return op(a, a)'
b'         return op(a, b)'
b' '
b'@@ -78,16 +83,16 @@'
b'     def wrapped(a, b):'
b'         if JS_Undefined in (a, b):'
b'             return False'
b'-        if isinstance(a, str) or isinstance(b, str):'
b'-            return op(str(a or 0), str(b or 0))'
b'+        if isinstance(a, unicode) or isinstance(b, unicode):'
b'+            return op(unicode(a or 0), unicode(b or 0))'
b'         return op(a or 0, b or 0)'
b' '
b'     return wrapped'
b' '
b' '
b' def _js_ternary(cndn, if_true=True, if_false=False):'
b'-    """Simulate JS\'s ternary operator (cndn?if_true:if_false)"""'
b"-    if cndn in (False, None, 0, '', JS_Undefined):"
b'+    u"""Simulate JS\'s ternary operator (cndn?if_true:if_false)"""'
b"+    if cndn in (False, None, 0, u'', JS_Undefined):"
b'         return if_false'
b'     with contextlib.suppress(TypeError):'
b'         if math.isnan(cndn):  # NB: NaN cannot be checked by membership'
b'@@ -96,22 +101,22 @@'
b' '
b' '
b' # Ref: https://es5.github.io/#x9.8.1'
b'-def js_number_to_string(val: float, radix: int = 10):'
b'+def js_number_to_string(val, radix = 10):'
b'     if radix in (JS_Undefined, None):'
b'         radix = 10'
b"-    assert radix in range(2, 37), 'radix must be an integer at least 2 and no greater than 36'"
b"+    assert radix in xrange(2, 37), u'radix must be an integer at least 2 and no greater than 36'"
b' '
b'     if math.isnan(val):'
b"-        return 'NaN'"
b"+        return u'NaN'"
b'     if val == 0:'
b"-        return '0'"
b"+        return u'0'"
b'     if math.isinf(val):'
b"-        return '-Infinity' if val < 0 else 'Infinity'"
b"+        return u'-Infinity' if val < 0 else u'Infinity'"
b'     if radix == 10:'
b'         # TODO: implement special cases'
b'         ...'
b' '
b"-    ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz.-'"
b"+    ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz.-'"
b' '
b'     result = collections.deque()'
b'     sign = val < 0'
b'@@ -128,7 +133,7 @@'
b'         # if we need to round, propagate potential carry through fractional part'
b'         needs_rounding = fraction > 0.5 or (fraction == 0.5 and int(digit) & 1)'
b'         if needs_rounding and fraction + delta > 1:'
b'-            for index in reversed(range(1, len(result))):'
b'+            for index in reversed(xrange(1, len(result))):'
b'                 if result[index] + 1 < radix:'
b'                     result[index] += 1'
b'                     break'
b'@@ -147,62 +152,62 @@'
b'     if sign:'
b'         result.appendleft(-1)  # `-`'
b' '
b"-    return bytes(ALPHABET[digit] for digit in result).decode('ascii')"
b"+    return str(ALPHABET[digit] for digit in result).decode(u'ascii')"
b' '
b' '
b' # Ref: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Operator_Precedence'
b' _OPERATORS = {  # None => Defined in JSInterpreter._operator'
b"-    '?': None,"
b"-    '??': None,"
b"-    '||': None,"
b"-    '&&': None,"
b'-'
b"-    '|': _js_bit_op(operator.or_),"
b"-    '^': _js_bit_op(operator.xor),"
b"-    '&': _js_bit_op(operator.and_),"
b'-'
b"-    '===': operator.is_,"
b"-    '!==': operator.is_not,"
b"-    '==': _js_eq_op(operator.eq),"
b"-    '!=': _js_eq_op(operator.ne),"
b'-'
b"-    '<=': _js_comp_op(operator.le),"
b"-    '>=': _js_comp_op(operator.ge),"
b"-    '<': _js_comp_op(operator.lt),"
b"-    '>': _js_comp_op(operator.gt),"
b'-'
b"-    '>>': _js_bit_op(operator.rshift),"
b"-    '<<': _js_bit_op(operator.lshift),"
b'-'
b"-    '+': _js_arith_op(operator.add),"
b"-    '-': _js_arith_op(operator.sub),"
b'-'
b"-    '*': _js_arith_op(operator.mul),"
b"-    '%': _js_mod,"
b"-    '/': _js_div,"
b"-    '**': _js_exp,"
b"+    u'?': None,"
b"+    u'??': None,"
b"+    u'||': None,"
b"+    u'&&': None,"
b'+'
b"+    u'|': _js_bit_op(operator.or_),"
b"+    u'^': _js_bit_op(operator.xor),"
b"+    u'&': _js_bit_op(operator.and_),"
b'+'
b"+    u'===': operator.is_,"
b"+    u'!==': operator.is_not,"
b"+    u'==': _js_eq_op(operator.eq),"
b"+    u'!=': _js_eq_op(operator.ne),"
b'+'
b"+    u'<=': _js_comp_op(operator.le),"
b"+    u'>=': _js_comp_op(operator.ge),"
b"+    u'<': _js_comp_op(operator.lt),"
b"+    u'>': _js_comp_op(operator.gt),"
b'+'
b"+    u'>>': _js_bit_op(operator.rshift),"
b"+    u'<<': _js_bit_op(operator.lshift),"
b'+'
b"+    u'+': _js_arith_op(operator.add),"
b"+    u'-': _js_arith_op(operator.sub),"
b'+'
b"+    u'*': _js_arith_op(operator.mul),"
b"+    u'%': _js_mod,"
b"+    u'/': _js_div,"
b"+    u'**': _js_exp,"
b' }'
b' '
b"-_COMP_OPERATORS = {'===', '!==', '==', '!=', '<=', '>=', '<', '>'}"
b'-'
b"-_NAME_RE = r'[a-zA-Z_$][\\w$]*'"
b"-_MATCHING_PARENS = dict(zip(*zip('()', '{}', '[]')))"
b'-_QUOTES = \'\\\'"/\''
b"-_NESTED_BRACKETS = r'[^[\\]]+(?:\\[[^[\\]]+(?:\\[[^\\]]+\\])?\\])?'"
b'-'
b'-'
b'-class JS_Undefined:'
b"+_COMP_OPERATORS = set([u'===', u'!==', u'==', u'!=', u'<=', u'>=', u'<', u'>'])"
b'+'
b"+_NAME_RE = ur'[a-zA-Z_$][\\w$]*'"
b"+_MATCHING_PARENS = dict(izip(*izip(u'()', u'{}', u'[]')))"
b'+_QUOTES = u\'\\\'"/\''
b"+_NESTED_BRACKETS = ur'[^[\\]]+(?:\\[[^[\\]]+(?:\\[[^\\]]+\\])?\\])?'"
b'+'
b'+'
b'+class JS_Undefined(object):'
b'     pass'
b' '
b' '
b' class JS_Break(ExtractorError):'
b'     def __init__(self):'
b"-        ExtractorError.__init__(self, 'Invalid break')"
b"+        ExtractorError.__init__(self, u'Invalid break')"
b' '
b' '
b' class JS_Continue(ExtractorError):'
b'     def __init__(self):'
b"-        ExtractorError.__init__(self, 'Invalid continue')"
b"+        ExtractorError.__init__(self, u'Invalid continue')"
b' '
b' '
b' class JS_Throw(ExtractorError):'
b'@@ -220,7 +225,7 @@'
b'         self.maps[0][key] = value'
b' '
b'     def __delitem__(self, key):'
b"-        raise NotImplementedError('Deleting is not supported')"
b"+        raise NotImplementedError(u'Deleting is not supported')"
b' '
b'     def set_local(self, key, value):'
b'         self.maps[0][key] = value'
b'@@ -231,12 +236,14 @@'
b'         return JS_Undefined'
b' '
b' '
b'-class Debugger:'
b'+class Debugger(object):'
b'     import sys'
b"-    ENABLED = False and 'pytest' in sys.modules"
b"+    ENABLED = False and u'pytest' in sys.modules"
b' '
b'     @staticmethod'
b'-    def write(*args, level=100):'
b'+    def write(*args, **_3to2kwargs):'
b"+        if 'level' in _3to2kwargs: level = _3to2kwargs['level']; del _3to2kwargs['level']"
b'+        else: level = 100'
b'         write_string(f\'[debug] JS: {"  " * (100 - level)}\''
b'                      f\'{" ".join(truncate_string(str(x), 50, 50) for x in args)}\\n\')'
b' '
b'@@ -247,33 +254,33 @@'
b'                 cls.write(stmt, level=allow_recursion)'
b'             try:'
b'                 ret, should_ret = f(self, stmt, local_vars, allow_recursion, *args, **kwargs)'
b'-            except Exception as e:'
b'+            except Exception, e:'
b'                 if cls.ENABLED:'
b'                     if isinstance(e, ExtractorError):'
b'                         e = e.orig_msg'
b"-                    cls.write('=> Raises:', e, '<-|', stmt, level=allow_recursion)"
b"+                    cls.write(u'=> Raises:', e, u'<-|', stmt, level=allow_recursion)"
b'                 raise'
b'             if cls.ENABLED and stmt.strip():'
b'                 if should_ret or repr(ret) != stmt:'
b"-                    cls.write(['->', '=>'][should_ret], repr(ret), '<-|', stmt, level=allow_recursion)"
b"+                    cls.write([u'->', u'=>'][should_ret], repr(ret), u'<-|', stmt, level=allow_recursion)"
b'             return ret, should_ret'
b'         return interpret_statement'
b' '
b' '
b'-class JSInterpreter:'
b'+class JSInterpreter(object):'
b'     __named_object_counter = 0'
b' '
b'     _RE_FLAGS = {'
b"         # special knowledge: Python's re flags are bitmask values, current max 128"
b'         # invent new bitmask values well above that for literal parsing'
b'         # TODO: new pattern class to execute matches with these flags'
b"-        'd': 1024,  # Generate indices for substring matches"
b"-        'g': 2048,  # Global search"
b"-        'i': re.I,  # Case-insensitive search"
b"-        'm': re.M,  # Multi-line search"
b"-        's': re.S,  # Allows . to match newline characters"
b"-        'u': re.U,  # Treat a pattern as a sequence of unicode code points"
b'-        \'y\': 4096,  # Perform a "sticky" search that matches starting at the current position in the target string'
b"+        u'd': 1024,  # Generate indices for substring matches"
b"+        u'g': 2048,  # Global search"
b"+        u'i': re.I,  # Case-insensitive search"
b"+        u'm': re.M,  # Multi-line search"
b"+        u's': re.S,  # Allows . to match newline characters"
b"+        u'u': re.U,  # Treat a pattern as a sequence of unicode code points"
b'+        u\'y\': 4096,  # Perform a "sticky" search that matches starting at the current position in the target string'
b'     }'
b' '
b'     def __init__(self, code, objects=None):'
b'@@ -285,7 +292,7 @@'
b'         def __init__(self, msg, expr=None, *args, **kwargs):'
b'             if expr is not None:'
b"                 msg = f'{msg.rstrip()} in: {truncate_string(expr, 50, 50)}'"
b'-            super().__init__(msg, *args, **kwargs)'
b'+            super(Exception, self).__init__(msg, *args, **kwargs)'
b' '
b'     def _named_object(self, namespace, obj):'
b'         self.__named_object_counter += 1'
b'@@ -307,8 +314,8 @@'
b'         return flags, expr[idx + 1:]'
b' '
b'     @staticmethod'
b"-    def _separate(expr, delim=',', max_split=None):"
b"-        OP_CHARS = '+-*/%&|^=<>!,;{}:['"
b"+    def _separate(expr, delim=u',', max_split=None):"
b"+        OP_CHARS = u'+-*/%&|^=<>!,;{}:['"
b'         if not expr:'
b'             return'
b'         counters = dict.fromkeys(_MATCHING_PARENS.values(), 0)'
b'@@ -323,13 +330,13 @@'
b'                     counters[char] -= 1'
b'             elif not escaping:'
b'                 if char in _QUOTES and in_quote in (char, None):'
b"-                    if in_quote or after_op or char != '/':"
b"+                    if in_quote or after_op or char != u'/':"
b'                         in_quote = None if in_quote and not in_regex_char_group else char'
b"-                elif in_quote == '/' and char in '[]':"
b"-                    in_regex_char_group = char == '['"
b"-            escaping = not escaping and in_quote and char == '\\\\'"
b"+                elif in_quote == u'/' and char in u'[]':"
b"+                    in_regex_char_group = char == u'['"
b"+            escaping = not escaping and in_quote and char == u'\\\\'"
b'             in_unary_op = (not in_quote and not in_regex_char_group'
b"-                           and after_op not in (True, False) and char in '-+')"
b"+                           and after_op not in (True, False) and char in u'-+')"
b'             after_op = char if (not in_quote and char in OP_CHARS) else (char.isspace() and after_op)'
b' '
b'             if char != delim[pos] or any(counters.values()) or in_quote or in_unary_op:'
b'@@ -355,14 +362,14 @@'
b'         return separated[0][1:].strip(), separated[1].strip()'
b' '
b'     def _operator(self, op, left_val, right_expr, expr, local_vars, allow_recursion):'
b"-        if op in ('||', '&&'):"
b"-            if (op == '&&') ^ _js_ternary(left_val):"
b"+        if op in (u'||', u'&&'):"
b"+            if (op == u'&&') ^ _js_ternary(left_val):"
b'                 return left_val  # short circuiting'
b"-        elif op == '??':"
b"+        elif op == u'??':"
b'             if left_val not in (None, JS_Undefined):'
b'                 return left_val'
b"-        elif op == '?':"
b"-            right_expr = _js_ternary(left_val, *self._separate(right_expr, ':', 1))"
b"+        elif op == u'?':"
b"+            right_expr = _js_ternary(left_val, *self._separate(right_expr, u':', 1))"
b' '
b'         right_val = self.interpret_expression(right_expr, local_vars, allow_recursion)'
b'         if not _OPERATORS.get(op):'
b'@@ -370,15 +377,15 @@'
b' '
b'         try:'
b'             return _OPERATORS[op](left_val, right_val)'
b'-        except Exception as e:'
b'+        except Exception, e:'
b"             raise self.Exception(f'Failed to evaluate {left_val!r} {op} {right_val!r}', expr, cause=e)"
b' '
b'     def _index(self, obj, idx, allow_undefined=False):'
b"-        if idx == 'length':"
b"+        if idx == u'length':"
b'             return len(obj)'
b'         try:'
b'             return obj[int(idx)] if isinstance(obj, list) else obj[idx]'
b'-        except Exception as e:'
b'+        except Exception, e:'
b'             if allow_undefined:'
b'                 return JS_Undefined'
b"             raise self.Exception(f'Cannot get index {idx}', repr(obj), cause=e)"
b'@@ -392,11 +399,11 @@'
b'     @Debugger.wrap_interpreter'
b'     def interpret_statement(self, stmt, local_vars, allow_recursion=100, _is_var_declaration=False):'
b'         if allow_recursion < 0:'
b"-            raise self.Exception('Recursion limit reached')"
b"+            raise self.Exception(u'Recursion limit reached')"
b'         allow_recursion -= 1'
b' '
b'         should_return = False'
b"-        sub_statements = list(self._separate(stmt, ';')) or ['']"
b"+        sub_statements = list(self._separate(stmt, u';')) or [u'']"
b'         expr = stmt = sub_statements.pop().strip()'
b' '
b'         for sub_stmt in sub_statements:'
b'@@ -404,19 +411,19 @@'
b'             if should_return:'
b'                 return ret, should_return'
b' '
b'-        m = re.match(r\'(?P<var>(?:var|const|let)\\s)|return(?:\\s+|(?=["\\\'])|$)|(?P<throw>throw\\s+)\', stmt)'
b'+        m = re.match(ur\'(?P<var>(?:var|const|let)\\s)|return(?:\\s+|(?=["\\\'])|$)|(?P<throw>throw\\s+)\', stmt)'
b'         if m:'
b'             expr = stmt[len(m.group(0)):].strip()'
b"-            if m.group('throw'):"
b"+            if m.group(u'throw'):"
b'                 raise JS_Throw(self.interpret_expression(expr, local_vars, allow_recursion))'
b"-            should_return = not m.group('var')"
b"-            _is_var_declaration = _is_var_declaration or bool(m.group('var'))"
b"+            should_return = not m.group(u'var')"
b"+            _is_var_declaration = _is_var_declaration or bool(m.group(u'var'))"
b'         if not expr:'
b'             return None, should_return'
b' '
b'         if expr[0] in _QUOTES:'
b'             inner, outer = self._separate(expr, expr[0], 1)'
b"-            if expr[0] == '/':"
b"+            if expr[0] == u'/':"
b'                 flags, outer = self._regex_flags(outer)'
b"                 # We don't support regex methods yet, so no point compiling it"
b"                 inner = f'{inner}/{flags}'"
b'@@ -428,9 +435,9 @@'
b'                 return inner, should_return'
b'             expr = self._named_object(local_vars, inner) + outer'
b' '
b"-        if expr.startswith('new '):"
b"+        if expr.startswith(u'new '):"
b'             obj = expr[4:]'
b"-            if obj.startswith('Date('):"
b"+            if obj.startswith(u'Date('):"
b'                 left, right = self._separate_at_paren(obj[4:])'
b'                 date = unified_timestamp('
b'                     self.interpret_expression(left, local_vars, allow_recursion), False)'
b'@@ -440,14 +447,14 @@'
b'             else:'
b"                 raise self.Exception(f'Unsupported object {obj}', expr)"
b' '
b"-        if expr.startswith('void '):"
b"+        if expr.startswith(u'void '):"
b'             left = self.interpret_expression(expr[5:], local_vars, allow_recursion)'
b'             return None, should_return'
b' '
b"-        if expr.startswith('{'):"
b"+        if expr.startswith(u'{'):"
b'             inner, outer = self._separate_at_paren(expr)'
b'             # try for object expression (Map)'
b"-            sub_expressions = [list(self._separate(sub_expr.strip(), ':', 1)) for sub_expr in self._separate(inner)]"
b"+            sub_expressions = [list(self._separate(sub_expr.strip(), u':', 1)) for sub_expr in self._separate(inner)]"
b'             if all(len(sub_expr) == 2 for sub_expr in sub_expressions):'
b'                 def dict_item(key, val):'
b'                     val = self.interpret_expression(val, local_vars, allow_recursion)'
b'@@ -463,7 +470,7 @@'
b'             else:'
b'                 expr = self._dump(inner, local_vars) + outer'
b' '
b"-        if expr.startswith('('):"
b"+        if expr.startswith(u'('):"
b'             inner, outer = self._separate_at_paren(expr)'
b'             inner, should_abort = self.interpret_statement(inner, local_vars, allow_recursion)'
b'             if not outer or should_abort:'
b'@@ -471,26 +478,26 @@'
b'             else:'
b'                 expr = self._dump(inner, local_vars) + outer'
b' '
b"-        if expr.startswith('['):"
b"+        if expr.startswith(u'['):"
b'             inner, outer = self._separate_at_paren(expr)'
b'             name = self._named_object(local_vars, ['
b'                 self.interpret_expression(item, local_vars, allow_recursion)'
b'                 for item in self._separate(inner)])'
b'             expr = name + outer'
b' '
b"-        m = re.match(r'''(?x)"
b"+        m = re.match(ur'''(?x)"
b'                 (?P<try>try)\\s*\\{|'
b'                 (?P<if>if)\\s*\\(|'
b'                 (?P<switch>switch)\\s*\\(|'
b'                 (?P<for>for)\\s*\\('
b"                 ''', expr)"
b'         md = m.groupdict() if m else {}'
b"-        if md.get('if'):"
b"+        if md.get(u'if'):"
b'             cndn, expr = self._separate_at_paren(expr[m.end() - 1:])'
b'             if_expr, expr = self._separate_at_paren(expr.lstrip())'
b'             # TODO: "else if" is not handled'
b'             else_expr = None'
b"-            m = re.match(r'else\\s*{', expr)"
b"+            m = re.match(ur'else\\s*{', expr)"
b'             if m:'
b'                 else_expr, expr = self._separate_at_paren(expr[m.end() - 1:])'
b'             cndn = _js_ternary(self.interpret_expression(cndn, local_vars, allow_recursion))'
b'@@ -499,14 +506,14 @@'
b'             if should_abort:'
b'                 return ret, True'
b' '
b"-        if md.get('try'):"
b"+        if md.get(u'try'):"
b'             try_expr, expr = self._separate_at_paren(expr[m.end() - 1:])'
b'             err = None'
b'             try:'
b'                 ret, should_abort = self.interpret_statement(try_expr, local_vars, allow_recursion)'
b'                 if should_abort:'
b'                     return ret, True'
b'-            except Exception as e:'
b'+            except Exception, e:'
b'                 # XXX: This works for now, but makes debugging future issues very hard'
b'                 err = e'
b' '
b'@@ -516,12 +523,12 @@'
b'                 sub_expr, expr = self._separate_at_paren(expr[m.end() - 1:])'
b'                 if err:'
b'                     catch_vars = {}'
b"-                    if m.group('err'):"
b"-                        catch_vars[m.group('err')] = err.error if isinstance(err, JS_Throw) else err"
b"+                    if m.group(u'err'):"
b"+                        catch_vars[m.group(u'err')] = err.error if isinstance(err, JS_Throw) else err"
b'                     catch_vars = local_vars.new_child(catch_vars)'
b'                     err, pending = None, self.interpret_statement(sub_expr, catch_vars, allow_recursion)'
b' '
b"-            m = re.match(r'finally\\s*\\{', expr)"
b"+            m = re.match(ur'finally\\s*\\{', expr)"
b'             if m:'
b'                 sub_expr, expr = self._separate_at_paren(expr[m.end() - 1:])'
b'                 ret, should_abort = self.interpret_statement(sub_expr, local_vars, allow_recursion)'
b'@@ -535,19 +542,19 @@'
b'             if err:'
b'                 raise err'
b' '
b"-        elif md.get('for'):"
b"+        elif md.get(u'for'):"
b'             constructor, remaining = self._separate_at_paren(expr[m.end() - 1:])'
b"-            if remaining.startswith('{'):"
b"+            if remaining.startswith(u'{'):"
b'                 body, expr = self._separate_at_paren(remaining)'
b'             else:'
b"-                switch_m = re.match(r'switch\\s*\\(', remaining)  # FIXME: ?"
b"+                switch_m = re.match(ur'switch\\s*\\(', remaining)  # FIXME: ?"
b'                 if switch_m:'
b'                     switch_val, remaining = self._separate_at_paren(remaining[switch_m.end() - 1:])'
b"-                    body, expr = self._separate_at_paren(remaining, '}')"
b"-                    body = 'switch(%s){%s}' % (switch_val, body)"
b"+                    body, expr = self._separate_at_paren(remaining, u'}')"
b"+                    body = u'switch(%s){%s}' % (switch_val, body)"
b'                 else:'
b"-                    body, expr = remaining, ''"
b"-            start, cndn, increment = self._separate(constructor, ';')"
b"+                    body, expr = remaining, u''"
b"+            start, cndn, increment = self._separate(constructor, u';')"
b'             self.interpret_expression(start, local_vars, allow_recursion)'
b'             while True:'
b'                 if not _js_ternary(self.interpret_expression(cndn, local_vars, allow_recursion)):'
b'@@ -562,19 +569,19 @@'
b'                     pass'
b'                 self.interpret_expression(increment, local_vars, allow_recursion)'
b' '
b"-        elif md.get('switch'):"
b"+        elif md.get(u'switch'):"
b'             switch_val, remaining = self._separate_at_paren(expr[m.end() - 1:])'
b'             switch_val = self.interpret_expression(switch_val, local_vars, allow_recursion)'
b"-            body, expr = self._separate_at_paren(remaining, '}')"
b"-            items = body.replace('default:', 'case default:').split('case ')[1:]"
b"+            body, expr = self._separate_at_paren(remaining, u'}')"
b"+            items = body.replace(u'default:', u'case default:').split(u'case ')[1:]"
b'             for default in (False, True):'
b'                 matched = False'
b'                 for item in items:'
b"-                    case, stmt = (i.strip() for i in self._separate(item, ':', 1))"
b"+                    case, stmt = (i.strip() for i in self._separate(item, u':', 1))"
b'                     if default:'
b"-                        matched = matched or case == 'default'"
b"+                        matched = matched or case == u'default'"
b'                     elif not matched:'
b"-                        matched = (case != 'default'"
b"+                        matched = (case != u'default'"
b'                                    and switch_val == self.interpret_expression(case, local_vars, allow_recursion))'
b'                     if not matched:'
b'                         continue'
b'@@ -607,36 +614,36 @@'
b'                 =(?!=)(?P<expr>.*)$'
b"             ''', expr)"
b'         if m:  # We are assigning a value to a variable'
b"-            left_val = local_vars.get(m.group('out'))"
b'-'
b"-            if not m.group('index'):"
b"+            left_val = local_vars.get(m.group(u'out'))"
b'+'
b"+            if not m.group(u'index'):"
b'                 eval_result = self._operator('
b"-                    m.group('op'), left_val, m.group('expr'), expr, local_vars, allow_recursion)"
b"+                    m.group(u'op'), left_val, m.group(u'expr'), expr, local_vars, allow_recursion)"
b'                 if _is_var_declaration:'
b"-                    local_vars.set_local(m.group('out'), eval_result)"
b"+                    local_vars.set_local(m.group(u'out'), eval_result)"
b'                 else:'
b"-                    local_vars[m.group('out')] = eval_result"
b"-                return local_vars[m.group('out')], should_return"
b"+                    local_vars[m.group(u'out')] = eval_result"
b"+                return local_vars[m.group(u'out')], should_return"
b'             elif left_val in (None, JS_Undefined):'
b'                 raise self.Exception(f\'Cannot index undefined variable {m.group("out")}\', expr)'
b' '
b"-            idx = self.interpret_expression(m.group('index'), local_vars, allow_recursion)"
b"+            idx = self.interpret_expression(m.group(u'index'), local_vars, allow_recursion)"
b'             if not isinstance(idx, (int, float)):'
b"                 raise self.Exception(f'List index {idx} must be integer', expr)"
b'             idx = int(idx)'
b'             left_val[idx] = self._operator('
b"-                m.group('op'), self._index(left_val, idx), m.group('expr'), expr, local_vars, allow_recursion)"
b"+                m.group(u'op'), self._index(left_val, idx), m.group(u'expr'), expr, local_vars, allow_recursion)"
b'             return left_val[idx], should_return'
b' '
b"         for m in re.finditer(rf'''(?x)"
b'                 (?P<pre_sign>\\+\\+|--)(?P<var1>{_NAME_RE})|'
b"                 (?P<var2>{_NAME_RE})(?P<post_sign>\\+\\+|--)''', expr):"
b"-            var = m.group('var1') or m.group('var2')"
b"+            var = m.group(u'var1') or m.group(u'var2')"
b'             start, end = m.span()'
b"-            sign = m.group('pre_sign') or m.group('post_sign')"
b"+            sign = m.group(u'pre_sign') or m.group(u'post_sign')"
b'             ret = local_vars[var]'
b"-            local_vars[var] += 1 if sign[0] == '+' else -1"
b"-            if m.group('pre_sign'):"
b"+            local_vars[var] += 1 if sign[0] == u'+' else -1"
b"+            if m.group(u'pre_sign'):"
b'                 ret = local_vars[var]'
b'             expr = expr[:start] + self._dump(ret, local_vars) + expr[end:]'
b' '
b'@@ -659,17 +666,17 @@'
b'         if expr.isdigit():'
b'             return int(expr), should_return'
b' '
b"-        elif expr == 'break':"
b"+        elif expr == u'break':"
b'             raise JS_Break'
b"-        elif expr == 'continue':"
b"+        elif expr == u'continue':"
b'             raise JS_Continue'
b"-        elif expr == 'undefined':"
b"+        elif expr == u'undefined':"
b'             return JS_Undefined, should_return'
b"-        elif expr == 'NaN':"
b"-            return float('NaN'), should_return"
b'-'
b"-        elif m and m.group('return'):"
b"-            var = m.group('name')"
b"+        elif expr == u'NaN':"
b"+            return float(u'NaN'), should_return"
b'+'
b"+        elif m and m.group(u'return'):"
b"+            var = m.group(u'name')"
b'             # Declared variables'
b'             if _is_var_declaration:'
b'                 ret = local_vars.get_local(var)'
b'@@ -686,54 +693,54 @@'
b'         with contextlib.suppress(ValueError):'
b'             return json.loads(js_to_json(expr, strict=True)), should_return'
b' '
b"-        if m and m.group('indexing'):"
b"-            val = local_vars[m.group('in')]"
b"-            idx = self.interpret_expression(m.group('idx'), local_vars, allow_recursion)"
b"+        if m and m.group(u'indexing'):"
b"+            val = local_vars[m.group(u'in')]"
b"+            idx = self.interpret_expression(m.group(u'idx'), local_vars, allow_recursion)"
b'             return self._index(val, idx), should_return'
b' '
b'         for op in _OPERATORS:'
b'             separated = list(self._separate(expr, op))'
b'             right_expr = separated.pop()'
b'             while True:'
b"-                if op in '?<>*-' and len(separated) > 1 and not separated[-1].strip():"
b"+                if op in u'?<>*-' and len(separated) > 1 and not separated[-1].strip():"
b'                     separated.pop()'
b"-                elif not (separated and op == '?' and right_expr.startswith('.')):"
b"+                elif not (separated and op == u'?' and right_expr.startswith(u'.')):"
b'                     break'
b"                 right_expr = f'{op}{right_expr}'"
b"-                if op != '-':"
b"+                if op != u'-':"
b"                     right_expr = f'{separated.pop()}{op}{right_expr}'"
b'             if not separated:'
b'                 continue'
b'             left_val = self.interpret_expression(op.join(separated), local_vars, allow_recursion)'
b'             return self._operator(op, left_val, right_expr, expr, local_vars, allow_recursion), should_return'
b' '
b"-        if m and m.group('attribute'):"
b"-            variable, member, nullish = m.group('var', 'member', 'nullish')"
b"+        if m and m.group(u'attribute'):"
b"+            variable, member, nullish = m.group(u'var', u'member', u'nullish')"
b'             if not member:'
b"-                member = self.interpret_expression(m.group('member2'), local_vars, allow_recursion)"
b"+                member = self.interpret_expression(m.group(u'member2'), local_vars, allow_recursion)"
b'             arg_str = expr[m.end():]'
b"-            if arg_str.startswith('('):"
b"+            if arg_str.startswith(u'('):"
b'                 arg_str, remaining = self._separate_at_paren(arg_str)'
b'             else:'
b'                 arg_str, remaining = None, arg_str'
b' '
b'             def assertion(cndn, msg):'
b'-                """ assert, but without risk of getting optimized out """'
b'+                u""" assert, but without risk of getting optimized out """'
b'                 if not cndn:'
b"                     raise self.Exception(f'{member} {msg}', expr)"
b' '
b'             def eval_method():'
b'                 nonlocal member'
b' '
b"-                if (variable, member) == ('console', 'debug'):"
b"+                if (variable, member) == (u'console', u'debug'):"
b'                     if Debugger.ENABLED:'
b"                         Debugger.write(self.interpret_expression(f'[{arg_str}]', local_vars, allow_recursion))"
b'                     return'
b' '
b'                 types = {'
b"-                    'String': str,"
b"-                    'Math': float,"
b"-                    'Array': list,"
b"+                    u'String': unicode,"
b"+                    u'Math': float,"
b"+                    u'Array': list,"
b'                 }'
b'                 obj = local_vars.get(variable, types.get(variable, NO_DEFAULT))'
b'                 if obj is NO_DEFAULT:'
b'@@ -758,92 +765,93 @@'
b'                     for v in self._separate(arg_str)]'
b' '
b'                 # Fixup prototype call'
b"-                if isinstance(obj, type) and member.startswith('prototype.'):"
b"-                    new_member, _, func_prototype = member.partition('.')[2].partition('.')"
b"-                    assertion(argvals, 'takes one or more arguments')"
b"+                if isinstance(obj, type) and member.startswith(u'prototype.'):"
b"+                    new_member, _, func_prototype = member.partition(u'.')[2].partition(u'.')"
b"+                    assertion(argvals, u'takes one or more arguments')"
b"                     assertion(isinstance(argvals[0], obj), f'needs binding to type {obj}')"
b"-                    if func_prototype == 'call':"
b'-                        obj, *argvals = argvals'
b"-                    elif func_prototype == 'apply':"
b"-                        assertion(len(argvals) == 2, 'takes two arguments')"
b"+                    if func_prototype == u'call':"
b'+                        _3to2list = list(argvals)'
b'+                        obj, argvals, = _3to2list[:1] + [_3to2list[1:]]'
b"+                    elif func_prototype == u'apply':"
b"+                        assertion(len(argvals) == 2, u'takes two arguments')"
b'                         obj, argvals = argvals'
b"-                        assertion(isinstance(argvals, list), 'second argument needs to be a list')"
b"+                        assertion(isinstance(argvals, list), u'second argument needs to be a list')"
b'                     else:'
b"                         raise self.Exception(f'Unsupported Function method {func_prototype}', expr)"
b'                     member = new_member'
b' '
b'-                if obj is str:'
b"-                    if member == 'fromCharCode':"
b"-                        assertion(argvals, 'takes one or more arguments')"
b"-                        return ''.join(map(chr, argvals))"
b'+                if obj is unicode:'
b"+                    if member == u'fromCharCode':"
b"+                        assertion(argvals, u'takes one or more arguments')"
b"+                        return u''.join(imap(unichr, argvals))"
b"                     raise self.Exception(f'Unsupported String method {member}', expr)"
b'                 elif obj is float:'
b"-                    if member == 'pow':"
b"-                        assertion(len(argvals) == 2, 'takes two arguments')"
b"+                    if member == u'pow':"
b"+                        assertion(len(argvals) == 2, u'takes two arguments')"
b'                         return argvals[0] ** argvals[1]'
b"                     raise self.Exception(f'Unsupported Math method {member}', expr)"
b' '
b"-                if member == 'split':"
b"-                    assertion(argvals, 'takes one or more arguments')"
b"-                    assertion(len(argvals) == 1, 'with limit argument is not implemented')"
b"+                if member == u'split':"
b"+                    assertion(argvals, u'takes one or more arguments')"
b"+                    assertion(len(argvals) == 1, u'with limit argument is not implemented')"
b'                     return obj.split(argvals[0]) if argvals[0] else list(obj)'
b"-                elif member == 'join':"
b"-                    assertion(isinstance(obj, list), 'must be applied on a list')"
b"-                    assertion(len(argvals) == 1, 'takes exactly one argument')"
b"+                elif member == u'join':"
b"+                    assertion(isinstance(obj, list), u'must be applied on a list')"
b"+                    assertion(len(argvals) == 1, u'takes exactly one argument')"
b'                     return argvals[0].join(obj)'
b"-                elif member == 'reverse':"
b"-                    assertion(not argvals, 'does not take any arguments')"
b"+                elif member == u'reverse':"
b"+                    assertion(not argvals, u'does not take any arguments')"
b'                     obj.reverse()'
b'                     return obj'
b"-                elif member == 'slice':"
b"-                    assertion(isinstance(obj, (list, str)), 'must be applied on a list or string')"
b"-                    assertion(len(argvals) <= 2, 'takes between 0 and 2 arguments')"
b"+                elif member == u'slice':"
b"+                    assertion(isinstance(obj, (list, unicode)), u'must be applied on a list or string')"
b"+                    assertion(len(argvals) <= 2, u'takes between 0 and 2 arguments')"
b'                     return obj[slice(*argvals, None)]'
b"-                elif member == 'splice':"
b"-                    assertion(isinstance(obj, list), 'must be applied on a list')"
b"-                    assertion(argvals, 'takes one or more arguments')"
b'-                    index, how_many = map(int, ([*argvals, len(obj)])[:2])'
b"+                elif member == u'splice':"
b"+                    assertion(isinstance(obj, list), u'must be applied on a list')"
b"+                    assertion(argvals, u'takes one or more arguments')"
b'+                    index, how_many = imap(int, ([*argvals, len(obj)])[:2])'
b'                     if index < 0:'
b'                         index += len(obj)'
b'                     add_items = argvals[2:]'
b'                     res = []'
b'-                    for _ in range(index, min(index + how_many, len(obj))):'
b'+                    for _ in xrange(index, min(index + how_many, len(obj))):'
b'                         res.append(obj.pop(index))'
b'                     for i, item in enumerate(add_items):'
b'                         obj.insert(index + i, item)'
b'                     return res'
b"-                elif member == 'unshift':"
b"-                    assertion(isinstance(obj, list), 'must be applied on a list')"
b"-                    assertion(argvals, 'takes one or more arguments')"
b"+                elif member == u'unshift':"
b"+                    assertion(isinstance(obj, list), u'must be applied on a list')"
b"+                    assertion(argvals, u'takes one or more arguments')"
b'                     for item in reversed(argvals):'
b'                         obj.insert(0, item)'
b'                     return obj'
b"-                elif member == 'pop':"
b"-                    assertion(isinstance(obj, list), 'must be applied on a list')"
b"-                    assertion(not argvals, 'does not take any arguments')"
b"+                elif member == u'pop':"
b"+                    assertion(isinstance(obj, list), u'must be applied on a list')"
b"+                    assertion(not argvals, u'does not take any arguments')"
b'                     if not obj:'
b'                         return'
b'                     return obj.pop()'
b"-                elif member == 'push':"
b"-                    assertion(argvals, 'takes one or more arguments')"
b"+                elif member == u'push':"
b"+                    assertion(argvals, u'takes one or more arguments')"
b'                     obj.extend(argvals)'
b'                     return obj'
b"-                elif member == 'forEach':"
b"-                    assertion(argvals, 'takes one or more arguments')"
b"-                    assertion(len(argvals) <= 2, 'takes at-most 2 arguments')"
b"-                    f, this = ([*argvals, ''])[:2]"
b"-                    return [f((item, idx, obj), {'this': this}, allow_recursion) for idx, item in enumerate(obj)]"
b"-                elif member == 'indexOf':"
b"-                    assertion(argvals, 'takes one or more arguments')"
b"-                    assertion(len(argvals) <= 2, 'takes at-most 2 arguments')"
b"+                elif member == u'forEach':"
b"+                    assertion(argvals, u'takes one or more arguments')"
b"+                    assertion(len(argvals) <= 2, u'takes at-most 2 arguments')"
b"+                    f, this = ([*argvals, u''])[:2]"
b"+                    return [f((item, idx, obj), {u'this': this}, allow_recursion) for idx, item in enumerate(obj)]"
b"+                elif member == u'indexOf':"
b"+                    assertion(argvals, u'takes one or more arguments')"
b"+                    assertion(len(argvals) <= 2, u'takes at-most 2 arguments')"
b'                     idx, start = ([*argvals, 0])[:2]'
b'                     try:'
b'                         return obj.index(idx, start)'
b'                     except ValueError:'
b'                         return -1'
b"-                elif member == 'charCodeAt':"
b"-                    assertion(isinstance(obj, str), 'must be applied on a string')"
b"-                    assertion(len(argvals) == 1, 'takes exactly one argument')"
b"+                elif member == u'charCodeAt':"
b"+                    assertion(isinstance(obj, unicode), u'must be applied on a string')"
b"+                    assertion(len(argvals) == 1, u'takes exactly one argument')"
b'                     idx = argvals[0] if isinstance(argvals[0], int) else 0'
b'                     if idx >= len(obj):'
b'                         return None'
b'@@ -860,10 +868,10 @@'
b'             else:'
b'                 return eval_method(), should_return'
b' '
b"-        elif m and m.group('function'):"
b"-            fname = m.group('fname')"
b"+        elif m and m.group(u'function'):"
b"+            fname = m.group(u'fname')"
b'             argvals = [self.interpret_expression(v, local_vars, allow_recursion)'
b"-                       for v in self._separate(m.group('args'))]"
b"+                       for v in self._separate(m.group(u'args'))]"
b'             if fname in local_vars:'
b'                 return local_vars[fname](argvals, allow_recursion=allow_recursion), should_return'
b'             elif fname not in self._functions:'
b'@@ -876,14 +884,14 @@'
b'     def interpret_expression(self, expr, local_vars, allow_recursion):'
b'         ret, should_return = self.interpret_statement(expr, local_vars, allow_recursion)'
b'         if should_return:'
b"-            raise self.Exception('Cannot return from an expression', expr)"
b"+            raise self.Exception(u'Cannot return from an expression', expr)"
b'         return ret'
b' '
b'     def extract_object(self, objname, *global_stack):'
b'-        _FUNC_NAME_RE = r\'\'\'(?:[a-zA-Z$0-9]+|"[a-zA-Z$0-9]+"|\'[a-zA-Z$0-9]+\')\'\'\''
b'+        _FUNC_NAME_RE = ur\'\'\'(?:[a-zA-Z$0-9]+|"[a-zA-Z$0-9]+"|\'[a-zA-Z$0-9]+\')\'\'\''
b'         obj = {}'
b'         obj_m = re.search('
b"-            r'''(?x)"
b"+            ur'''(?x)"
b'                 (?<![a-zA-Z$0-9.])%s\\s*=\\s*{\\s*'
b'                     (?P<fields>(%s\\s*:\\s*function\\s*\\(.*?\\)\\s*{.*?}(?:,\\s*)?)*)'
b'                 }\\s*;'
b'@@ -891,37 +899,37 @@'
b'             self.code)'
b'         if not obj_m:'
b"             raise self.Exception(f'Could not find object {objname}')"
b"-        fields = obj_m.group('fields')"
b"+        fields = obj_m.group(u'fields')"
b'         # Currently, it only supports function definitions'
b'         fields_m = re.finditer('
b"-            r'''(?x)"
b"+            ur'''(?x)"
b'                 (?P<key>%s)\\s*:\\s*function\\s*\\((?P<args>(?:%s|,)*)\\){(?P<code>[^}]+)}'
b"             ''' % (_FUNC_NAME_RE, _NAME_RE),"
b'             fields)'
b'         for f in fields_m:'
b"-            argnames = f.group('args').split(',')"
b"-            name = remove_quotes(f.group('key'))"
b"+            argnames = f.group(u'args').split(u',')"
b"+            name = remove_quotes(f.group(u'key'))"
b'             obj[name] = function_with_repr('
b"-                self.build_function(argnames, f.group('code'), *global_stack), f'F<{name}>')"
b"+                self.build_function(argnames, f.group(u'code'), *global_stack), f'F<{name}>')"
b' '
b'         return obj'
b' '
b'     def extract_function_code(self, funcname):'
b'-        """ @returns argnames, code """'
b'+        u""" @returns argnames, code """'
b'         func_m = re.search('
b"-            r'''(?xs)"
b"+            ur'''(?xs)"
b'                 (?:'
b'                     function\\s+%(name)s|'
b'                     [{;,]\\s*%(name)s\\s*=\\s*function|'
b'                     (?:var|const|let)\\s+%(name)s\\s*=\\s*function'
b'                 )\\s*'
b'                 \\((?P<args>[^)]*)\\)\\s*'
b"-                (?P<code>{.+})''' % {'name': re.escape(funcname)},"
b"+                (?P<code>{.+})''' % {u'name': re.escape(funcname)},"
b'             self.code)'
b'         if func_m is None:'
b'             raise self.Exception(f\'Could not find JS function "{funcname}"\')'
b"-        code, _ = self._separate_at_paren(func_m.group('code'))"
b"-        return [x.strip() for x in func_m.group('args').split(',')], code"
b"+        code, _ = self._separate_at_paren(func_m.group(u'code'))"
b"+        return [x.strip() for x in func_m.group(u'args').split(u',')], code"
b' '
b'     def extract_function(self, funcname, *global_stack):'
b'         return function_with_repr('
b'@@ -931,13 +939,13 @@'
b'     def extract_function_from_code(self, argnames, code, *global_stack):'
b'         local_vars = {}'
b'         while True:'
b"-            mobj = re.search(r'function\\((?P<args>[^)]*)\\)\\s*{', code)"
b"+            mobj = re.search(ur'function\\((?P<args>[^)]*)\\)\\s*{', code)"
b'             if mobj is None:'
b'                 break'
b'             start, body_start = mobj.span()'
b'             body, remaining = self._separate_at_paren(code[body_start - 1:])'
b'             name = self._named_object(local_vars, self.extract_function_from_code('
b"-                [x.strip() for x in mobj.group('args').split(',')],"
b"+                [x.strip() for x in mobj.group(u'args').split(u',')],"
b'                 body, local_vars, *global_stack))'
b'             code = code[:start] + name + remaining'
b'         return self.build_function(argnames, code, local_vars, *global_stack)'
b'@@ -953,7 +961,7 @@'
b'             global_stack[0].update(itertools.zip_longest(argnames, args, fillvalue=None))'
b'             global_stack[0].update(kwargs)'
b'             var_stack = LocalNameSpace(*global_stack)'
b"-            ret, should_abort = self.interpret_statement(code.replace('\\n', ' '), var_stack, allow_recursion - 1)"
b"+            ret, should_abort = self.interpret_statement(code.replace(u'\\n', u' '), var_stack, allow_recursion - 1)"
b'             if should_abort:'
b'                 return ret'
b'         return resf'
