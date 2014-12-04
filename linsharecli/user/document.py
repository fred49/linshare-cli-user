#! /usr/bin/env python
# -*- coding: utf-8 -*-


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
# Copyright 2014 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#

from __future__ import unicode_literals

from linshareapi.cache import Time
from linsharecli.user.core import DefaultCommand
from linsharecli.common.filters import PartialOr
from linsharecli.common.filters import PartialDate
from linsharecli.common.formatters import DateFormatter
from linsharecli.common.formatters import SizeFormatter
from argparse import RawTextHelpFormatter
from argtoolbox import DefaultCompleter as Completer


# -----------------------------------------------------------------------------
class DocumentsCommand(DefaultCommand):
    """ List all documents store into LinShare."""
    IDENTIFIER = "name"
    DEFAULT_SORT = "creationDate"
    DEFAULT_SORT_SIZE = "size"
    DEFAULT_TOTAL = "Documents found : %s"
    DEFAULT_SORT_NAME = "name"
    RESOURCE_IDENTIFIER = "uuid"
    MSG_RS_NOT_FOUND = "No documents could be found."
    MSG_RS_DELETED = "The document '%(name)s' (%(uuid)s) was deleted. (%(time)s s)"
    MSG_RS_CAN_NOT_BE_DELETED = "The document '%(uuid)s' can not be deleted."
    MSG_RS_CAN_NOT_BE_DELETED_M = "%s document(s) can not be deleted."
    MSG_RS_DOWNLOADED = "The document '%(name)s' (%(uuid)s) was downloaded. (%(time)s s)"
    MSG_RS_CAN_NOT_BE_DOWNLOADED = "One document can not be downloaded."
    MSG_RS_CAN_NOT_BE_DOWNLOADED_M = "%s documents can not be downloaded."

    def complete(self, args, prefix):
        super(DocumentsCommand, self).__call__(args)
        json_obj = self.ls.documents.list()
        return (
            v.get('uuid') for v in json_obj if v.get('uuid').startswith(prefix))


# -----------------------------------------------------------------------------
class DocumentsListCommand(DocumentsCommand):
    """ List all documents store into LinShare."""

    @Time('linsharecli.document', label='Global time : %s')
    def __call__(self, args):
        super(DocumentsListCommand, self).__call__(args)
        cli = self.ls.documents
        table = self.get_table(args, cli, self.IDENTIFIER)
        json_obj = cli.list()
        # Filters
        filters = [PartialOr(self.IDENTIFIER, args.names, True),
                 PartialDate("creationDate", args.cdate)]
        # Formatters
        formatters = [DateFormatter('creationDate'),
                    DateFormatter('expirationDate'),
                    SizeFormatter('size'),
                    DateFormatter('modificationDate')]
        return self._list(args, cli, table, json_obj, formatters, filters)


# -----------------------------------------------------------------------------
class DocumentsUploadCommand(DefaultCommand):
    """ Upload a file to LinShare using its rest api. return the uploaded
    document uuid  """

    @Time('linsharecli.document', label='Global time : %s')
    def __call__(self, args):
        super(DocumentsUploadCommand, self).__call__(args)

        count = len(args.files)
        position = 0
        for file_path in args.files:
            position += 1
            json_obj = self.ls.documents.upload(file_path, args.description)
            if json_obj:
                json_obj['time'] = self.ls.last_req_time
                json_obj['position'] = position
                json_obj['count'] = count
                self.log.info(
                    "%(position)s/%(count)s: The file '%(name)s' (%(uuid)s) was uploaded. (%(time)ss)",
                    json_obj)


# -----------------------------------------------------------------------------
class DocumentsDownloadCommand(DocumentsCommand):

    @Time('linsharecli.document', label='Global time : %s')
    def __call__(self, args):
        super(DocumentsDownloadCommand, self).__call__(args)
        cli = self.ls.documents
        self._download_all(args, cli, args.uuids)


# -----------------------------------------------------------------------------
class DocumentsDeleteCommand(DocumentsCommand):

    @Time('linsharecli.document', label='Global time : %s')
    def __call__(self, args):
        super(DocumentsDeleteCommand, self).__call__(args)
        cli = self.ls.documents
        self._download_all(args, cli, args.uuids)


# -----------------------------------------------------------------------------
class DocumentsUploadAndSharingCommand(DefaultCommand):

    @Time('linsharecli.document', label='Global time : %s')
    def __call__(self, args):
        super(DocumentsUploadAndSharingCommand, self).__call__(args)

        for file_path in args.files:
            json_obj = self.ls.documents.upload(file_path)
            uuid = json_obj.get('uuid')

            json_obj['time'] = self.ls.last_req_time
            self.log.info(
                "The file '%(name)s' (%(uuid)s) was uploaded. (%(time)ss)",
                json_obj)

            for mail in args.mails:
                code, msg, req_time = self.ls.shares.share(uuid, mail)

                if code == 204:
                    self.log.info(
                        "The document '" + uuid +
                        "' was successfully shared with " + mail +
                        " ( " + req_time + "s)")
                else:
                    self.log.warn("Trying to share document '" +
                                  uuid + "' with " + mail)
                    self.log.error("Unexpected return code : " +
                                   str(code) + " : " + msg)

    def complete(self, args, prefix):
        super(DocumentsUploadAndSharingCommand, self).__call__(args)

        from argcomplete import warn
        if len(prefix) >= 3:
            json_obj = self.ls.users.list()
            return (v.get('mail')
                    for v in json_obj if v.get('mail').startswith(prefix))
        else:
            warn("Completion need at least 3 characters.")

    def complete2(self, args, prefix):
        super(DocumentsUploadAndSharingCommand, self).__call__(args)

        from argcomplete import warn
        if len(prefix) >= 3:
            import re
            json_obj = self.ls.users.list()
            guesses = []
            mails = []
            cpt = 0
            for v in json_obj:
                mail = v.get('mail')
                if re.match(".*" + prefix + ".*", mail):
                    guesses.append(mail)
                if mail.startswith(prefix):
                    cpt += 1
                    mails.append(mail)
                if cpt >= 5:
                    break
            if mails:
                return mails
            else:
                cpt = 0
                warning = ["Some results :"]
                for i in guesses:
                    cpt += 1
                    warning.append(" * " + i + "\n")
                    if cpt >= 4:
                        break
                warn("".join(warning))
                return guesses
        else:
            warn("Completion need at least 3 characters.")


# -----------------------------------------------------------------------------
def add_parser(subparsers, name, desc):
    parser_tmp = subparsers.add_parser(name, help=desc)

    subparsers2 = parser_tmp.add_subparsers()

    parser_tmp2 = subparsers2.add_parser('upload',
                                         help="upload documents to linshare")
    parser_tmp2.set_defaults(__func__=DocumentsUploadCommand())
    parser_tmp2.add_argument('--desc', action="store", dest="description",
                             required=False, help="Optional description.")
    parser_tmp2.add_argument('files', nargs='+')

    parser_tmp2 = subparsers2.add_parser('upshare',
                                         help="upload and share documents")
    parser_tmp2.set_defaults(__func__=DocumentsUploadAndSharingCommand())
    parser_tmp2.add_argument('files', nargs='+')
    parser_tmp2.add_argument('-m',
                             '--mail',
                             action="append",
                             dest="mails",
                             required=True,
                             help="Recipient mails."
                             ).completer = Completer()


    parser_tmp2 = subparsers2.add_parser(
        'download',
        help="download documents from linshare")
    parser_tmp2.set_defaults(__func__=DocumentsDownloadCommand())
    parser_tmp2.add_argument('uuids', nargs='+').completer = Completer()

    parser_tmp2 = subparsers2.add_parser(
        'delete',
        help="delete documents from linshare")
    parser_tmp2.set_defaults(__func__=DocumentsDeleteCommand())
    parser_tmp2.add_argument('uuids', nargs='+').completer = Completer()

    parser_tmp2 = subparsers2.add_parser(
        'list',
        formatter_class=RawTextHelpFormatter,
        help="list documents from linshare")
    parser_tmp2.add_argument('names', nargs="*", help="")
    parser_tmp2.add_argument('--date', action="store", dest="cdate")
    parser_tmp2.add_argument('-r', '--reverse', action="store_true",
                             help="reverse order while sorting")
    parser_tmp2.add_argument('--sort-name', action="store_true",
                             help="sort by file name")
    parser_tmp2.add_argument('--extended', action="store_true",
                             help="extended format")
    parser_tmp2.add_argument('--sort-size', action="store_true",
                             help="sort by file size")
    #parser_tmp2.add_argument('--show-columns', action="store_true",
    #                    help="List all available fields in received data.")
    parser_tmp2.add_argument('-t', '--vertical', action="store_true",
                             help="use vertical output mode")
    parser_tmp2.add_argument('--csv', action="store_true", help="Csv output")
    parser_tmp2.add_argument('--no-headers', action="store_true",
                             help="No headers for csv output")
    parser_tmp2.add_argument('--raw', action="store_true",
                             help="Disable all formatters")
    parser_tmp2.add_argument('--start', action="store", type=int, default=0,
                             help="Print all left rows after the first n rows.")
    parser_tmp2.add_argument('--end', action="store", type=int, default=0,
                             help="Print the last n rows.")
    parser_tmp2.add_argument('--limit', action="store", type=int, default=0,
                             help="Used to limit the number of row to print.")
    parser_tmp2.add_argument('-o', '--output-dir', action="store",
                             dest="directory")
    parser_tmp2.add_argument('-d', '--download', action="store_true")
    parser_tmp2.add_argument('--dry-run', action="store_true")
    parser_tmp2.add_argument('-D', '--delete', action="store_true")
    parser_tmp2.add_argument('-c', '--count', action="store_true",
                             dest="count_only")
    parser_tmp2.set_defaults(__func__=DocumentsListCommand())
