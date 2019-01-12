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
from linsharecli.common.formatters import LastAuthorFormatter
from linsharecli.common.core import add_list_parser_options
from linsharecli.common.core import add_delete_parser_options
from linsharecli.common.core import add_download_parser_options
from linshareapi.core import LinShareException
from linshareapi.core import ResourceBuilder
# from argtoolbox import DefaultCompleter as Completer


INVALID_CHARS = [
    (" ", "."),
    (" ", "."),
    ("é", "e"),
    ("è", "e"),
    ("ê", "e"),
    ("à", "a"),
    ("[", "."),
    ("]", "."),
    ("(", "."),
    (")", "."),
    ("{", "."),
    ("}", "."),
    ("'", "."),
    ("!", "."),
    ("?", "."),
    ("¿", "."),
    ("¦", "."),
    ("'", "."),
    ("&", ".and."),
    ("¡", "."),
    ("–", "-"),
    ("—", "-"),
    ("…", "."),
    ("⁄", "."),
    ("#", ""),
    ("@", ""),
    ("’", ""),
    (",", "."),
    (":", "."),
    (";", "."),
    ("...", "."),
    ("..", "."),
]

def format_record_for_autocomplete(row):
    """Build one result from uuid and sanitysed name"""
    uuid = row.get('uuid')
    sep = "@@@"
    name = row.get('name')
    for char, replace in INVALID_CHARS:
        name = name.replace(char, replace)
    return uuid + sep + name.strip(".")

def get_uuid_from(record):
    """TODO"""
    return record.split('@@@')[0]


class WorkgroupCompleter(object):

    def __init__(self, config):
        self.config = config

    def __call__(self, prefix, **kwargs):
        from argcomplete import debug
        try:
            debug("\n------------ ThreadCompleter -----------------")
            debug("Kwargs content :")
            for i, j in kwargs.items():
                debug("key : " + str(i))
                debug("\t - " + str(j))
            debug("\n------------ ThreadCompleter -----------------\n")
            args = kwargs.get('parsed_args')
            # FIXME
            wg_cmd = WgNodeContentListCommand(self.config)
            return wg_cmd.complete_workgroups(args, prefix)
        # pylint: disable-msg=W0703
        except Exception as ex:
            debug("\nERROR:An exception was caught :" + str(ex) + "\n")


class FolderCompleter(object):

    def __init__(self, config):
        self.config = config

    def __call__(self, prefix, **kwargs):
        from argcomplete import debug
        try:
            debug("\n------------ FolderCompleter -----------------")
            debug("Kwargs content :")
            for i, j in kwargs.items():
                debug("key : " + str(i))
                debug("\t - " + str(j))
            debug("\n------------ FolderCompleter -----------------\n")
            args = kwargs.get('parsed_args')
            wg_cmd = WgNodeContentListCommand(self.config)
            return wg_cmd.complete_workgroups_folders(args, prefix)
        # pylint: disable-msg=W0703
        except Exception as ex:
            debug("\nERROR:An exception was caught :" + str(ex) + "\n")


# -----------------------------------------------------------------------------
class WgNodesCommand(DefaultCommand):

    DEFAULT_TOTAL = "Documents found : %(count)s"
    MSG_RS_NOT_FOUND = "No documents could be found."
    MSG_RS_DELETED = ("%(position)s/%(count)s: "
                      "The document '%(name)s' (%(uuid)s) was deleted. "
                      "(%(time)s s)")
    MSG_RS_CAN_NOT_BE_DELETED = "The document '%(uuid)s' can not be deleted."
    MSG_RS_CAN_NOT_BE_DELETED_M = "%(count)s document(s) can not be deleted."
    MSG_RS_DOWNLOADED = ("%(position)s/%(count)s: "
                         "The document '%(name)s' (%(uuid)s) was downloaded. "
                         "(%(time)s s)")
    MSG_RS_CAN_NOT_BE_DOWNLOADED = "One document can not be downloaded."
    MSG_RS_CAN_NOT_BE_DOWNLOADED_M = ("%(count)s "
                                      "documents can not be downloaded.")

    CFG_DOWNLOAD_MODE = 1
    CFG_DOWNLOAD_ARG_ATTR = "wg_uuid"
    CFG_DELETE_MODE = 1
    CFG_DELETE_ARG_ATTR = "wg_uuid"

    ACTIONS = {
        'delete': '_delete_all',
        'download': '_download_all',
        'count_only': '_count_only',
    }

    def complete(self, args, prefix):
        """Autocomplete on every node in the current folder, file or folder"""
        super(WgNodesCommand, self).__call__(args)
        cli = self.ls.workgroup_nodes
        json_obj = cli.list(args.wg_uuid)
        # only root folder is supported for now.
        # json_obj = cli.list(args.wg_uuid, args.folders)
        return (v.get('uuid')
                for v in json_obj if v.get('uuid').startswith(prefix))

    def complete_workgroups(self, args, prefix):
        """TODO"""
        super(WgNodesCommand, self).__call__(args)
        json_obj = self.ls.threads.list()
        return (v.get('uuid')
                for v in json_obj if v.get('uuid').startswith(prefix))

    def complete_workgroups_folders(self, args, prefix):
        """TODO"""
        from argcomplete import debug
        super(WgNodesCommand, self).__call__(args)
        cli = self.ls.workgroup_nodes
        debug("folders : ", args.folders)
        if args.folders:
            debug("len folders : ", len(args.folders))
        debug("prefix : ", prefix)
        debug("len prefix : ", len(prefix))

        def to_list(json_obj, parent, prefix):
            """Convert json_obj to a list ready to use for completion"""
            debug("\n>----------- to_list - 1  -----------------")
            debug("parent: ", parent)
            debug("prefix: ", prefix)
            debug("RAW", json_obj)
            json_obj = list(
                format_record_for_autocomplete(row)
                for row in json_obj if row.get('type') == "FOLDER"
            )
            debug("UUIDS", json_obj)
            debug("------------ to_list - 1 ----------------<\n")
            return json_obj

        if args.folders:
            parent = get_uuid_from(args.folders[-1])
            if len(parent) >= 36:
                json_obj = cli.list(args.wg_uuid, parent)
                res = to_list(json_obj, parent, prefix)
                return res
            else:
                if len(args.folders) >= 2:
                    parent = get_uuid_from(args.folders[-2])
                else:
                    parent = None
                json_obj = cli.list(args.wg_uuid, parent)
                return to_list(json_obj, parent, prefix)
        else:
            parent = None
            json_obj = cli.list(args.wg_uuid)
            res = to_list(json_obj, parent, prefix)
            return res

    def _run(self, method, message_ok, err_suffix, *args):
        try:
            json_obj = method(*args)
            self.log.info(message_ok, json_obj)
            if self.debug:
                self.pretty_json(json_obj)
            return True
        except LinShareException as ex:
            self.log.debug("LinShareException : " + str(ex.args))
            self.log.error(ex.args[1] + " : " + err_suffix)
        return False


# -----------------------------------------------------------------------------
class WorkgroupDocumentsUploadCommand(WgNodesCommand):
    """ Upload a file to LinShare using its rest api. return the uploaded
document uuid  """

    @Time('linsharecli.document', label='Global time : %(time)s')
    def __call__(self, args):
        super(WorkgroupDocumentsUploadCommand, self).__call__(args)
        count = len(args.files)
        position = 0
        parent = None
        if args.folders:
            parent = get_uuid_from(args.folders[-1])
            self.ls.workgroup_nodes.get(args.wg_uuid, parent)
        for file_path in args.files:
            position += 1
            json_obj = self.ls.workgroup_nodes.upload(
                args.wg_uuid, file_path, args.description, parent)
            if json_obj:
                json_obj['time'] = self.ls.last_req_time
                json_obj['position'] = position
                json_obj['count'] = count
                self.log.info(
                    ("%(position)s/%(count)s: "
                     "The file '%(name)s' (%(uuid)s) was uploaded. "
                     "(%(time)ss)"),
                    json_obj)
        return True


# -----------------------------------------------------------------------------
class WgNodeContentListCommand(WgNodesCommand):
    """ List all thread members."""

    @Time('linsharecli.workgroups.nodes', label='Global time : %(time)s')
    def __call__(self, args):
        super(WgNodeContentListCommand, self).__call__(args)
        cli = self.ls.workgroup_nodes
        table = self.get_table(args, cli, self.IDENTIFIER, args.fields)
        parent = None
        if args.folders:
            parent = get_uuid_from(args.folders[-1])
            self.ls.workgroup_nodes.get(args.wg_uuid, parent)
        json_obj = cli.list(args.wg_uuid, parent)
        # Filters
        filters = [PartialOr(self.IDENTIFIER, args.names, True),
                   PartialDate("creationDate", args.cdate)]
        # Formatters
        formatters = [DateFormatter('creationDate'),
                      DateFormatter('uploadDate'),
                      SizeFormatter('size', "-"),
                      LastAuthorFormatter('lastAuthor'),
                      DateFormatter('modificationDate')]
        return self._list(args, cli, table, json_obj, formatters, filters)

    def complete_fields(self, args, prefix):
        super(WgNodeContentListCommand, self).__call__(args)
        cli = self.ls.workgroup_nodes
        return cli.get_rbu().get_keys(True)


class WorkgroupDocumentsDownloadCommand(WgNodesCommand):

    @Time('linsharecli.workgroups.nodes', label='Global time : %(time)s')
    def __call__(self, args):
        super(WorkgroupDocumentsDownloadCommand, self).__call__(args)
        cli = self.ls.workgroup_nodes
        return self._download_all(args, cli, args.uuids)


# -----------------------------------------------------------------------------
class WorkgroupDocumentsDeleteCommand(WgNodesCommand):

    @Time('linsharecli.workgroups.nodes', label='Global time : %(time)s')
    def __call__(self, args):
        super(WorkgroupDocumentsDeleteCommand, self).__call__(args)
        cli = self.ls.workgroup_nodes
        return self._delete_all(args, cli, args.uuids)


# -----------------------------------------------------------------------------
class FolderCreateCommand(WgNodesCommand):

    @Time('linsharecli.threads', label='Global time : %(time)s')
    def __call__(self, args):
        super(FolderCreateCommand, self).__call__(args)
        cli = self.ls.workgroup_folders
        rbu = cli.get_rbu()
        rbu.load_from_args(args)
        if args.folders:
            parent = get_uuid_from(args.folders[-1])
            rbu.set_value('parent', parent)
        return self._run(
            cli.create,
            ("The following folder '%(name)s' "
             "(%(uuid)s) was successfully created"),
            args.name,
            rbu.to_resource())


# -----------------------------------------------------------------------------
def add_parser(subparsers, name, desc, config):
    parser_tmp = subparsers.add_parser(name, help=desc)
    parser_tmp.add_argument(
        'wg_uuid',
        help="workgroup uuid"
        ).completer = WorkgroupCompleter(config)

    subparsers2 = parser_tmp.add_subparsers()

    # command : list
    parser = subparsers2.add_parser(
        'list',
        help="list workgroup nodes from linshare")
    parser.add_argument(
        '-f', '--filter', action="append", dest="names",
        help="Filter documents by their names")
    parser.add_argument(
        'folders', nargs="*",
        help="Browse folders'content: folder_uuid, folder_uuid, ..."
        ).completer = FolderCompleter(config)
    add_list_parser_options(
        parser, download=True, delete=True, cdate=True)
    parser.set_defaults(__func__=WgNodeContentListCommand(config))

    # command : delete
    parser = subparsers2.add_parser(
        'delete',
        help="delete workgroup nodes (folders, documents, ...)")
    add_delete_parser_options(parser)
    parser.set_defaults(__func__=WorkgroupDocumentsDeleteCommand(config))

    # command : download
    parser = subparsers2.add_parser(
        'download',
        help="download documents from linshare")
    add_download_parser_options(parser)
    parser.set_defaults(__func__=WorkgroupDocumentsDownloadCommand(config))

    # command : upload
    parser = subparsers2.add_parser(
        'upload',
        help="upload documents to linshare")
    parser.add_argument('--desc', action="store", dest="description",
                        required=False, help="Optional description.")
    parser.add_argument('files', nargs='+')
    parser.add_argument(
        '-f', '--folders', action="append",
        help="The new folder will be created in the last folder list. Otherwise it will be create at the root of the workgroup"
        ).completer = FolderCompleter(config)
    parser.set_defaults(__func__=WorkgroupDocumentsUploadCommand(config))

    # command : create
    parser = subparsers2.add_parser(
        'create', help="create workgroup.")
    parser.add_argument('name', action="store", help="")
    parser.add_argument(
        'folders', nargs="*",
        help="The new folder will be created in the last folder list. Otherwise it will be create at the root of the workgroup"
        ).completer = FolderCompleter(config)
    parser.set_defaults(__func__=FolderCreateCommand(config))

