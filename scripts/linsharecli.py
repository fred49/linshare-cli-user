#! /usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

# This file is part of Linshare user cli.
#
# LinShare user cli is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinShare user cli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare user cli.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2013 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
import sys
import argparse
import logging
import logging.handlers

from argtoolbox import Config, Element, SimpleSection, DefaultProgram
from argtoolbox import streamHandler, DEFAULT_LOGGING_FORMAT
from argtoolbox import Base64ElementHook, SectionHook
from linshare_cli.user import add_document_parser, add_share_parser
from linshare_cli.user import add_received_share_parser, add_threads_parser
from linshare_cli.user import add_users_parser, add_config_parser
from linshare_cli.user import add_test_parser

# -----------------------------------------------------------------------------
# logs
# -----------------------------------------------------------------------------
g_log = logging.getLogger()
g_log.setLevel(logging.INFO)
# logger handlers
g_log.addHandler(streamHandler)
# debug mode
# if you need debug during class construction, file config loading,
# you just need to export _LINSHARE_CLI_USER_DEBUG=True
if os.getenv('_LINSHARE_CLI_USER_DEBUG', False):
    g_log.setLevel(logging.DEBUG)
    streamHandler.setFormatter(DEFAULT_LOGGING_FORMAT)

# global logger variable
log = logging.getLogger('linshare-cli')

# -----------------------------------------------------------------------------
# create global configuration
# -----------------------------------------------------------------------------
config = Config("linshare-cli",
                desc="""An user cli for LinShare, using its REST API.""")

section_server = config.add_section(SimpleSection("server"))

section_server.add_element(Element(
    'host',
    required=True,
    default='http://localhost:8080/linshare'))

section_server.add_element(Element(
    'realm',
    desc=argparse.SUPPRESS,
    default="Name Of Your LinShare Realm"))

section_server.add_element(Element('user', required=True))

section_server.add_element(Element(
    'password',
    required=True,
    hidden=True,
    desc="user password to linshare",
    hooks=[Base64ElementHook(), ]))

section_server.add_element(Element(
    'application_name',
    default="linshare",
    conf_hidden=True,
    desc="Default value is 'linshare' (example http:/x.x.x.x/linshare)"))

section_server.add_element(Element(
    'nocache',
    e_type=bool,
    default=False,
    desc=argparse.SUPPRESS))

section_server.add_element(Element('verbose'))

section_server.add_element(Element(
    'debug',
    e_type=int,
    default=0,
    desc="""(default: 0)
# 0 : debug off
# 1 : debug on
# 2 : debug on and request result is printed (pretty json)
# 3 : debug on and urllib debug on and http headers and request are printed"""
))

# loading default configuration
config.load()

# -----------------------------------------------------------------------------
# arguments parser
# -----------------------------------------------------------------------------
parser = config.get_parser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument(
    '-d',
    action="count",
    **config.server.debug.get_arg_parse_arguments())

parser.add_argument('-v', '--verbose', action="store_true", default=False)

parser.add_argument('--version', action="version", version="%(prog)s 0.1")

parser.add_argument(
    '-p',
    action="store_true",
    default=False,
    dest="ask_password",
    help="If set, the program will ask you your password.")

parser.add_argument(
    '-s',
    action="store",
    dest='server_section',
    help="""This option let you select the server section in the cfg file
    you want to load (server section is always load first as default
    configuration). You just need to specify a number like '4' for
    section 'server-4'""")

# If section_server is defined, we need to modify the suffix attribute of
# server Section object.
hook = SectionHook(config.server, "_suffix", "server_section")

# Reloading configuration with previous optional arguments
# (ex config file name, server section, ...)
config.reload(hook)

# Adding all others options.
parser.add_argument(
    '-u',
    '--user',
    action="store",
    **config.server.user.get_arg_parse_arguments())

parser.add_argument(
    '-P',
    '--password',
    action="store",
    **config.server.password.get_arg_parse_arguments())

parser.add_argument(
    '-H',
    '--host',
    action="store",
    **config.server.host.get_arg_parse_arguments())

parser.add_argument(
    '-r',
    '--realm',
    action="store",
    **config.server.realm.get_arg_parse_arguments())

parser.add_argument(
    '--nocache',
    action="store_true",
    **config.server.nocache.get_arg_parse_arguments())

parser.add_argument(
    '-a',
    '--appname',
    action="store",
    **config.server.application_name.get_arg_parse_arguments())

# Adding all others parsers.
subparsers = parser.add_subparsers()
add_document_parser(subparsers, "documents", "Documents management")
add_threads_parser(subparsers, "threads", "threads management")
add_share_parser(subparsers, "shares", "Created shares management")
add_received_share_parser(subparsers,
                          "received_shares",
                          "Received shares management")
add_received_share_parser(subparsers,
                          "rshares",
                          "Alias of received_share command")
add_config_parser(
    subparsers,
    "config",
    "Config tools like autocomplete configuration or pref-file generation.",
    config)
add_users_parser(subparsers, "users",  "users")
add_test_parser(subparsers)

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    prog = DefaultProgram(parser, config)
    if prog():
        sys.exit(0)
    else:
        sys.exit(1)