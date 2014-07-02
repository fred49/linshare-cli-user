#! /usr/bin/env python
# -*- coding: utf-8 -*-


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

from __future__ import unicode_literals

import linshare_cli.common as common
from linshare_cli.core import AdminCli
from argtoolbox import DefaultCompleter
from linshare_cli.common import VTable
from linshare_cli.common import HTable
import argtoolbox


# -----------------------------------------------------------------------------
class DefaultCommand(common.DefaultCommand):
    """ Default command object use by the serer API. If you want to add a new
    command to the command line interface, your class should extend this class.
    """

    def __get_cli_object(self, args):
        return AdminCli(args.host, args.user, args.password, args.verbose,
                        args.debug, args.realm, args.application_name)


# -----------------------------------------------------------------------------
class NotYetImplementedCommand(argtoolbox.DefaultCommand):
    """Just for test. Print test to stdout"""

    def __init__(self, config=None):
        super(NotYetImplementedCommand, self).__init__(config)

    def __call__(self, args):
        print "Not Yet Implemented."


# -----------------------------------------------------------------------------
class TestCommand(argtoolbox.DefaultCommand):
    """Just for test. Print test to stdout"""

    def __init__(self, config=None):
        super(TestCommand, self).__init__(config)
        self.verbose = False
        self.debug = False

    def __call__(self, args):
        self.verbose = args.verbose
        self.debug = args.debug
        print "Test"
        print unicode(self.config)
        print args
        self.log.info("End of test command.")


# -------------------------- Domains ------------------------------------------
# -----------------------------------------------------------------------------
class DomainsListCommand(DefaultCommand):
    """ List all domains."""

    def __call__(self, args):
        super(DomainsListCommand, self).__call__(args)
        json_obj = self.ls.domains.list()
        keys = self.ls.domains.get_rbu().get_keys(args.extended)
        table = None
        if args.vertical:
            table = VTable(keys)
        else:
            table = HTable(keys)
            # styles
            table.align["identifier"] = "l"
            table.padding_width = 1
        table.sortby = "identifier"
        table.reversesort = args.reverse
        if args.label:
            table.sortby = "label"
        def filters(row):
            """Return true if the current row matches the filter."""
            if not args.identifiers:
                return True
            if row.get('identifier') in args.identifiers:
                return True
            return False
        table.print_table(json_obj, keys, filters)

    def complete(self, args, prefix):
        super(DomainsListCommand, self).__call__(args)
        json_obj = self.ls.domains.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# -----------------------------------------------------------------------------
# Ignore unused variable prefix
# pylint: disable-msg=W0613
class DomainsCreateCommand(DefaultCommand):
    """ List all domains."""

    def __call__(self, args):
        super(DomainsCreateCommand, self).__call__(args)
        rbu = self.ls.domains.get_rbu()
        rbu.load_from_args(args)
        json_obj = self.ls.domains.create(rbu.to_resource())
        self.pretty_json(json_obj)

    def complete_type(self, args, prefix):
        """ Complete with available domain type."""
        super(DomainsCreateCommand, self).__call__(args)
        return self.ls.domains.options_type()

    def complete_role(self, args, prefix):
        """ Complete with available role."""
        super(DomainsCreateCommand, self).__call__(args)
        return self.ls.domains.options_role()

    def complete_language(self, args, prefix):
        """ Complete with available language."""
        super(DomainsCreateCommand, self).__call__(args)
        return self.ls.domains.options_language()


# -----------------------------------------------------------------------------
class DomainProvidersCreateCommand(DefaultCommand):
    """ List all domains."""

    def __call__(self, args):
        super(DomainProvidersCreateCommand, self).__call__(args)
        resource = None
        for model in self.ls.domains.list():
            if model.get('identifier') == args.identifier:
                resource = model
                break
        if resource is None:
            raise ValueError("Domain idenfier not found")
        rbu = self.ls.domains.get_rbu()
        rbu.copy(resource)
        rbu.load_from_args(args)
        providers = [{
            "baseDn": args.basedn,
            "domainPatternId": args.dpattern,
            "ldapConnectionId": args.ldap
        }]
        rbu.set_value("providers", providers)

        json_obj = self.ls.domains.update(rbu.to_resource())
        self.pretty_json(json_obj)

    def complete(self, args, prefix):
        super(DomainProvidersCreateCommand, self).__call__(args)
        json_obj = self.ls.domains.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))

    def complete_ldap(self, args, prefix):
        super(DomainProvidersCreateCommand, self).__call__(args)
        json_obj = self.ls.ldap_connections.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))

    def complete_dpattern(self, args, prefix):
        super(DomainProvidersCreateCommand, self).__call__(args)
        json_obj = self.ls.domain_patterns.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# -----------------------------------------------------------------------------
class DomainProvidersDeleteCommand(DefaultCommand):
    """ List all domains."""

    def __call__(self, args):
        super(DomainProvidersDeleteCommand, self).__call__(args)
        resource = None
        for model in self.ls.domains.list():
            if model.get('identifier') == args.identifier:
                resource = model
                break
        if resource is None:
            raise ValueError("Domain idenfier not found")
        rbu = self.ls.domains.get_rbu()
        rbu.copy(resource)
        rbu.load_from_args(args)
        providers = []
        rbu.set_value("providers", providers)
        json_obj = self.ls.domains.update(rbu.to_resource())
        self.pretty_json(json_obj)

    def complete(self, args, prefix):
        super(DomainProvidersDeleteCommand, self).__call__(args)
        json_obj = self.ls.domains.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# -----------------------------------------------------------------------------
class DomainProvidersUpdateCommand(DefaultCommand):
    """ List all domains."""

    def __call__(self, args):
        super(DomainProvidersUpdateCommand, self).__call__(args)
        resource = None
        for model in self.ls.domains.list():
            if model.get('identifier') == args.identifier:
                resource = model
                break
        if resource is None:
            raise ValueError("Domain idenfier not found")
        rbu = self.ls.domains.get_rbu()
        rbu.copy(resource)
        rbu.load_from_args(args)

        resource = rbu.to_resource()
        for i in resource['providers']:
            if args.ldap is not None:
                i['ldapConnectionId'] = args.ldap
            if args.dpattern is not None:
                i['domainPatternId'] = args.dpattern
            if args.basedn is not None:
                i['baseDn'] = args.basedn

        json_obj = self.ls.domains.update(resource)
        self.pretty_json(json_obj)

    def complete(self, args, prefix):
        super(DomainProvidersUpdateCommand, self).__call__(args)
        json_obj = self.ls.domains.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))

    def complete_ldap(self, args, prefix):
        super(DomainProvidersUpdateCommand, self).__call__(args)
        json_obj = self.ls.ldap_connections.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))

    def complete_dpattern(self, args, prefix):
        super(DomainProvidersUpdateCommand, self).__call__(args)
        json_obj = self.ls.domain_patterns.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# -----------------------------------------------------------------------------
class DomainsUpdateCommand(DefaultCommand):
    """ List all domains."""

    def __call__(self, args):
        super(DomainsUpdateCommand, self).__call__(args)
        resource = None
        for model in self.ls.domains.list():
            if model.get('identifier') == args.identifier:
                resource = model
                break
        if resource is None:
            raise ValueError("Domain idenfier not found")
        rbu = self.ls.domains.get_rbu()
        rbu.copy(resource)
        rbu.load_from_args(args)
        json_obj = self.ls.domains.update(rbu.to_resource())
        self.pretty_json(json_obj)

    def complete(self, args, prefix):
        super(DomainsUpdateCommand, self).__call__(args)
        json_obj = self.ls.domains.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))

    def complete_role(self, args, prefix):
        """ Complete with available role."""
        super(DomainsUpdateCommand, self).__call__(args)
        return self.ls.domains.options_role()

    def complete_language(self, args, prefix):
        """ Complete with available language."""
        super(DomainsUpdateCommand, self).__call__(args)
        return self.ls.domains.options_language()


# -----------------------------------------------------------------------------
class DomainsDeleteCommand(DefaultCommand):
    """ List all domains."""

    def __call__(self, args):
        super(DomainsDeleteCommand, self).__call__(args)
        self.ls.domains.delete(args.identifier)

    def complete(self, args, prefix):
        super(DomainsDeleteCommand, self).__call__(args)
        json_obj = self.ls.domains.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# ---------------------- Ldap connections -------------------------------------
# -----------------------------------------------------------------------------
class LdapConnectionsListCommand(DefaultCommand):
    """ List all ldap connections."""

    def __call__(self, args):
        super(LdapConnectionsListCommand, self).__call__(args)
        json_obj = self.ls.ldap_connections.list()
        keys = self.ls.ldap_connections.get_rbu().get_keys()
        table = None
        if args.vertical:
            table = VTable(keys)
        else:
            table = HTable(keys)
            # styles
            table.align["identifier"] = "l"
            table.padding_width = 1
        table.sortby = "identifier"
        table.reversesort = args.reverse
        def filters(row):
            if not args.identifiers:
                return True
            if row.get('identifier') in args.identifiers:
                return True
            return False
        table.print_table(json_obj, keys, filters)

    def complete(self, args, prefix):
        super(LdapConnectionsListCommand, self).__call__(args)
        json_obj = self.ls.ldap_connections.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# -----------------------------------------------------------------------------
class LdapConnectionsCreateCommand(DefaultCommand):
    """Create ldap connection."""

    def __call__(self, args):
        super(LdapConnectionsCreateCommand, self).__call__(args)
        rbu = self.ls.ldap_connections.get_rbu()
        rbu.load_from_args(args)
        json_obj = self.ls.ldap_connections.create(rbu.to_resource())
        self.pretty_json(json_obj)


# -----------------------------------------------------------------------------
class LdapConnectionsUpdateCommand(DefaultCommand):
    """Update ldap connection."""

    def __call__(self, args):
        super(LdapConnectionsUpdateCommand, self).__call__(args)
        resource = None
        for model in self.ls.ldap_connections.list():
            if model.get('identifier') == args.identifier:
                resource = model
                break
        if resource is None:
            raise ValueError("Ldap idenfier not found")
        rbu = self.ls.ldap_connections.get_rbu()
        rbu.copy(resource)
        rbu.load_from_args(args)
        json_obj = self.ls.ldap_connections.update(rbu.to_resource())
        self.pretty_json(json_obj)

    def complete(self, args, prefix):
        super(LdapConnectionsUpdateCommand, self).__call__(args)
        json_obj = self.ls.ldap_connections.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# -----------------------------------------------------------------------------
class LdapConnectionsDeleteCommand(DefaultCommand):
    """Delete ldap connection."""

    def __call__(self, args):
        super(LdapConnectionsDeleteCommand, self).__call__(args)
        self.ls.ldap_connections.delete(args.identifier)

    def complete(self, args, prefix):
        super(LdapConnectionsDeleteCommand, self).__call__(args)
        json_obj = self.ls.ldap_connections.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# ----------------------- Domains patterns ------------------------------------
# -----------------------------------------------------------------------------
class DomainPatternsListCommand(DefaultCommand):
    """ List all domain patterns."""

    def __call__(self, args):
        super(DomainPatternsListCommand, self).__call__(args)
        json_obj = self.ls.domain_patterns.list(args.model)
        keys = self.ls.domain_patterns.get_rbu().get_keys(args.extended)
        table = None
        if args.vertical:
            table = VTable(keys)
        else:
            table = HTable(keys)
            # styles
            table.align["identifier"] = "l"
            table.padding_width = 1
        table.sortby = "identifier"
        table.reversesort = args.reverse
        def filters(row):
            if not args.identifiers:
                return True
            if row.get('identifier') in args.identifiers:
                return True
            return False
        table.print_table(json_obj, keys, filters)

    def complete(self, args, prefix):
        super(DomainPatternsListCommand, self).__call__(args)
        json_obj = self.ls.domain_patterns.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))

# -----------------------------------------------------------------------------
class DomainPatternsUpdateCommand(DefaultCommand):
    """ Update a domain pattern."""

    def __call__(self, args):
        super(DomainPatternsUpdateCommand, self).__call__(args)
        resource = None
        for model in self.ls.domain_patterns.list():
            if model.get('identifier') == args.identifier:
                resource = model
                break
        if resource is None:
            raise ValueError("Domain resource idenfier not found")
        rbu = self.ls.domain_patterns.get_rbu()
        rbu.copy(resource)
        rbu.load_from_args(args)
        json_obj = self.ls.domain_patterns.update(rbu.to_resource())
        self.pretty_json(json_obj)

    def complete(self, args, prefix):
        super(DomainPatternsUpdateCommand, self).__call__(args)
        json_obj = self.ls.domain_patterns.list()
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# -----------------------------------------------------------------------------
class DomainPatternsCreateCommand(DefaultCommand):
    """ Create a domain pattern."""

    def __call__(self, args):
        super(DomainPatternsCreateCommand, self).__call__(args)
        rbu = self.ls.domain_patterns.get_rbu()
        if args.model:
            json_obj = self.ls.domain_patterns.list(True)
            for model in json_obj:
                if model.get('identifier') == args.model:
                    rbu.copy(model)
                    # reset identifier
                    rbu.set_value('identifier', "")
                    break
        rbu.load_from_args(args)
        json_obj = self.ls.domain_patterns.create(rbu.to_resource())
        self.pretty_json(json_obj)

    def complete(self, args, prefix):
        super(DomainPatternsCreateCommand, self).__call__(args)
        json_obj = self.ls.domain_patterns.list(True)
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# -----------------------------------------------------------------------------
class DomainPatternsDeleteCommand(DefaultCommand):
    """ List all domain patterns."""

    def __call__(self, args):
        super(DomainPatternsDeleteCommand, self).__call__(args)
        self.ls.domain_patterns.delete(args.identifier)

    def complete(self, args, prefix):
        super(DomainPatternsDeleteCommand, self).__call__(args)
        json_obj = self.ls.domain_patterns.list(True)
        return (v.get('identifier')
                for v in json_obj if v.get('identifier').startswith(prefix))


# -------------------------- Threads ------------------------------------------
# -----------------------------------------------------------------------------
class ThreadsListCommand(DefaultCommand):
    """ List all threads store into LinShare."""

    def __call__(self, args):
        super(ThreadsListCommand, self).__call__(args)

        json_obj = self.ls.threads.list()
        d_format = "{name:60s}{creationDate:30s}{uuid:30s}"
        #self.pretty_json(json_obj)
        self.format_date(json_obj, 'creationDate')
        self.print_list(json_obj, d_format, "Threads")

        #self.print_test(json_obj)


# -----------------------------------------------------------------------------
class ThreadMembersListCommand(DefaultCommand):
    """ List all thread members store from a thread."""

    def __call__(self, args):
        super(ThreadMembersListCommand, self).__call__(args)

        json_obj = self.ls.thread_members.list(args.uuid)

        d_format = "{firstName:11s}{lastName:10s}{admin:<7}{readonly:<9}{id}"
        #self.pretty_json(json_obj)
        self.print_list(json_obj, d_format, "Thread members")

    def complete(self, args, prefix):
        super(ThreadMembersListCommand, self).__call__(args)

        json_obj = self.ls.threads.list()
        return (v.get('uuid')
                for v in json_obj if v.get('uuid').startswith(prefix))


# -------------------------- Users --------------------------------------------
# -----------------------------------------------------------------------------
class UsersListCommand(DefaultCommand):
    """ List all users store into LinShare."""

    def __call__(self, args):
        super(UsersListCommand, self).__call__(args)

        json_obj = self.ls.users.list()
        d_format = "{firstName:11s}{lastName:10s}{domain:<20}{mail}"
        #print "%(firstName)-10s %(lastName)-10s\t %(domain)s %(mail)s" % f
        #self.pretty_json(json_obj)
        self.print_list(json_obj, d_format, "Users")



###############################################################################
###  domains
###############################################################################
def add_domains_parser(subparsers, name, desc):
    """Add all domain sub commands."""
    parser_tmp = subparsers.add_parser(name, help=desc)
    subparsers2 = parser_tmp.add_subparsers()

    # command : list
    parser_tmp2 = subparsers2.add_parser(
        'list', help="list domains.")
    parser_tmp2.add_argument('identifiers', nargs="*",
                             help="").completer = DefaultCompleter()
    parser_tmp2.add_argument('--extended', action="store_true",
                             help="extended format")
    parser_tmp2.add_argument('-r', '--reverse', action="store_true",
                             help="reverse order while sorting")
    parser_tmp2.add_argument('-n', '--label', action="store_true",
                             help="sort by domain label")
    parser_tmp2.add_argument('-t', '--vertical', action="store_true",
                             help="use vertical output mode")
    parser_tmp2.set_defaults(__func__=DomainsListCommand())

    # command : create
    parser_tmp2 = subparsers2.add_parser(
        'create', help="create domain.")
    parser_tmp2.add_argument('--label', action="store", help="",
                             required=True)
    parser_tmp2.add_argument('identifier', action="store", help="")
    parser_tmp2.add_argument(
        '--type', dest="domain_type", action="store", help="",
        required=True).completer = DefaultCompleter("complete_type")
    parser_tmp2.add_argument('--description', action="store", help="")
    parser_tmp2.add_argument(
        '--role', dest="role", action="store",
        help="").completer = DefaultCompleter("complete_role")
    parser_tmp2.add_argument(
        '--language', dest="language", action="store",
        help="").completer = DefaultCompleter("complete_language")
    parser_tmp2.add_argument(
        '--mime-policy', dest="mime_policy", action="store",
        help="TODO").completer = DefaultCompleter("complete_mime")
    parser_tmp2.add_argument(
        '--domain-policy', dest="domain_policy", action="store",
        help="TODO").completer = DefaultCompleter("complete_policy")
    parser_tmp2.add_argument(
        '--mail-config', dest="mail_config", action="store",
        help="TODO").completer = DefaultCompleter("complete_mail")
    parser_tmp2.set_defaults(__func__=DomainsCreateCommand())

    # command : update
    parser_tmp2 = subparsers2.add_parser(
        'update', help="update domain.")
    parser_tmp2.add_argument(
        'identifier', action="store", help="").completer = DefaultCompleter()
    parser_tmp2.add_argument('--label', action="store", help="")
    parser_tmp2.add_argument('--description', action="store", help="")
    parser_tmp2.add_argument(
        '--role', dest="role", action="store",
        help="").completer = DefaultCompleter("complete_role")
    parser_tmp2.add_argument(
        '--language', dest="language", action="store",
        help="").completer = DefaultCompleter("complete_language")
    parser_tmp2.set_defaults(__func__=DomainsUpdateCommand())

    # command : delete
    parser_tmp2 = subparsers2.add_parser(
        'delete', help="delete domain.")
    parser_tmp2.add_argument(
        'identifier', action="store",
        help="").completer = DefaultCompleter()
    parser_tmp2.set_defaults(__func__=DomainsDeleteCommand())

    # command : set provider
    parser_tmp2 = subparsers2.add_parser(
        'setup', help="add user provider.")
    parser_tmp2.add_argument(
        'identifier', action="store",
        help="domain identifier").completer = DefaultCompleter()
    parser_tmp2.add_argument('--basedn', action="store", help="",
                             required=True)
    parser_tmp2.add_argument(
        '--ldap', dest="ldap", action="store", help="ldap identifier",
        required=True).completer = DefaultCompleter("complete_ldap")
    parser_tmp2.add_argument(
        '--dpattern', dest="dpattern", action="store", help="domain pattern identifier",
        required=True).completer = DefaultCompleter("complete_dpattern")
    parser_tmp2.set_defaults(__func__=DomainProvidersCreateCommand())

    # command : update provider
    parser_tmp2 = subparsers2.add_parser(
        'updateup', help="update user provider.")
    parser_tmp2.add_argument(
        'identifier', action="store",
        help="domain identifier").completer = DefaultCompleter()
    parser_tmp2.add_argument('--basedn', action="store", help="")
    parser_tmp2.add_argument(
        '--ldap', dest="ldap", action="store",
        help="ldap identifier").completer = DefaultCompleter("complete_ldap")
    parser_tmp2.add_argument(
        '--dpattern', dest="dpattern", action="store",
        help="domain pattern identifier").completer = DefaultCompleter("complete_dpattern")
    parser_tmp2.set_defaults(__func__=DomainProvidersUpdateCommand())

    # command : del provider
    parser_tmp2 = subparsers2.add_parser(
        'delup', help="add user provider.")
    parser_tmp2.add_argument(
        'identifier', action="store",
        help="domain identifier").completer = DefaultCompleter()
    parser_tmp2.set_defaults(__func__=DomainProvidersDeleteCommand())


###############################################################################
###  ldap connections
###############################################################################
def add_ldap_connections_parser(subparsers, name, desc):
    """Add all ldap connections sub commands."""
    parser_tmp = subparsers.add_parser(name, help=desc)
    subparsers2 = parser_tmp.add_subparsers()

    # command : list
    parser_tmp2 = subparsers2.add_parser(
        'list', help="list ldap connections.")
    parser_tmp2.add_argument('identifiers', nargs="*",
                             help="").completer = DefaultCompleter()
    parser_tmp2.add_argument('-r', '--reverse', action="store_true",
                             help="reverse order while sorting")
    parser_tmp2.add_argument('-t', '--vertical', action="store_true",
                             help="use vertical output mode")
    parser_tmp2.set_defaults(__func__=LdapConnectionsListCommand())

    # command : delete
    parser_tmp2 = subparsers2.add_parser(
        'delete', help="delete ldap connections.")
    parser_tmp2.add_argument('--identifier',
                             action="store",
                             help="",
                             required=True).completer = DefaultCompleter()
    parser_tmp2.set_defaults(__func__=LdapConnectionsDeleteCommand())

    # command : create
    parser_tmp2 = subparsers2.add_parser(
        'create', help="create ldap connections.")
    parser_tmp2.add_argument('identifier', action="store", help="")
    parser_tmp2.add_argument('--provider-url', action="store", help="",
                             required=True)
    parser_tmp2.add_argument('--principal', action="store", help="")
    parser_tmp2.add_argument('--credential', action="store", help="")
    parser_tmp2.set_defaults(__func__=LdapConnectionsCreateCommand())

    # command : update
    parser_tmp2 = subparsers2.add_parser(
        'update', help="update ldap connections.")
    parser_tmp2.add_argument(
        'identifier', action="store", help="").completer = DefaultCompleter()
    parser_tmp2.add_argument('--provider-url', action="store", help="")
    parser_tmp2.add_argument('--principal', action="store", help="")
    parser_tmp2.add_argument('--credential', action="store", help="")
    parser_tmp2.set_defaults(__func__=LdapConnectionsUpdateCommand())


###############################################################################
###  domain patterns
###############################################################################
def add_domain_patterns_parser(subparsers, name, desc):
    """Add all domain pattern sub commands."""
    parser_tmp = subparsers.add_parser(name, help=desc)

    # command : list
    subparsers2 = parser_tmp.add_subparsers()
    parser_tmp2 = subparsers2.add_parser(
        'list', help="list domain patterns.")
    parser_tmp2.add_argument('identifiers', nargs="*",
                             help="").completer = DefaultCompleter()
    parser_tmp2.add_argument('--extended', action="store_true",
                             help="extended format")
    parser_tmp2.add_argument('-r', '--reverse', action="store_true",
                             help="reverse order while sorting")
    parser_tmp2.add_argument('-m', '--model', action="store_true",
                             help="show model of domain patterns")
    parser_tmp2.add_argument('-t', '--vertical', action="store_true",
                             help="use vertical output mode")
    parser_tmp2.set_defaults(__func__=DomainPatternsListCommand())

    # command : create
    parser_tmp2 = subparsers2.add_parser(
        'create', help="create domain pattern.")
    parser_tmp2.add_argument('identifier', action="store", help="")
    parser_tmp2.add_argument('--model', action="store",
                             help="").completer = DefaultCompleter()
    parser_tmp2.add_argument('--completion-page-size', action="store",
                             type=int, help="", required=True)
    parser_tmp2.add_argument('--completion-size-limit', action="store",
                             type=int, help="", required=True)
    parser_tmp2.add_argument('--search-page-size', action="store",
                             type=int, help="", required=True)
    parser_tmp2.add_argument('--search-size-limit', action="store",
                             type=int, help="", required=True)
    parser_tmp2.add_argument('--ldap-uid', action="store", help="",
                             required=True)
    parser_tmp2.add_argument('--first-name', action="store", help="",
                             required=True)
    parser_tmp2.add_argument('--last-name', action="store", help="",
                             required=True)
    parser_tmp2.add_argument('--mail', action="store", help="", required=True)
    parser_tmp2.add_argument('--description', action="store", help="",
                             required=True)
    parser_tmp2.add_argument('--auth-command', action="store", help="",
                             required=True)
    parser_tmp2.add_argument('--search-user-command', action="store", help="",
                             required=True)
    parser_tmp2.add_argument('--auto-complete-command-on-all-attributes',
                             action="store", help="", required=True)
    parser_tmp2.add_argument('--auto-complete-command-on-first-and-last-name',
                             action="store", help="", required=True)
    parser_tmp2.set_defaults(__func__=DomainPatternsCreateCommand())

    # command : delete
    parser_tmp2 = subparsers2.add_parser(
        'delete', help="delete domain pattern.")
    parser_tmp2.add_argument('identifier', action="store",
                             help="").completer = DefaultCompleter()
    parser_tmp2.set_defaults(__func__=DomainPatternsDeleteCommand())

    # command : update
    parser_tmp2 = subparsers2.add_parser(
        'update', help="update domain patterns.")
    parser_tmp2.add_argument(
        'identifier', action="store", help="").completer = DefaultCompleter()
    parser_tmp2.add_argument('--completion-page-size', action="store",
                             type=int, help="")
    parser_tmp2.add_argument('--completion-size-limit', action="store",
                             type=int, help="")
    parser_tmp2.add_argument('--search-page-size', action="store",
                             type=int, help="")
    parser_tmp2.add_argument('--search-size-limit', action="store",
                             type=int, help="")
    parser_tmp2.add_argument('--ldap-uid', action="store", help="")
    parser_tmp2.add_argument('--first-name', action="store", help="")
    parser_tmp2.add_argument('--last-name', action="store", help="")
    parser_tmp2.add_argument('--mail', action="store", help="")
    parser_tmp2.add_argument('--description', action="store", help="")
    parser_tmp2.add_argument('--model', action="store",
                             help="").completer = DefaultCompleter()
    parser_tmp2.add_argument('--auth-command', action="store", help="")
    parser_tmp2.add_argument('--search-user-command', action="store", help="")
    parser_tmp2.add_argument('--auto-complete-command-on-all-attributes',
                             action="store", help="")
    parser_tmp2.add_argument('--auto-complete-command-on-first-and-last-name',
                             action="store", help="")
    parser_tmp2.set_defaults(__func__=DomainPatternsUpdateCommand())


###############################################################################
###  threads
###############################################################################
def add_threads_parser(subparsers, name, desc):
    """Add all thread sub commands."""
    parser_tmp = subparsers.add_parser(name, help=desc)

    subparsers2 = parser_tmp.add_subparsers()
    parser_tmp2 = subparsers2.add_parser(
        'list',
        help="list threads from linshare")
    parser_tmp2.set_defaults(__func__=ThreadsListCommand())


###############################################################################
###  threads
###############################################################################
def add_thread_members_parser(subparsers, name, desc):
    """Add all thread member sub commands."""
    parser_tmp = subparsers.add_parser(name, help=desc)

    subparsers2 = parser_tmp.add_subparsers()
    parser_tmp2 = subparsers2.add_parser(
        'listmembers',
        help="list thread members.")
    parser_tmp2.add_argument(
        '-u',
        '--uuid',
        action="store",
        dest="uuid",
        required=True).completer = DefaultCompleter()
    parser_tmp2.set_defaults(__func__=ThreadMembersListCommand())


###############################################################################
###  users
###############################################################################
def add_users_parser(subparsers, name, desc):
    """Add all user sub commands."""
    parser_tmp = subparsers.add_parser(name, help=desc)

    subparsers2 = parser_tmp.add_subparsers()
    parser_tmp2 = subparsers2.add_parser('list',
                                         help="list users from linshare")
    parser_tmp2.set_defaults(__func__=UsersListCommand())


###############################################################################
### test
###############################################################################
def add_test_parser(subparsers, config):
    """Add test commands."""
    parser_tmp = subparsers.add_parser('test', add_help=False)
    parser_tmp.add_argument('files', nargs='*')
    parser_tmp.set_defaults(__func__=TestCommand(config))
