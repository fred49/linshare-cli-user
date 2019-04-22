#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


# This file is part of Linshare cli.
#
# LinShare cli is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinShare cli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare cli.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#

from __future__ import unicode_literals

from linshareapi.cache import Time
from argtoolbox import DefaultCompleter as Completer
from linsharecli.common.core import add_list_parser_options
from linsharecli.common.filters import PartialOr
from linsharecli.admin.core import DefaultCommand
from linsharecli.common.formatters import DateFormatter


class MailConfigsCommand(DefaultCommand):
    """TODO"""

    IDENTIFIER = "name"
    DEFAULT_SORT = "name"
    DEFAULT_SORT_NAME = "name"
    RESOURCE_IDENTIFIER = "uuid"

    # pylint: disable=line-too-long
    DEFAULT_TOTAL = "Mail configs found : %(count)s"
    MSG_RS_NOT_FOUND = "No mail config could be found."
    MSG_RS_DELETED = "%(position)s/%(count)s: The mail config '%(name)s' (%(uuid)s) was deleted. (%(time)s s)"
    MSG_RS_CAN_NOT_BE_DELETED = "The mail config '%(name)s'  '%(uuid)s' can not be deleted."
    MSG_RS_CAN_NOT_BE_DELETED_M = "%(count)s mail config(s) can not be deleted."
    MSG_RS_UPDATED = "The mail config '%(name)s' (%(uuid)s) was successfully updated."
    MSG_RS_CREATED = "The mail config '%(name)s' (%(uuid)s) was successfully created. (%(_time)s s)"

    def complete(self, args, prefix):
        super(MailConfigsCommand, self).__call__(args)
        json_obj = self.ls.public_keys.list()
        return (v.get(self.RESOURCE_IDENTIFIER)
                for v in json_obj if v.get(self.RESOURCE_IDENTIFIER).startswith(prefix))

    # pylint: disable=unused-argument
    def complete_fields(self, args, prefix):
        """TODO"""
        super(MailConfigsCommand, self).__call__(args)
        cli = self.ls.public_keys
        return cli.get_rbu().get_keys(True)

    def complete_domain(self, args, prefix):
        """TODO"""
        super(MailConfigsCommand, self).__call__(args)
        json_obj = self.ls.domains.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


class MailConfigsListCommand(MailConfigsCommand):
    """ List all public keys."""

    @Time('linsharecli.publickeys', label='Global time : %(time)s')
    def __call__(self, args):
        super(MailConfigsListCommand, self).__call__(args)
        cli = self.ls.mail_configs
        table = self.get_table(args, cli, self.IDENTIFIER, args.fields)
        json_obj = cli.list(args.domain, args.parent)
        # Filters
        filters = [PartialOr(self.IDENTIFIER, args.identifiers, True)]
        formatters = [
            DateFormatter('creationDate'),
            DateFormatter('modificationDate')
        ]
        return self._list(args, cli, table, json_obj, formatters=formatters,
                          filters=filters)


def add_parser(subparsers, name, desc, config):
    """Add all mail configs commands."""
    parser_tmp = subparsers.add_parser(name, help=desc)
    subparsers2 = parser_tmp.add_subparsers()

    # command : list
    parser = subparsers2.add_parser(
        'list', help="list mail configs")
    parser.add_argument('identifiers', nargs="*", help="")
    add_list_parser_options(parser, delete=True, cdate=False)
    parser.add_argument('--parent',
                        action="store_true",
                        help="Display also mail configs from parent domains")
    parser.add_argument('--domain',
                       ).completer = Completer("complete_domain")
    parser.set_defaults(__func__=MailConfigsListCommand(config))