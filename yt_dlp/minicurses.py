b'--- ./yt_dlp/minicurses.py\t(original)'
b'+++ ./yt_dlp/minicurses.py\t(refactored)'
b'@@ -1,37 +1,39 @@'
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import functools'
b' from threading import Lock'
b' '
b' from .utils import supports_terminal_sequences, write_string'
b' '
b' CONTROL_SEQUENCES = {'
b"-    'DOWN': '\\n',"
b"-    'UP': '\\033[A',"
b"-    'ERASE_LINE': '\\033[K',"
b"-    'RESET': '\\033[0m',"
b"+    u'DOWN': u'\\n',"
b"+    u'UP': u'\\033[A',"
b"+    u'ERASE_LINE': u'\\033[K',"
b"+    u'RESET': u'\\033[0m',"
b' }'
b' '
b' '
b' _COLORS = {'
b"-    'BLACK': '0',"
b"-    'RED': '1',"
b"-    'GREEN': '2',"
b"-    'YELLOW': '3',"
b"-    'BLUE': '4',"
b"-    'PURPLE': '5',"
b"-    'CYAN': '6',"
b"-    'WHITE': '7',"
b"+    u'BLACK': u'0',"
b"+    u'RED': u'1',"
b"+    u'GREEN': u'2',"
b"+    u'YELLOW': u'3',"
b"+    u'BLUE': u'4',"
b"+    u'PURPLE': u'5',"
b"+    u'CYAN': u'6',"
b"+    u'WHITE': u'7',"
b' }'
b' '
b' '
b' _TEXT_STYLES = {'
b"-    'NORMAL': '0',"
b"-    'BOLD': '1',"
b"-    'UNDERLINED': '4',"
b"+    u'NORMAL': u'0',"
b"+    u'BOLD': u'1',"
b"+    u'UNDERLINED': u'4',"
b' }'
b' '
b' '
b' def format_text(text, f):'
b"-    '''"
b"+    u'''"
b'     @param f    String representation of formatting to apply in the form:'
b'                 [style] [light] font_color [on [light] bg_color]'
b'                 E.g. "red", "bold green on light blue"'
b'@@ -39,43 +41,43 @@'
b'     f = f.upper()'
b'     tokens = f.strip().split()'
b' '
b"-    bg_color = ''"
b"-    if 'ON' in tokens:"
b"-        if tokens[-1] == 'ON':"
b"+    bg_color = u''"
b"+    if u'ON' in tokens:"
b"+        if tokens[-1] == u'ON':"
b"             raise SyntaxError(f'Empty background format specified in {f!r}')"
b'         if tokens[-1] not in _COLORS:'
b"             raise SyntaxError(f'{tokens[-1]} in {f!r} must be a color')"
b"         bg_color = f'4{_COLORS[tokens.pop()]}'"
b"-        if tokens[-1] == 'LIGHT':"
b"+        if tokens[-1] == u'LIGHT':"
b"             bg_color = f'0;10{bg_color[1:]}'"
b'             tokens.pop()'
b"-        if tokens[-1] != 'ON':"
b"+        if tokens[-1] != u'ON':"
b'             raise SyntaxError(f\'Invalid format {f.split(" ON ", 1)[1]!r} in {f!r}\')'
b"         bg_color = f'\\033[{bg_color}m'"
b'         tokens.pop()'
b' '
b'     if not tokens:'
b"-        fg_color = ''"
b"+        fg_color = u''"
b'     elif tokens[-1] not in _COLORS:'
b"         raise SyntaxError(f'{tokens[-1]} in {f!r} must be a color')"
b'     else:'
b"         fg_color = f'3{_COLORS[tokens.pop()]}'"
b"-        if tokens and tokens[-1] == 'LIGHT':"
b"+        if tokens and tokens[-1] == u'LIGHT':"
b"             fg_color = f'9{fg_color[1:]}'"
b'             tokens.pop()'
b"-        fg_style = tokens.pop() if tokens and tokens[-1] in _TEXT_STYLES else 'NORMAL'"
b"+        fg_style = tokens.pop() if tokens and tokens[-1] in _TEXT_STYLES else u'NORMAL'"
b"         fg_color = f'\\033[{_TEXT_STYLES[fg_style]};{fg_color}m'"
b'         if tokens:'
b'             raise SyntaxError(f\'Invalid format {" ".join(tokens)!r} in {f!r}\')'
b' '
b'     if fg_color or bg_color:'
b"-        text = text.replace(CONTROL_SEQUENCES['RESET'], f'{fg_color}{bg_color}')"
b"+        text = text.replace(CONTROL_SEQUENCES[u'RESET'], f'{fg_color}{bg_color}')"
b'         return f\'{fg_color}{bg_color}{text}{CONTROL_SEQUENCES["RESET"]}\''
b'     else:'
b'         return text'
b' '
b' '
b'-class MultilinePrinterBase:'
b'+class MultilinePrinterBase(object):'
b'     def __init__(self, stream=None, lines=1):'
b'         self.stream = stream'
b'         self.maximum = lines - 1'
b'@@ -99,7 +101,7 @@'
b'         return text'
b' '
b'     def write(self, *text):'
b"-        write_string(''.join(text), self.stream)"
b"+        write_string(u''.join(text), self.stream)"
b' '
b' '
b' class QuietMultilinePrinter(MultilinePrinterBase):'
b'@@ -108,7 +110,7 @@'
b' '
b' class MultilineLogger(MultilinePrinterBase):'
b'     def write(self, *text):'
b"-        self.stream.debug(''.join(text))"
b"+        self.stream.debug(u''.join(text))"
b' '
b'     def print_at_line(self, text, pos):'
b'         # stream is the logger object, not an actual stream'
b'@@ -117,12 +119,12 @@'
b' '
b' class BreaklineStatusPrinter(MultilinePrinterBase):'
b'     def print_at_line(self, text, pos):'
b"-        self.write(self._add_line_number(text, pos), '\\n')"
b"+        self.write(self._add_line_number(text, pos), u'\\n')"
b' '
b' '
b' class MultilinePrinter(MultilinePrinterBase):'
b'     def __init__(self, stream=None, lines=1, preserve_output=True):'
b'-        super().__init__(stream, lines)'
b'+        super(MultilinePrinter, self).__init__(stream, lines)'
b'         self.preserve_output = preserve_output'
b'         self._lastline = self._lastlength = 0'
b'         self._movelock = Lock()'
b'@@ -136,31 +138,31 @@'
b' '
b'     def _move_cursor(self, dest):'
b'         current = min(self._lastline, self.maximum)'
b"-        yield '\\r'"
b"+        yield u'\\r'"
b'         distance = dest - current'
b'         if distance < 0:'
b"-            yield CONTROL_SEQUENCES['UP'] * -distance"
b"+            yield CONTROL_SEQUENCES[u'UP'] * -distance"
b'         elif distance > 0:'
b"-            yield CONTROL_SEQUENCES['DOWN'] * distance"
b"+            yield CONTROL_SEQUENCES[u'DOWN'] * distance"
b'         self._lastline = dest'
b' '
b'     @lock'
b'     def print_at_line(self, text, pos):'
b'         if self._HAVE_FULLCAP:'
b"-            self.write(*self._move_cursor(pos), CONTROL_SEQUENCES['ERASE_LINE'], text)"
b"+            self.write(*self._move_cursor(pos), CONTROL_SEQUENCES[u'ERASE_LINE'], text)"
b'             return'
b' '
b'         text = self._add_line_number(text, pos)'
b'         textlen = len(text)'
b'         if self._lastline == pos:'
b'             # move cursor at the start of progress when writing to same line'
b"-            prefix = '\\r'"
b"+            prefix = u'\\r'"
b'             if self._lastlength > textlen:'
b"-                text += ' ' * (self._lastlength - textlen)"
b"+                text += u' ' * (self._lastlength - textlen)"
b'             self._lastlength = textlen'
b'         else:'
b'             # otherwise, break the line'
b"-            prefix = '\\n'"
b"+            prefix = u'\\n'"
b'             self._lastlength = textlen'
b'         self.write(prefix, text)'
b'         self._lastline = pos'
b'@@ -171,12 +173,12 @@'
b'         # so that other to_screen calls can precede'
b'         text = self._move_cursor(self.maximum) if self._HAVE_FULLCAP else []'
b'         if self.preserve_output:'
b"-            self.write(*text, '\\n')"
b"+            self.write(*text, u'\\n')"
b'             return'
b' '
b'         if self._HAVE_FULLCAP:'
b'             self.write('
b"-                *text, CONTROL_SEQUENCES['ERASE_LINE'],"
b"+                *text, CONTROL_SEQUENCES[u'ERASE_LINE'],"
b'                 f\'{CONTROL_SEQUENCES["UP"]}{CONTROL_SEQUENCES["ERASE_LINE"]}\' * self.maximum)'
b'         else:'
b"-            self.write('\\r', ' ' * self._lastlength, '\\r')"
b"+            self.write(u'\\r', u' ' * self._lastlength, u'\\r')"
