#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

import logging.config
from lib.common import conf
from lib.common.helpers import csv_to_dictionary


class Base():
    """
    @param command_base: base command of hammer.
    Output of recent: `hammer --help`
        shell                         Interactive Shell
        architecture                  Manipulate Foreman's architectures.
        global_parameter              Manipulate Foreman's global parameters.
        compute_resource              Manipulate Foreman's compute resources.
        domain                        Manipulate Foreman's domains.
        environment                   Manipulate Foreman's environments.
        fact                          Search Foreman's facts.
        report                        Browse and read reports.
        puppet_class                  Browse and read reports.
        host                          Manipulate Foreman's hosts.
        hostgroup                     Manipulate Foreman's hostgroups.
        location                      Manipulate Foreman's locations.
        medium                        Manipulate Foreman's installation media.
        model                         Manipulate Foreman's hardware models.
        os                            Manipulate Foreman's operating system.
        organization                  Manipulate Foreman's organizations.
        partition_table               Manipulate Foreman's partition tables.
        proxy                         Manipulate Foreman's smart proxies.
        subnet                        Manipulate Foreman's subnets.
        template                      Manipulate Foreman's config templates.
        user                          Manipulate Foreman's users.
    @since: 27.Nov.2013
    """
    command_base = None  # each inherited instance should define this
    command_sub = None  # specific to instance, like: create, update, etc

    try:
        logging.config.fileConfig("%s/logging.conf" % conf.get_root_path())
    except Exception:
        log_format = '%(levelname)s %(module)s:%(lineno)d: %(message)s'
        logging.basicConfig(format=log_format)

    logger = logging.getLogger("robottelo")
    logger.setLevel(int(conf.properties['nosetests.verbosity']))

    locale = conf.properties['main.locale']
    katello_user = conf.properties['foreman.admin.username']
    katello_passwd = conf.properties['foreman.admin.password']

    def add_operating_system(self, options=None):
        """
        Adds OS to record.
        """

        self.command_sub = "add_operatingsystem"

        options = options or {}

        (stdout, stderr) = self.execute(self._construct_command(options))

        return False if stderr else True

    def create(self, options=None):
        """
        Creates a new record using the arguments passed via dictionary.
        """

        self.command_sub = "create"

        options = options or {}

        (stdout, stderr) = self.execute(self._construct_command(options))

        return False if stderr else True

    def delete(self, options=None):
        """
        Deletes existing record.
        """

        self.command_sub = "delete"

        options = options or {}

        (stdout, stderr) = self.execute(self._construct_command(options))

        return False if stderr else True

    def dump(self, options=None):
        """
        Displays the content for existing partition table.
        """

        self.command_sub = "dump"

        options = options or {}

        (stdout, stderr) = self.execute(self._construct_command(options))

        return '' if stderr else stdout[0]

    def execute(self, command, user=None, password=None):

        if user is None:
            user = self.katello_user
        if password is None:
            password = self.katello_passwd

        shell_cmd = "LANG=%s hammer -u %s -p %s --csv %s"

        stdout, stderr = self.conn.exec_command(
            shell_cmd % (self.locale, user, password, command))[-2:]

        output = stdout.readlines()
        errors = stderr.readlines()

        # helps for each command to be grouped with a new line.
        print ""

        self.logger.debug(shell_cmd % (self.locale, user, password, command))

        if output:
            self.logger.debug("".join(output))
        if errors:
            self.logger.error("".join(errors))

        return output, errors

    def exists(self, name):
        """
        Search for record by name.
        """

        options = {
            "search": "name='%s'" % name,
        }

        _ret = self.list(options)

        if _ret:
            _ret = _ret[0]

        return _ret

    def info(self, options=None):
        """
        Gets information by provided: options dictionary.
        @param options: ID (sometimes name or id).
        """
        self.command_sub = "info"
        if options is None:
            options = {}

        stdout = self.execute(self._construct_command(options))[0]

        return csv_to_dictionary(stdout) if stdout else {}

    def list(self, options=None):
        """
        List information.
        @param cmdID: ID (sometimes name works as well) to retrieve info.
        """
        self.command_sub = "list"
        if options is None:
            options = {}
            options['per-page'] = 10000

        stdout = self.execute(self._construct_command(options))[0]
        return csv_to_dictionary(stdout) if stdout else {}

    def remove_operating_system(self, options=None):
        """
        Removes OS from record.
        """

        self.command_sub = "remove_operatingsystem"

        options = options or {}

        (stdout, stderr) = self.execute(self._construct_command(options))

        return False if stderr else True

    def update(self, options=None):
        """
        Updates existing record.
        """

        self.command_sub = "update"

        options = options or {}

        (stdout, stderr) = self.execute(self._construct_command(options))

        return False if stderr else True

    def _construct_command(self, options={}):
        tail = ""

        for key, val in options.items():
            if val:
                tail = tail + " --%s='%s'" % (key, val)
            else:
                tail = tail + " --%s" % key
        cmd = self.command_base + " " + self.command_sub + " " + tail.strip()

        return cmd