#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/3/16
@desc: ...
"""
# import socket
# from typing import Union, Optional, TYPE_CHECKING, Tuple
#
#
# def select_address_family(host: str) -> int:
#     """Return ``AF_INET4``, ``AF_INET6``, or ``AF_UNIX`` depending on
#     the host and port."""
#     # disabled due to problems with current ipv6 implementations
#     # and various operating systems.  Probably this code also is
#     # not supposed to work, but I can't come up with any other
#     # ways to implement this.
#     # try:
#     #     info = socket.getaddrinfo(host, port, socket.AF_UNSPEC,
#     #                               socket.SOCK_STREAM, 0,
#     #                               socket.AI_PASSIVE)
#     #     if info:
#     #         return info[0][0]
#     # except socket.gaierror:
#     #     pass
#     if host.startswith("unix://"):
#         return socket.AF_UNIX
#     elif ":" in host and hasattr(socket, "AF_INET6"):
#         return socket.AF_INET6
#     return socket.AF_INET


# def get_sockaddr(
#     host: str, port: Optional[int], family: int
# ) -> Union[tuple, str, bytes]:
#     """Return a fully qualified socket address that can be passed to
#     :func:`socket.bind`."""
#     if family == af_unix:
#         return host.split("://", 1)[1]
#     try:
#         res = socket.getaddrinfo(
#             host, port, family, socket.SOCK_STREAM, socket.IPPROTO_TCP
#         )
#     except socket.gaierror:
#         return host, port
#     return res[0][4]