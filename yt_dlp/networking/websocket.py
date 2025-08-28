from __future__ import absolute_import

import abc

from .common import RequestHandler, Response


class WebSocketResponse(Response):

    def send(self, message):
        u"""
        Send a message to the server.

        @param message: The message to send. A string (str) is sent as a text frame, bytes is sent as a binary frame.
        """
        raise NotImplementedError

    def recv(self):
        u"""
        Receive a message from the server.
        """
        raise NotImplementedError


class WebSocketRequestHandler(RequestHandler):
    __metaclass__ = abc.ABCMeta
