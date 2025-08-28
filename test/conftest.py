b'--- ./test/conftest.py\t(original)'
b'+++ ./test/conftest.py\t(refactored)'
b'@@ -1,3 +1,4 @@'
b'+from __future__ import absolute_import'
b' import inspect'
b' '
b' import pytest'
b'@@ -9,7 +10,7 @@'
b' '
b' @pytest.fixture'
b' def handler(request):'
b"-    RH_KEY = getattr(request, 'param', None)"
b"+    RH_KEY = getattr(request, u'param', None)"
b'     if not RH_KEY:'
b'         return'
b'     if inspect.isclass(RH_KEY) and issubclass(RH_KEY, RequestHandler):'
b'@@ -23,42 +24,42 @@'
b'         RH_KEY = handler.RH_KEY'
b' '
b'         def __init__(self, **kwargs):'
b'-            super().__init__(logger=FakeLogger, **kwargs)'
b'+            super(HandlerWrapper, self).__init__(logger=FakeLogger, **kwargs)'
b' '
b'     return HandlerWrapper'
b' '
b' '
b' @pytest.fixture(autouse=True)'
b' def skip_handler(request, handler):'
b'-    """usage: pytest.mark.skip_handler(\'my_handler\', \'reason\')"""'
b"-    for marker in request.node.iter_markers('skip_handler'):"
b'+    u"""usage: pytest.mark.skip_handler(\'my_handler\', \'reason\')"""'
b"+    for marker in request.node.iter_markers(u'skip_handler'):"
b'         if marker.args[0] == handler.RH_KEY:'
b"-            pytest.skip(marker.args[1] if len(marker.args) > 1 else '')"
b"+            pytest.skip(marker.args[1] if len(marker.args) > 1 else u'')"
b' '
b' '
b' @pytest.fixture(autouse=True)'
b' def skip_handler_if(request, handler):'
b'-    """usage: pytest.mark.skip_handler_if(\'my_handler\', lambda request: True, \'reason\')"""'
b"-    for marker in request.node.iter_markers('skip_handler_if'):"
b'+    u"""usage: pytest.mark.skip_handler_if(\'my_handler\', lambda request: True, \'reason\')"""'
b"+    for marker in request.node.iter_markers(u'skip_handler_if'):"
b'         if marker.args[0] == handler.RH_KEY and marker.args[1](request):'
b"-            pytest.skip(marker.args[2] if len(marker.args) > 2 else '')"
b"+            pytest.skip(marker.args[2] if len(marker.args) > 2 else u'')"
b' '
b' '
b' @pytest.fixture(autouse=True)'
b' def skip_handlers_if(request, handler):'
b'-    """usage: pytest.mark.skip_handlers_if(lambda request, handler: True, \'reason\')"""'
b"-    for marker in request.node.iter_markers('skip_handlers_if'):"
b'+    u"""usage: pytest.mark.skip_handlers_if(lambda request, handler: True, \'reason\')"""'
b"+    for marker in request.node.iter_markers(u'skip_handlers_if'):"
b'         if handler and marker.args[0](request, handler):'
b"-            pytest.skip(marker.args[1] if len(marker.args) > 1 else '')"
b"+            pytest.skip(marker.args[1] if len(marker.args) > 1 else u'')"
b' '
b' '
b' def pytest_configure(config):'
b'     config.addinivalue_line('
b"-        'markers', 'skip_handler(handler): skip test for the given handler',"
b"+        u'markers', u'skip_handler(handler): skip test for the given handler',"
b'     )'
b'     config.addinivalue_line('
b"-        'markers', 'skip_handler_if(handler): skip test for the given handler if condition is true',"
b"+        u'markers', u'skip_handler_if(handler): skip test for the given handler if condition is true',"
b'     )'
b'     config.addinivalue_line('
b"-        'markers', 'skip_handlers_if(handler): skip test for handlers when the condition is true',"
b"+        u'markers', u'skip_handlers_if(handler): skip test for handlers when the condition is true',"
b'     )'
