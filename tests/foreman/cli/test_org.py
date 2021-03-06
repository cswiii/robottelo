# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

# pylint: disable=R0904
"""Test class for Organization CLI"""

from ddt import ddt
from fauxfactory import gen_string
from robottelo.common import conf
from robottelo.common.constants import FOREMAN_PROVIDERS
from robottelo.cli.factory import (
    make_domain, make_hostgroup, make_lifecycle_environment,
    make_medium, make_org, make_proxy, make_subnet, make_template, make_user,
    make_compute_resource, CLIFactoryError)
from robottelo.cli.lifecycleenvironment import LifecycleEnvironment
from robottelo.cli.org import Org
from robottelo.common.decorators import (
    data, run_only_on, skip_if_bug_open, stubbed)
from robottelo.test import CLITestCase


def positive_create_data_1():
    """Random data for positive creation"""

    return (
        {'name': gen_string("latin1", 10)},
        {'name': gen_string("utf8", 10)},
        {'name': gen_string("alpha", 10)},
        {'name': gen_string("alphanumeric", 10)},
        {'name': gen_string("numeric", 10)},
        {'name': gen_string("html", 10)},
    )


# Use this when name and label must match. Labels cannot
# contain the same data type as names, so this is a bit limited
# compared to other tests.
# Label cannot contain characters other than ascii alpha numerals, '_', '-'.
def positive_create_data_2():
    """Random simpler data for positive creation"""

    return (
        {'name': gen_string("alpha", 10)},
        {'name': gen_string("alphanumeric", 10)},
        {'name': gen_string("numeric", 10)},
        {'name': '{0}-{1}'.format(gen_string("alpha", 5),
                                  gen_string("alpha", 5))},
        {'name': '{0}_{1}'.format(gen_string("alpha", 5),
                                  gen_string("alpha", 5))},
    )


# Label cannot contain characters other than ascii alpha numerals, '_', '-'.
def positive_name_label_data():
    """Random data for Label tests"""

    return (
        {'name': gen_string("latin1", 10),
         'label': gen_string("alpha", 10)},
        {'name': gen_string("utf8", 10),
         'label': gen_string("alpha", 10)},
        {'name': gen_string("alpha", 10),
         'label': gen_string("alpha", 10)},
        {'name': gen_string("alphanumeric", 10),
         'label': gen_string("alpha", 10)},
        {'name': gen_string("numeric", 10),
         'label': gen_string("alpha", 10)},
        {'name': gen_string("html", 10),
         'label': gen_string("alpha", 10)},
    )


def positive_name_desc_data():
    """Random data for Descriptions tests"""

    return (
        {'name': gen_string("latin1", 10),
         'description': gen_string("latin1", 10)},
        {'name': gen_string("utf8", 10),
         'description': gen_string("utf8", 10)},
        {'name': gen_string("alpha", 10),
         'description': gen_string("alpha", 10)},
        {'name': gen_string("alphanumeric", 10),
         'description': gen_string("alphanumeric", 10)},
        {'name': gen_string("numeric", 10),
         'description': gen_string("numeric", 10)},
        {'name': gen_string("html", 10),
         'description': gen_string("numeric", 10)},
    )


def positive_name_desc_label_data():
    """Random data for Labels and Description"""

    return (
        {'name': gen_string("alpha", 10),
         'description': gen_string("alpha", 10),
         'label': gen_string("alpha", 10)},
        {'name': gen_string("alphanumeric", 10),
         'description': gen_string("alphanumeric", 10),
         'label': gen_string("alpha", 10)},
        {'name': gen_string("numeric", 10),
         'description': gen_string("numeric", 10),
         'label': gen_string("alpha", 10)},
        {'name': gen_string("html", 10),
         'description': gen_string("numeric", 10),
         'label': gen_string("alpha", 10)},
    )


@ddt
class TestOrg(CLITestCase):
    """Tests for Organizations via Hammer CLI"""

    # Tests for issues

    # This test also covers the redmine bug 4443
    @data(*positive_create_data_1())
    def test_redmine_4486(self, test_data):
        """@test: Can search for an organization by name

        @feature: Organizations

        @assert: organization is created and can be searched by name

        """

        new_obj = make_org(test_data)
        # Can we find the new object?
        result = Org.exists(search=('name', new_obj['name']))

        self.assertEqual(result.return_code, 0, "Failed to create object")
        self.assertEqual(len(result.stderr), 0,
                         "There should not be an exception here")
        self.assertEqual(new_obj['name'],
                         result.stdout['name'])

    @run_only_on('sat')
    def test_remove_domain(self):
        """@Test: Check if a Domain can be removed from an Org

        @Feature: Org - Domain

        @Assert: Domain is removed from the org

        """
        org_result = make_org()
        domain_result = make_domain()
        Org.add_domain(
            {'name': org_result['name'], 'domain': domain_result['name']})
        return_value = Org.remove_domain(
            {'name': org_result['name'], 'domain': domain_result['name']})
        self.assertEqual(
            return_value.return_code, 0, "Remove Domain - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    @data(*positive_create_data_1())
    def test_bugzilla_1079587(self, test_data):
        """@test: Search for an organization by label

        @feature: Organizations

        @assert: organization is created and can be searched by label

        """

        new_obj = make_org(test_data)
        # Can we find the new object?
        result = Org.exists(search=('label', new_obj['label']))

        self.assertEqual(result.return_code, 0, "Failed to find the object")
        self.assertEqual(len(result.stderr), 0,
                         "There should not be an exception here")
        self.assertEqual(new_obj['name'],
                         result.stdout['name'])

    @skip_if_bug_open('bugzilla', 1076568)
    def test_bugzilla_1076568_1(self):
        """@test: Delete organization by name

        @feature: Organizations

        @assert: Organization is deleted

        @BZ: 1076568

        """

        new_obj = make_org()

        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])

        return_value = Org.delete({'name': new_obj['name']})
        self.assertEqual(
            return_value.return_code,
            0,
            "Deletion failed: %s" % result.stderr)
        self.assertEqual(
            len(return_value.stderr),
            0,
            "Unexpected error found: %s" % result.stderr)

        # Can we find the object?
        result = Org.info({'id': new_obj['id']})
        self.assertNotEqual(
            result.return_code,
            0,
            "Organization should be deleted but was found")
        self.assertGreater(len(result.stderr), 0,
                           "There should not be an exception here")
        self.assertEqual(
            len(result.stdout), 0, "Output should be blank.")

    @skip_if_bug_open('bugzilla', 1076568)
    def test_bugzilla_1076568_2(self):
        """@test: Delete organization by ID

        @feature: Organizations

        @assert: Organization is deleted

        @BZ: 1076568

        """

        new_obj = make_org()

        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])

        return_value = Org.delete({'id': new_obj['id']})
        self.assertEqual(
            return_value.return_code,
            0,
            "Deletion failed: %s" % result.stderr)
        self.assertEqual(
            len(return_value.stderr),
            0,
            "Unexpected error found: %s" % result.stderr)

        # Can we find the object?
        result = Org.info({'id': new_obj['id']})
        self.assertNotEqual(
            result.return_code,
            0,
            "Organization should be deleted but was found")
        self.assertGreater(len(result.stderr), 0,
                           "There should not be an exception here")
        self.assertEqual(
            len(result.stdout), 0, "Output should be blank.")

    @skip_if_bug_open('bugzilla', 1076568)
    def test_bugzilla_1076568_3(self):
        """@test: Delete organization by label

        @feature: Organizations

        @assert: Organization is deleted

        @BZ: 1076568

        """

        new_obj = make_org()

        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])

        return_value = Org.delete({'label': new_obj['label']})
        self.assertEqual(
            return_value.return_code,
            0,
            "Deletion failed: %s" % result.stderr)
        self.assertEqual(
            len(return_value.stderr),
            0,
            "Unexpected error found: %s" % result.stderr)

        # Can we find the object?
        result = Org.info({'id': new_obj['id']})
        self.assertNotEqual(
            result.return_code,
            0,
            "Organization should be deleted but was found")
        self.assertGreater(len(result.stderr), 0,
                           "There should not be an exception here")
        self.assertEqual(
            len(result.stdout), 0, "Output should be blank.")

    def test_bugzilla_1076541(self):
        """@test: Cannot update organization name via CLI

        @feature: Organizations

        @assert: Organization name is updated

        """

        new_obj = make_org()
        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])

        # Update the org name
        new_name = gen_string("alpha", 15)
        result = Org.update({'id': new_obj['id'],
                             'new-name': new_name})

        self.assertEqual(result.return_code, 0)
        self.assertEqual(
            len(result.stderr), 0, "There should not be an error here")

        # Fetch the org again
        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(
            result.stdout['name'],
            new_name,
            "Org name was not updated"
        )

    def test_bugzilla_1075163(self):
        """@Test: Add --label as a valid argument to organization info command

        @Feature: Org - Positive Create

        @Assert: Organization is created and info can be obtained by its label
        graciously

        """

        new_obj = make_org()
        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0, "Failed to create object")
        self.assertEqual(len(result.stderr), 0,
                         "There should not be an exception here")

        self.assertEqual(new_obj['name'], result.stdout['name'])

    def test_bugzilla_1075156(self):
        """@Test: Cannot use CLI info for organizations by name

        @Feature: Org - Positive Create

        @Assert: Organization is created and info can be obtained by its name
        graciously

        """

        new_obj = make_org()
        result = Org.info({'name': new_obj['name']})
        self.assertEqual(result.return_code, 0, "Failed to create object")
        self.assertEqual(len(result.stderr), 0,
                         "There should not be an exception here")

        self.assertEqual(new_obj['name'], result.stdout['name'])

    @run_only_on('sat')
    def test_bugzilla_1062295_1(self):
        """@Test: Foreman Cli : Add_Config template fails

        @Feature: Org

        @Assert: Config Template is added to the org

        """
        org_result = make_org()
        template_result = make_template()
        return_value = Org.add_config_template({
            'name': org_result['name'],
            'config-template': template_result['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Add ConfigTemplate- retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    @run_only_on('sat')
    def test_bugzilla_1062295_2(self):
        """@Test: Foreman Cli : Add_Config template fails

        @Feature: Org

        @Assert: ConfigTemplate is removed from the org

        """
        org_result = make_org()
        template_result = make_template()
        Org.add_config_template({
            'name': org_result['name'],
            'config-template': template_result['name']})
        return_value = Org.remove_config_template({
            'name': org_result['name'],
            'config-template': template_result['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Remove ConfigTemplate- retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    def test_bugzilla_1023125(self):
        """@Test: hammer-cli: trying to create duplicate org throws unhandled ISE

        @Feature: Org - Positive Create

        @Assert: Organization is created once and second attempt is handled
        graciously

        """

        new_obj = make_org()

        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0, "Failed to create object")
        self.assertEqual(len(result.stderr), 0,
                         "There should not be an exception here")
        self.assertEqual(new_obj['name'], result.stdout['name'])

        # Create new org with the same name as before
        # should yield an exception
        with self.assertRaises(Exception):
            make_org({'name': new_obj['name']})

    # This Bugzilla bug is private. It is impossible to fetch info about it.
    def test_bugzilla_1078866(self):
        """@Test: hammer organization <info,list> --help types information doubled

        @Feature: org info/list

        @Assert: no duplicated lines in usage message

        """
        # org list --help:
        result = Org.list({'help': True})
        # get list of lines and check they all are unique
        lines = [line['message'] for line in result.stdout]
        self.assertEqual(len(set(lines)), len(lines))

        # org info --help:info returns more lines (obviously), ignore exception
        result = Org.info({'help': True})

        # get list of lines and check they all are unique
        lines = [line for line in result.stdout['options']]
        self.assertEqual(len(set(lines)), len(lines))

    # CRUD

    @data(*positive_create_data_1())
    def test_positive_create_1(self, test_data):
        """@test: Create organization with valid name only

        @feature: Organizations

        @assert: organization is created, label is auto-generated

        """

        new_obj = make_org(test_data)
        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0, "Failed to create object")
        self.assertEqual(len(result.stderr), 0,
                         "There should not be an exception here")
        self.assertGreater(
            len(result.stdout), 0, "Failed to fetch organization")
        self.assertEqual(new_obj['name'], result.stdout['name'])

    @data(*positive_create_data_2())
    def test_positive_create_2(self, test_data):
        """@test: Create organization with valid matching name and label only

        @feature: Organizations

        @assert: organization is created, label matches name

        """

        test_data['label'] = test_data['name']
        new_obj = make_org(test_data)

        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0, "Failed to create object")
        self.assertEqual(len(result.stderr), 0,
                         "There should not be an exception here")
        self.assertGreater(
            len(result.stdout), 0, "Failed to fetch organization")
        self.assertEqual(result.stdout['name'], result.stdout['label'])
        self.assertEqual(new_obj['name'], result.stdout['name'])

    @skip_if_bug_open('bugzilla', 1142821)
    @data(*positive_name_label_data())
    def test_positive_create_3(self, test_data):
        """@test: Create organization with valid unmatching name and label only

        @feature: Organizations

        @assert: organization is created, label does not match name

        """

        new_obj = make_org(test_data)

        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0, "Failed to create object")
        self.assertEqual(len(result.stderr), 0,
                         "There should not be an exception here")
        self.assertGreater(
            len(result.stdout), 0, "Failed to fetch organization")
        self.assertNotEqual(result.stdout['name'],
                            result.stdout['label'])
        self.assertEqual(new_obj['name'],
                         result.stdout['name'])
        self.assertEqual(new_obj['label'],
                         result.stdout['label'])

    @data(*positive_name_desc_data())
    def test_positive_create_4(self, test_data):
        """@test: Create organization with valid name and description only

        @feature: Organizations

        @assert: organization is created, label is auto-generated

        """

        test_data['label'] = ""
        new_obj = make_org(test_data)

        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0, "Failed to create object")
        self.assertEqual(len(result.stderr), 0,
                         "There should not be an exception here")
        self.assertGreater(
            len(result.stdout), 0, "Failed to fetch organization")
        self.assertNotEqual(result.stdout['name'],
                            result.stdout['description'])
        self.assertEqual(new_obj['name'],
                         result.stdout['name'])

    @data(*positive_name_desc_data())
    def test_positive_create_5(self, test_data):
        """@test: Create organization with valid name, label and description

        @feature: Organizations

        @assert: organization is created

        """

        test_data['label'] = gen_string('alpha', 10)
        new_obj = make_org(test_data)

        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0, "Failed to create object")
        self.assertEqual(len(result.stderr), 0,
                         "There should not be an exception here")
        self.assertGreater(
            len(result.stdout), 0, "Failed to fetch organization")
        self.assertEqual(new_obj['name'], result.stdout['name'])

    def test_list_org(self):
        """@Test: Check if Org can be listed

        @Feature: Org - List

        @Assert: Org is listed

        """
        return_value = Org.list()
        self.assertEqual(
            return_value.return_code,
            0,
            "List Org - retcode")
        self.assertEqual(
            len(return_value.stderr),
            0,
            "There should not be an exception here"
        )

    @run_only_on('sat')
    def test_add_subnet(self):
        """@Test: Check if a subnet can be added to an Org

        @Feature: Org - Subnet

        @Assert: Subnet is added to the org

        """
        org_result = make_org()
        subnet_result = make_subnet()
        return_value = Org.add_subnet(
            {'name': org_result['name'], 'subnet': subnet_result['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Add subnet - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    @run_only_on('sat')
    def test_remove_subnet(self):
        """@Test: Check if a subnet can be removed from an Org

        @Feature: Org - Subnet

        @Assert: Subnet is removed from the org

        """
        org_result = make_org()
        subnet_result = make_subnet()
        Org.add_subnet(
            {'name': org_result['name'], 'subnet': subnet_result['name']})
        return_value = Org.remove_subnet(
            {'name': org_result['name'], 'subnet': subnet_result['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Remove Subnet - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    def test_add_user(self):
        """@Test: Check if a User can be added to an Org

        @Feature: Org - User

        @Assert: User is added to the org

        """
        org_result = make_org()
        user_result = make_user()
        return_value = Org.add_user(
            {'name': org_result['name'], 'user-id': user_result['id']})
        self.assertEqual(return_value.return_code, 0,
                         "Add User - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    def test_remove_user(self):
        """@Test: Check if a User can be removed from an Org

        @Feature: Org - User

        @Assert: User is removed from the org

        """
        org_result = make_org()
        user_result = make_user()
        Org.add_user(
            {'name': org_result['name'], 'user-id': user_result['login']})
        return_value = Org.remove_user(
            {'name': org_result['name'], 'user-id': user_result['login']})
        self.assertEqual(return_value.return_code, 0,
                         "Remove User - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    @run_only_on('sat')
    def test_add_hostgroup(self):
        """@Test: Check if a hostgroup can be added to an Org

        @Feature: Org - Hostrgroup

        @Assert: Hostgroup is added to the org

        """
        org_result = make_org()
        hostgroup_result = make_hostgroup()
        return_value = Org.add_hostgroup({
            'name': org_result['name'],
            'hostgroup': hostgroup_result['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Add Hostgroup - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    @run_only_on('sat')
    def test_remove_hostgroup(self):
        """@Test: Check if a hostgroup can be removed from an Org

        @Feature: Org - Subnet

        @Assert: Hostgroup is removed from the org

        """
        org_result = make_org()
        hostgroup_result = make_hostgroup()
        Org.add_hostgroup({
            'name': org_result['name'],
            'hostgroup': hostgroup_result['name']})
        return_value = Org.remove_hostgroup({
            'name': org_result['name'],
            'hostgroup': hostgroup_result['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Remove Hostgroup - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    @run_only_on('sat')
    def test_add_computeresource(self):
        """@Test: Check if a Compute Resource can be added to an Org

        @Feature: Org - Compute Resource

        @Assert: Compute Resource is added to the org

        """

        try:
            org = make_org()
            compute_res = make_compute_resource({
                'provider': FOREMAN_PROVIDERS['libvirt'],
                'url': "qemu+tcp://%s:16509/system" %
                conf.properties['main.server.hostname']})
        except CLIFactoryError as err:
            self.fail(err)
        return_value = Org.add_compute_resource({
            'name': org['name'],
            'compute-resource': compute_res['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Add ComputeResource - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")
        result = Org.info({'id': org['id']})
        self.assertEqual(result.stdout['compute-resources'][0],
                         compute_res['name'])

    @run_only_on('sat')
    @stubbed()
    def test_remove_computeresource(self):
        """@Test: Check if a ComputeResource can be removed from an Org

        @Feature: Org - ComputeResource

        @Assert: ComputeResource is removed from the org

        @status: manual

        """
        pass

    @run_only_on('sat')
    def test_add_medium(self):
        """@Test: Check if a Medium can be added to an Org

        @Feature: Org - Medium

        @Assert: Medium is added to the org

        """
        org_result = make_org()
        medium_result = make_medium()
        return_value = Org.add_medium({
            'name': org_result['name'],
            'medium': medium_result['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Add Medium - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    @run_only_on('sat')
    def test_remove_medium(self):
        """@Test: Check if a Medium can be removed from an Org

        @Feature: Org - Medium

        @Assert: Medium is removed from the org

        """
        org_result = make_org()
        medium_result = make_medium()
        Org.add_medium({
            'name': org_result['name'],
            'medium': medium_result['name']})
        return_value = Org.remove_medium({
            'name': org_result['name'],
            'medium': medium_result['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Remove Medium - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    @run_only_on('sat')
    @data(
        gen_string('alpha', 15),
        gen_string('alphanumeric', 15),
        gen_string('numeric', 15),
        gen_string('latin1', 15),
        gen_string('utf8', 15),
    )
    def test_add_configtemplate(self, data):
        """@Test: Check if a Config Template can be added to an Org

        @Feature: Org - Config Template

        @Assert: Config Template is added to the org

        """
        try:
            org = make_org()
            template = make_template({
                'name': data,
                'content': gen_string('alpha', 10),
            })
        except CLIFactoryError as err:
            self.fail(err)
        result = Org.add_config_template({
            'name': org['name'],
            'config-template': template['name']
        })
        self.assertEqual(result.return_code, 0,
                         "return code must be 0, instead got {0}".
                         format(result.return_code))
        self.assertEqual(
            len(result.stderr), 0, "There should not be an error here")
        result = Org.info({'id': org['id']})
        self.assertIn(
            u'{0} ({1})'. format(template['name'], template['type']),
            result.stdout['templates']
        )

    @run_only_on('sat')
    @data(
        gen_string('alpha', 15),
        gen_string('alphanumeric', 15),
        gen_string('numeric', 15),
        gen_string('latin1', 15),
        gen_string('utf8', 15),
    )
    def test_remove_configtemplate(self, data):
        """@Test: Check if a ConfigTemplate can be removed from an Org

        @Feature: Org - ConfigTemplate

        @Assert: ConfigTemplate is removed from the org

        """
        try:
            org = make_org()
            tmplt = make_template({
                'name': data,
                'content': gen_string('alpha', 10)
            })
        except CLIFactoryError as err:
            self.fail(err)

        # Add config-template
        result = Org.add_config_template({
            'name': org['name'],
            'config-template': tmplt['name']
        })
        self.assertEqual(result.return_code, 0,
                         "return code must be 0, instead got {0}".
                         format(result.return_code))
        self.assertEqual(
            len(result.stderr), 0, "There should not be an error here")
        result = Org.info({'id': org['id']})
        self.assertIn(
            u'{0} ({1})'. format(tmplt['name'], tmplt['type']),
            result.stdout['templates']
        )

        # Remove config-template
        result = Org.remove_config_template({
            'name': org['name'],
            'config-template': tmplt['name']
        })
        self.assertEqual(result.return_code, 0,
                         "return code must be 0, instead got {0}".
                         format(result.return_code))
        self.assertEqual(
            len(result.stderr), 0, "There should not be an error here")
        result = Org.info({'id': org['id']})
        self.assertNotIn(
            u'{0} ({1})'. format(tmplt['name'], tmplt['type']),
            result.stdout['templates']
        )

    @run_only_on('sat')
    def test_add_environment(self):
        """@Test: Check if an environment can be added to an Org

        @Feature: Org - Environment

        @Assert: Environment is added to the org

        """
        # Create a lifecycle environment.
        org_id = make_org()['id']
        lc_env_name = make_lifecycle_environment(
            {'organization-id': org_id})['name']

        # Read back information about the lifecycle environment. Verify the
        # sanity of that information.
        response = LifecycleEnvironment.list({
            'name': lc_env_name,
            'organization-id': org_id,
        })
        self.assertEqual(response.return_code, 0, response.stderr)
        self.assertEqual(response.stdout[0]['name'], lc_env_name)

    @run_only_on('sat')
    def test_remove_environment(self):
        """@Test: Check if an Environment can be removed from an Org

        @Feature: Org - Environment

        @Assert: Environment is removed from the org

        """
        # Create a lifecycle environment.
        org_id = make_org()['id']
        lc_env_name = make_lifecycle_environment(
            {'organization-id': org_id})['name']
        lc_env_attrs = {
            'name': lc_env_name,
            'organization-id': org_id,
        }

        # Read back information about the lifecycle environment. Verify the
        # sanity of that information.
        response = LifecycleEnvironment.list(lc_env_attrs)
        self.assertEqual(response.return_code, 0, response.stderr)
        self.assertEqual(response.stdout[0]['name'], lc_env_name)

        # Delete it.
        response = LifecycleEnvironment.delete(lc_env_attrs)
        self.assertEqual(response.return_code, 0, response.stderr)

        # We should get a zero-length response when searcing for the LC env.
        response = LifecycleEnvironment.list(lc_env_attrs)
        self.assertEqual(response.return_code, 0, response.stderr)
        self.assertEqual(len(response.stdout), 0, response.stdout)

    @run_only_on('sat')
    @stubbed("Needs to be re-worked!")
    def test_add_smartproxy(self):
        """@Test: Check if a Smartproxy can be added to an Org

        @Feature: Org - Smartproxy

        @Assert: Smartproxy is added to the org

        """
        org_result = make_org()
        proxy_result = make_proxy()
        return_value = Org.add_smart_proxy({
            'name': org_result['name'],
            'smart-proxy': proxy_result['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Add smartproxy - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    @run_only_on('sat')
    @stubbed("Needs to be re-worked!")
    def test_remove_smartproxy(self):
        """@Test: Check if a Smartproxy can be removed from an Org

        @Feature: Org - Smartproxy

        @Assert: Smartproxy is removed from the org

        """
        org_result = make_org()
        proxy_result = make_proxy()
        Org.add_smart_proxy({
            'name': org_result['name'],
            'smart-proxy': proxy_result['name']})
        return_value = Org.remove_smart_proxy({
            'name': org_result['name'],
            'smart-proxy': proxy_result['name']})
        self.assertEqual(return_value.return_code, 0,
                         "Remove smartproxy - retcode")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

    # Negative Create

    @data({'label': gen_string('alpha', 10),
           'name': gen_string('alpha', 300)},
          {'label': gen_string('alpha', 10),
           'name': gen_string('numeric', 300)},
          {'label': gen_string('alpha', 10),
           'name': gen_string('alphanumeric', 300)},
          {'label': gen_string('alpha', 10),
           'name': gen_string('utf8', 300)},
          {'label': gen_string('alpha', 10),
           'name': gen_string('latin1', 300)},
          {'label': gen_string('alpha', 10),
           'name': gen_string('html', 300)})
    def test_negative_create_0(self, test_data):
        """@test: Create organization with valid label and description, name is
        too long

        @feature: Organizations

        @assert: organization is not created

        """
        result = Org.create({'label': test_data['label'], 'description':
                             test_data['label'], 'name': test_data['name']})
        self.assertTrue(result.stderr)
        self.assertNotEqual(result.return_code, 0)

    @data(gen_string('alpha', 10),
          gen_string('numeric', 10),
          gen_string('alphanumeric', 10))
    def test_negative_create_1(self, test_data):
        """@test: Create organization with valid label and description, name is
        blank

        @feature: Organizations

        @assert: organization is not created

        """
        result = Org.create({'label': test_data, 'description': test_data,
                            'name': ''})
        self.assertTrue(result.stderr)
        self.assertNotEqual(result.return_code, 0)

    @data(gen_string('alpha', 10),
          gen_string('numeric', 10),
          gen_string('alphanumeric', 10))
    def test_negative_create_2(self, test_data):
        """@test: Create organization with valid label and description, name is
        whitespace

        @feature: Organizations

        @assert: organization is not created

        """
        result = Org.create({'label': test_data, 'description': test_data,
                             'name': ' \t'})
        self.assertGreater(
            len(result.stderr), 0, "There should be an exception here.")
        self.assertNotEqual(result.return_code, 0)

    @data(gen_string('alpha', 10),
          gen_string('numeric', 10),
          gen_string('alphanumeric', 10))
    def test_negative_create_3(self, test_data):
        """@test: Create organization with valid values, then create a new one
        with same values.

        @feature: Organizations

        @assert: organization is not created

        """
        result = Org.create({'label': test_data, 'description': test_data,
                             'name': test_data})
        self.assertFalse(result.stderr)
        self.assertEqual(result.return_code, 0)
        result = Org.create({'label': test_data, 'description': test_data,
                             'name': test_data})
        self.assertGreater(
            len(result.stderr), 0, "There should be an exception here.")
        self.assertNotEqual(result.return_code, 0)

    # Positive Delete

    @skip_if_bug_open('bugzilla', 1076568)
    @data(*positive_name_desc_label_data())
    def test_positive_delete_1(self, test_data):
        """@test: Create organization with valid values then delete it
        by ID

        @feature: Organizations

        @assert: organization is deleted

        @BZ: 1076568

        """

        new_obj = make_org(test_data)

        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])

        return_value = Org.delete({'id': new_obj['id']})
        self.assertEqual(return_value.return_code, 0, "Deletion failed")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

        # Can we find the object?
        result = Org.info({'id': new_obj['id']})
        self.assertNotEqual(
            result.return_code, 0, "Organization should be deleted")
        self.assertGreater(len(result.stderr), 0,
                           "There should not be an exception here")
        self.assertEqual(
            len(result.stdout), 0, "Output should be blank.")

    @skip_if_bug_open('bugzilla', 1076568)
    @data(*positive_name_desc_label_data())
    def test_positive_delete_2(self, test_data):
        """@test: Create organization with valid values then delete it
        by label

        @feature: Organizations

        @assert: organization is deleted

        @BZ: 1076568

        """

        new_obj = make_org(test_data)

        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])

        return_value = Org.delete({'label': new_obj['label']})
        self.assertEqual(return_value.return_code, 0, "Deletion failed")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

        # Can we find the object?
        result = Org.info({'id': new_obj['id']})
        self.assertNotEqual(
            result.return_code, 0, "Organization should be deleted")
        self.assertGreater(len(result.stderr), 0,
                           "There should not be an exception here")
        self.assertEqual(
            len(result.stdout), 0, "Output should be blank.")

    @skip_if_bug_open('bugzilla', 1076568)
    @data(*positive_name_desc_label_data())
    def test_positive_delete_3(self, test_data):
        """@test: Create organization with valid values then delete it
        by name

        @feature: Organizations

        @assert: organization is deleted

        @BZ: 1076568

        """

        new_obj = make_org(test_data)

        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})

        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])

        return_value = Org.delete({'name': new_obj['name']})
        self.assertEqual(return_value.return_code, 0, "Deletion failed")
        self.assertEqual(
            len(return_value.stderr), 0, "There should not be an error here")

        # Can we find the object?
        result = Org.info({'id': new_obj['id']})
        self.assertNotEqual(
            result.return_code, 0, "Organization should be deleted")
        self.assertGreater(len(result.stderr), 0,
                           "There should not be an exception here")
        self.assertEqual(
            len(result.stdout), 0, "Output should be blank.")

    @data({'name': gen_string("latin1", 10)},
          {'name': gen_string("utf8", 10)},
          {'name': gen_string("alpha", 10)},
          {'name': gen_string("alphanumeric", 10)},
          {'name': gen_string("numeric", 10)},
          {'name': gen_string("html", 10)})
    def test_positive_update_1(self, test_data):
        """@test: Create organization with valid values then update its name

        @feature: Organizations

        @assert: organization name is updated

        """

        new_obj = make_org()
        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])

        # Update the org name
        result = Org.update({'id': new_obj['id'],
                             'new-name': test_data['name']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(
            len(result.stderr), 0, "There should not be an error here")

        # Fetch the org again
        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(
            result.stdout['name'],
            test_data['name'],
            "Org name was not updated"
        )

    @skip_if_bug_open('bugzilla', 1114136)
    @data({'description': gen_string("latin1", 10)},
          {'description': gen_string("utf8", 10)},
          {'description': gen_string("alpha", 10)},
          {'description': gen_string("alphanumeric", 10)},
          {'description': gen_string("numeric", 10)},
          {'description': gen_string("html", 10)})
    def test_positive_update_3(self, test_data):
        """@test: Create organization with valid values then update its
        description

        @feature: Organizations

        @assert: organization description is updated

        @bz: 1114136

        """

        new_obj = make_org()
        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])

        # Update the org name
        result = Org.update({'id': new_obj['id'],
                             'description': test_data['description']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(
            len(result.stderr), 0, "There should not be an error here")

        # Fetch the org again
        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(
            result.stdout['description'],
            test_data['description'],
            "Org desc was not updated"
        )

    @skip_if_bug_open('bugzilla', 1114136)
    @data({'description': gen_string("latin1", 10),
           'name': gen_string("latin1", 10)},
          {'description': gen_string("utf8", 10),
           'name': gen_string("utf8", 10)},
          {'description': gen_string("alpha", 10),
           'name': gen_string("alpha", 10)},
          {'description': gen_string("alphanumeric", 10),
           'name': gen_string("alphanumeric", 10)},
          {'description': gen_string("numeric", 10),
           'name': gen_string("numeric", 10)},
          {'description': gen_string("html", 10),
           'name': gen_string("html", 10)})
    def test_positive_update_4(self, test_data):
        """@test: Create organization with valid values then update all values

        @feature: Organizations

        @assert: organization name and description are updated

        @bz: 1114136

        """

        new_obj = make_org()
        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])
        self.assertEqual(new_obj['description'], result.stdout['description'])

        # Update the org name
        result = Org.update({'id': new_obj['id'],
                             'new-name': test_data['name'],
                             'description': test_data['description']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(
            len(result.stderr), 0, "There should not be an error here")

        # Fetch the org again
        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(
            result.stdout['description'],
            test_data['description'],
            "Org desc was not updated"
        )
        self.assertEqual(
            result.stdout['name'],
            test_data['name'],
            "Org name was not updated"
        )

    # Negative Update

    @data({'name': ' '},
          {'name': gen_string('alpha', 300)},
          {'name': gen_string('numeric', 300)},
          {'name': gen_string('alphanumeric', 300)},
          {'name': gen_string('utf8', 300)},
          {'name': gen_string('latin1', 300)},
          {'name': gen_string('html', 300)})
    def test_negative_update_1(self, test_data):
        """@test: Create organization then fail to update
        its name

        @feature: Organizations

        @assert: organization name is not updated

        @bz: 1076541

        """

        new_obj = make_org()
        # Can we find the new object?
        result = Org.info({'id': new_obj['id']})
        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(new_obj['name'], result.stdout['name'])

        # Update the org name
        result = Org.update({'id': new_obj['id'],
                             'new-name': test_data['name']})
        self.assertNotEqual(result.return_code, 0)
        self.assertGreater(len(result.stderr), 0,
                           "There should be error - hammer expects error")

    # Miscelaneous

    @stubbed()
    @data("""DATADRIVENGOESHERE
        name, label and description are is alpha
        name, label and description are is numeric
        name, label and description are is alphanumeric
        name, label and description are is utf-8
        name, label and description are is latin1
        name, label and description are is html
    """)
    def test_list_key_1(self, test_data):
        """@test: Create organization and list it

        @feature: Organizations

        @assert: organization is displayed/listed

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        name, label and description are is alpha
        name, label and description are is numeric
        name, label and description are is alphanumeric
        name, label and description are is utf-8
        name, label and description are is latin1
        name, label and description are is html
    """)
    def test_search_key_1(self, test_data):
        """@test: Create organization and search/find it

        @feature: Organizations

        @assert: organization can be found

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        name, label and description are is alpha
        name, label and description are is numeric
        name, label and description are is alphanumeric
        name, label and description are is utf-8
        name, label and description are is latin1
        name, label and description are is html
    """)
    def test_info_key_1(self, test_data):
        """@test: Create single organization and get its info

        @feature: Organizations

        @assert: specific information for organization matches the
        creation values

        @status: manual

        """

        pass

    # Associations

    @stubbed()
    @data("""DATADRIVENGOESHERE
        domain name is alpha
        domain name is numeric
        domain name is alph_numeric
        domain name is utf-8
        domain name is latin1
        domain name is html
    """)
    def test_remove_domain_1(self, test_data):
        """@test: Add a domain to an organization and remove it by organization
        name and domain name

        @feature: Organizations

        @assert: the domain is removed from the organization

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        domain name is alpha
        domain name is numeric
        domain name is alph_numeric
        domain name is utf-8
        domain name is latin1
        domain name is html
    """)
    def test_remove_domain_2(self, test_data):
        """@test: Add a domain to an organization and remove it by organization
        ID and domain name

        @feature: Organizations

        @assert: the domain is removed from the organization

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        domain name is alpha
        domain name is numeric
        domain name is alph_numeric
        domain name is utf-8
        domain name is latin1
        domain name is html
    """)
    def test_remove_domain_3(self, test_data):
        """@test: Add a domain to an organization and remove it by organization
        name and domain ID

        @feature: Organizations

        @assert: the domain is removed from the organization

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        domain name is alpha
        domain name is numeric
        domain name is alph_numeric
        domain name is utf-8
        domain name is latin1
        domain name is html
    """)
    def test_remove_domain_4(self, test_data):
        """@test: Add a domain to an organization and remove it by organization
        ID and domain ID

        @feature: Organizations

        @assert: the domain is removed from the organization

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        user name is alpha
        user name is numeric
        user name is alpha_numeric
        user name is utf-8
        user name is latin1
        user name is html
    """)
    def test_remove_user_1(self, test_data):
        """@test: Create different types of users then add/remove user
        by using the organization ID

        @feature: Organizations

        @assert: User is added and then removed from organization

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        user name is alpha
        user name is numeric
        user name is alpha_numeric
        user name is utf-8
        user name is latin1
        user name is html
    """)
    def test_remove_user_2(self, test_data):
        """@test: Create different types of users then add/remove user
        by using the organization name

        @feature: Organizations

        @assert: The user is added then removed from the organization

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        user name is alpha and admin
        user name is numeric and admin
        user name is alpha_numeric and admin
        user name is utf-8 and admin
        user name is latin1 and admin
        user name is html and admin
    """)
    def test_remove_user_3(self, test_data):
        """@test: Create admin users then add user and remove it
        by using the organization name

        @feature: Organizations

        @assert: The user is added then removed from the organization

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        hostgroup name is alpha
        hostgroup name is numeric
        hostgroup name is alpha_numeric
        hostgroup name is utf-8
        hostgroup name is latin1
        hostgroup name is html
    """)
    def test_remove_hostgroup_1(self, test_data):
        """@test: Add a hostgroup and remove it by using the organization
        name and hostgroup name

        @feature: Organizations

        @assert: hostgroup is added to organization then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        hostgroup name is alpha
        hostgroup name is numeric
        hostgroup name is alpha_numeric
        hostgroup name is utf-8
        hostgroup name is latin1
        hostgroup name is html
    """)
    def test_remove_hostgroup_2(self, test_data):
        """@test: Add a hostgroup and remove it by using the organization
        ID and hostgroup name

        @feature: Organizations

        @assert: hostgroup is added to organization then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        hostgroup name is alpha
        hostgroup name is numeric
        hostgroup name is alpha_numeric
        hostgroup name is utf-8
        hostgroup name is latin1
        hostgroup name is html
    """)
    def test_remove_hostgroup_3(self, test_data):
        """@test: Add a hostgroup and remove it by using the organization
        name and hostgroup ID

        @feature: Organizations

        @assert: hostgroup is added to organization then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        hostgroup name is alpha
        hostgroup name is numeric
        hostgroup name is alpha_numeric
        hostgroup name is utf-8
        hostgroup name is latin1
        hostgroup name is html
    """)
    def test_remove_hostgroup_4(self, test_data):
        """@test: Add a hostgroup and remove it by using the organization
        ID and hostgroup ID

        @feature: Organizations

        @assert: hostgroup is added to organization then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        smartproxy name is alpha
        smartproxy name is numeric
        smartproxy name is alpha_numeric
        smartproxy name  is utf-8
        smartproxy name is latin1
        smartproxy name is html
    """)
    def test_add_smartproxy_1(self, test_data):
        """@test: Add a smart proxy by using organization name and smartproxy name

        @feature: Organizations

        @assert: smartproxy is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        smartproxy name is alpha
        smartproxy name is numeric
        smartproxy name is alpha_numeric
        smartproxy name  is utf-8
        smartproxy name is latin1
        smartproxy name is html
    """)
    def test_add_smartproxy_2(self, test_data):
        """@test: Add a smart proxy by using organization ID and smartproxy name

        @feature: Organizations

        @assert: smartproxy is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        smartproxy name is alpha
        smartproxy name is numeric
        smartproxy name is alpha_numeric
        smartproxy name  is utf-8
        smartproxy name is latin1
        smartproxy name is html
    """)
    def test_add_smartproxy_3(self, test_data):
        """@test: Add a smart proxy by using organization name and smartproxy ID

        @feature: Organizations

        @assert: smartproxy is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        smartproxy name is alpha
        smartproxy name is numeric
        smartproxy name is alpha_numeric
        smartproxy name  is utf-8
        smartproxy name is latin1
        smartproxy name is html
    """)
    def test_add_smartproxy_4(self, test_data):
        """@test: Add a smart proxy by using organization ID and smartproxy ID

        @feature: Organizations

        @assert: smartproxy is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @data(gen_string('alpha', 10),
          gen_string('numeric', 10),
          gen_string('alphanumeric', 10),
          gen_string('utf8', 10),
          gen_string('latin1', 10))
    def test_add_subnet_1(self, name):
        """@test: Add a subnet by using organization name and subnet name

        @feature: Organizations

        @assert: subnet is added

        """

        try:
            org = make_org()
            new_subnet = make_subnet({'name': name})
        except CLIFactoryError as err:
            self.fail(err)

        result = Org.add_subnet({
            'name': org['name'],
            'subnet': new_subnet['name'],
        })
        self.assertEqual(result.return_code, 0,
                         "return code must be 0, instead got {0}".
                         format(result.return_code))

        result = Org.info({'id': org['id']})
        self.assertIn(name, result.stdout['subnets'][0])

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        subnet name is alpha
        subnet name is numeric
        subnet name is alpha_numeric
        subnet name is utf-8
        subnet name is latin1
        subnet name  is html
    """)
    def test_add_subnet_2(self, test_data):
        """@test: Add a subnet by using organization ID and subnet name

        @feature: Organizations

        @assert: subnet is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        subnet name is alpha
        subnet name is numeric
        subnet name is alpha_numeric
        subnet name is utf-8
        subnet name is latin1
        subnet name  is html
    """)
    def test_add_subnet_3(self, test_data):
        """@test: Add a subnet by using organization name and subnet ID

        @feature: Organizations

        @assert: subnet is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        subnet name is alpha
        subnet name is numeric
        subnet name is alpha_numeric
        subnet name is utf-8
        subnet name is latin1
        subnet name  is html
    """)
    def test_add_subnet_4(self, test_data):
        """@test: Add a subnet by using organization ID and subnet ID

        @feature: Organizations

        @assert: subnet is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        domain name is alpha
        domain name is numeric
        domain name is alph_numeric
        domain name is utf-8
        domain name is latin1
        domain name is html
    """)
    def test_add_domain_1(self, test_data):
        """@test: Add a domain to an organization

        @feature: Organizations

        @assert: Domain is added to organization

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        user name is alpha
        user name is numeric
        user name is alpha_numeric
        user name is utf-8
        user name is latin1
        user name is html
    """)
    def test_add_user_1(self, test_data):
        """@test: Create different types of users then add user
        by using the organization ID

        @feature: Organizations

        @assert: User is added to organization

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        user name is alpha
        user name is numeric
        user name is alpha_numeric
        user name is utf-8
        user name is latin1
        user name is html
    """)
    def test_add_user_2(self, test_data):
        """@test: Create different types of users then add user
        by using the organization name

        @feature: Organizations

        @assert: User is added to organization

        @status: manual

        """

        pass

    @stubbed()
    @data("""DATADRIVENGOESHERE
        user name is alpha and an admin
        user name is numeric and an admin
        user name is alpha_numeric and an admin
        user name is utf-8 and an admin
        user name is latin1 and an admin
        user name is html and an admin
    """)
    def test_add_user_3(self, test_data):
        """@test: Create admin users then add user by using the organization name

        @feature: Organizations

        @assert: User is added to organization

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        hostgroup name is alpha
        hostgroup name is numeric
        hostgroup name is alpha_numeric
        hostgroup name is utf-8
        hostgroup name is latin1
        hostgroup name is html
    """)
    def test_add_hostgroup_1(self, test_data):
        """@test: Add a hostgroup by using the organization
        name and hostgroup name

        @feature: Organizations

        @assert: hostgroup is added to organization

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        hostgroup name is alpha
        hostgroup name is numeric
        hostgroup name is alpha_numeric
        hostgroup name is utf-8
        hostgroup name is latin1
        hostgroup name is html
    """)
    def test_add_hostgroup_2(self, test_data):
        """@test: Add a hostgroup by using the organization
        ID and hostgroup name

        @feature: Organizations

        @assert: hostgroup is added to organization

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        hostgroup name is alpha
        hostgroup name is numeric
        hostgroup name is alpha_numeric
        hostgroup name is utf-8
        hostgroup name is latin1
        hostgroup name is html
    """)
    def test_add_hostgroup_3(self, test_data):
        """@test: Add a hostgroup by using the organization
        name and hostgroup ID

        @feature: Organizations

        @assert: hostgroup is added to organization

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        hostgroup name is alpha
        hostgroup name is numeric
        hostgroup name is alpha_numeric
        hostgroup name is utf-8
        hostgroup name is latin1
        hostgroup name is html
    """)
    def test_add_hostgroup_4(self, test_data):
        """@test: Add a hostgroup by using the organization
        ID and hostgroup ID

        @feature: Organizations

        @assert: hostgroup is added to organization

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        computeresource is alpha
        computeresource is numeric
        computeresource is alpha_numeric
        computeresource is utf-8
        computeresource is latin1
        computeresource is html
    """)
    def test_remove_computeresource_1(self, test_data):
        """@test: Remove computeresource by using the organization
        name and computeresource name

        @feature: Organizations

        @assert: computeresource is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        computeresource is alpha
        computeresource is numeric
        computeresource is alpha_numeric
        computeresource is utf-8
        computeresource is latin1
        computeresource is html
    """)
    def test_remove_computeresource_2(self, test_data):
        """@test: Remove computeresource by using the organization
        ID and computeresource name

        @feature: Organizations

        @assert: computeresource is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        computeresource is alpha
        computeresource is numeric
        computeresource is alpha_numeric
        computeresource is utf-8
        computeresource is latin1
        computeresource is html
    """)
    def test_remove_computeresource_3(self, test_data):
        """@test: Remove computeresource by using the organization
        name and computeresource ID

        @feature: Organizations

        @assert: computeresource is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        computeresource is alpha
        computeresource is numeric
        computeresource is alpha_numeric
        computeresource is utf-8
        computeresource is latin1
        computeresource is html
    """)
    def test_remove_computeresource_4(self, test_data):
        """@test: Remove computeresource by using the organization
        ID and computeresource ID

        @feature: Organizations

        @assert: computeresource is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        medium name is alpha
        medium name is numeric
        medium name is alpha_numeric
        medium name is utf-8
        medium name is latin1
        medium name is html
        """)
    def test_remove_medium_1(self, test_data):
        """@test: Remove medium by using organization name and medium name

        @feature: Organizations

        @assert: medium is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        medium name is alpha
        medium name is numeric
        medium name is alpha_numeric
        medium name is utf-8
        medium name is latin1
        medium name is html
        """)
    def test_remove_medium_2(self, test_data):
        """@test: Remove medium by using organization ID and medium name

        @feature: Organizations

        @assert: medium is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        medium name is alpha
        medium name is numeric
        medium name is alpha_numeric
        medium name is utf-8
        medium name is latin1
        medium name is html
        """)
    def test_remove_medium_3(self, test_data):
        """@test: Remove medium by using organization name and medium ID

        @feature: Organizations

        @assert: medium is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        medium name is alpha
        medium name is numeric
        medium name is alpha_numeric
        medium name is utf-8
        medium name is latin1
        medium name is html
        """)
    def test_remove_medium_4(self, test_data):
        """@test: Remove medium by using organization ID and medium ID

        @feature: Organizations

        @assert: medium is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        configtemplate name is alpha
        configtemplate name is numeric
        configtemplate name is alpha_numeric
        configtemplate name is utf-8
        configtemplate name is latin1
        configtemplate name  is html
    """)
    def test_remove_configtemplate_1(self, test_data):
        """@test: Remove config template

        @feature: Organizations

        @assert: configtemplate is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        environment name is alpha
        environment name is numeric
        environment name is alpha_numeric
        environment name is utf-8
        environment name is latin1
        environment name  is html
    """)
    def test_remove_environment_1(self, test_data):
        """@test: Remove environment by using organization name and
        evironment name

        @feature: Organizations

        @assert: environment is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        environment name is alpha
        environment name is numeric
        environment name is alpha_numeric
        environment name is utf-8
        environment name is latin1
        environment name  is html
    """)
    def test_remove_environment_2(self, test_data):
        """@test: Remove environment by using organization ID and
        evironment name

        @feature: Organizations

        @assert: environment is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        environment name is alpha
        environment name is numeric
        environment name is alpha_numeric
        environment name is utf-8
        environment name is latin1
        environment name  is html
    """)
    def test_remove_environment_3(self, test_data):
        """@test: Remove environment by using organization name and
        evironment ID

        @feature: Organizations

        @assert: environment is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        environment name is alpha
        environment name is numeric
        environment name is alpha_numeric
        environment name is utf-8
        environment name is latin1
        environment name  is html
    """)
    def test_remove_environment_4(self, test_data):
        """@test: Remove environment by using organization ID and
        evironment ID

        @feature: Organizations

        @assert: environment is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        smartproxy name is alpha
        smartproxy name is numeric
        smartproxy name is alpha_numeric
        smartproxy name  is utf-8
        smartproxy name is latin1
        smartproxy name is html
    """)
    def test_remove_smartproxy_1(self, test_data):
        """@test: Remove smartproxy by using organization name and smartproxy name

        @feature: Organizations

        @assert: smartproxy is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        smartproxy name is alpha
        smartproxy name is numeric
        smartproxy name is alpha_numeric
        smartproxy name  is utf-8
        smartproxy name is latin1
        smartproxy name is html
    """)
    def test_remove_smartproxy_2(self, test_data):
        """@test: Remove smartproxy by using organization ID and smartproxy name

        @feature: Organizations

        @assert: smartproxy is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        smartproxy name is alpha
        smartproxy name is numeric
        smartproxy name is alpha_numeric
        smartproxy name  is utf-8
        smartproxy name is latin1
        smartproxy name is html
    """)
    def test_remove_smartproxy_3(self, test_data):
        """@test: Remove smartproxy by using organization name and smartproxy ID

        @feature: Organizations

        @assert: smartproxy is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        smartproxy name is alpha
        smartproxy name is numeric
        smartproxy name is alpha_numeric
        smartproxy name  is utf-8
        smartproxy name is latin1
        smartproxy name is html
    """)
    def test_remove_smartproxy_4(self, test_data):
        """@test: Remove smartproxy by using organization ID and smartproxy ID

        @feature: Organizations

        @assert: smartproxy is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        computeresource is alpha
        computeresource is numeric
        computeresource is alpha_numeric
        computeresource is utf-8
        computeresource is latin1
        computeresource is html
    """)
    def test_add_computeresource_1(self, test_data):
        """@test: Add compute resource using the organization
        name and computeresource name

        @feature: Organizations

        @assert: computeresource is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        computeresource is alpha
        computeresource is numeric
        computeresource is alpha_numeric
        computeresource is utf-8
        computeresource is latin1
        computeresource is html
    """)
    def test_add_computeresource_2(self, test_data):
        """@test: Add compute resource using the organization
        ID and computeresource name

        @feature: Organizations

        @assert: computeresource is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        computeresource is alpha
        computeresource is numeric
        computeresource is alpha_numeric
        computeresource is utf-8
        computeresource is latin1
        computeresource is html
    """)
    def test_add_computeresource_3(self, test_data):
        """@test: Add compute resource using the organization
        name and computeresource ID

        @feature: Organizations

        @assert: computeresource is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        computeresource is alpha
        computeresource is numeric
        computeresource is alpha_numeric
        computeresource is utf-8
        computeresource is latin1
        computeresource is html
    """)
    def test_add_computeresource_4(self, test_data):
        """@test: Add compute resource using the organization
        ID and computeresource ID

        @feature: Organizations

        @assert: computeresource is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        medium name is alpha
        medium name is numeric
        medium name is alpha_numeric
        medium name is utf-8
        medium name is latin1
        medium name is html
    """)
    def test_add_medium_1(self, test_data):
        """@test: Add medium by using the organization name and medium name

        @feature: Organizations

        @assert: medium is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        medium name is alpha
        medium name is numeric
        medium name is alpha_numeric
        medium name is utf-8
        medium name is latin1
        medium name is html
    """)
    def test_add_medium_2(self, test_data):
        """@test: Add medium by using the organization ID and medium name

        @feature: Organizations

        @assert: medium is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        medium name is alpha
        medium name is numeric
        medium name is alpha_numeric
        medium name is utf-8
        medium name is latin1
        medium name is html
    """)
    def test_add_medium_3(self, test_data):
        """@test: Add medium by using the organization name and medium ID

        @feature: Organizations

        @assert: medium is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        medium name is alpha
        medium name is numeric
        medium name is alpha_numeric
        medium name is utf-8
        medium name is latin1
        medium name is html
    """)
    def test_add_medium_4(self, test_data):
        """@test: Add medium by using the organization ID and medium ID

        @feature: Organizations

        @assert: medium is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        configtemplate name is alpha
        configtemplate name is numeric
        configtemplate name is alpha_numeric
        configtemplate name is utf-8
        configtemplate name is latin1
        configtemplate name  is html
    """)
    def test_add_configtemplate_1(self, test_data):
        """@test: Add config template by using organization name and
        configtemplate name

        @feature: Organizations

        @assert: configtemplate is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        configtemplate name is alpha
        configtemplate name is numeric
        configtemplate name is alpha_numeric
        configtemplate name is utf-8
        configtemplate name is latin1
        configtemplate name  is html
    """)
    def test_add_configtemplate_2(self, test_data):
        """@test: Add config template by using organization ID and
        configtemplate name

        @feature: Organizations

        @assert: configtemplate is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        configtemplate name is alpha
        configtemplate name is numeric
        configtemplate name is alpha_numeric
        configtemplate name is utf-8
        configtemplate name is latin1
        configtemplate name  is html
    """)
    def test_add_configtemplate_3(self, test_data):
        """@test: Add config template by using organization name and
        configtemplate ID

        @feature: Organizations

        @assert: configtemplate is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        configtemplate name is alpha
        configtemplate name is numeric
        configtemplate name is alpha_numeric
        configtemplate name is utf-8
        configtemplate name is latin1
        configtemplate name  is html
    """)
    def test_add_configtemplate_4(self, test_data):
        """@test: Add config template by using organization ID and
        configtemplate ID

        @feature: Organizations

        @assert: configtemplate is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        environment name is alpha
        environment name is numeric
        environment name is alpha_numeric
        environment name is utf-8
        environment name is latin1
        environment name  is html
    """)
    def test_add_environment_1(self, test_data):
        """@test: Add environment by using organization name and evironment name

        @feature: Organizations

        @assert: environment is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        environment name is alpha
        environment name is numeric
        environment name is alpha_numeric
        environment name is utf-8
        environment name is latin1
        environment name  is html
    """)
    def test_add_environment_2(self, test_data):
        """@test: Add environment by using organization ID and evironment name

        @feature: Organizations

        @assert: environment is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        environment name is alpha
        environment name is numeric
        environment name is alpha_numeric
        environment name is utf-8
        environment name is latin1
        environment name  is html
    """)
    def test_add_environment_3(self, test_data):
        """@test: Add environment by using organization name and evironment ID

        @feature: Organizations

        @assert: environment is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        environment name is alpha
        environment name is numeric
        environment name is alpha_numeric
        environment name is utf-8
        environment name is latin1
        environment name  is html
    """)
    def test_add_environment_4(self, test_data):
        """@test: Add environment by using organization ID and evironment ID

        @feature: Organizations

        @assert: environment is added

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        subnet name is alpha
        subnet name is numeric
        subnet name is alpha_numeric
        subnet name is utf-8
        subnet name is latin1
        subnet name  is html
    """)
    def test_remove_subnet_1(self, test_data):
        """@test: Remove subnet by using organization name and subnet name

        @feature: Organizations

        @assert: subnet is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        subnet name is alpha
        subnet name is numeric
        subnet name is alpha_numeric
        subnet name is utf-8
        subnet name is latin1
        subnet name  is html
    """)
    def test_remove_subnet_2(self, test_data):
        """@test: Remove subnet by using organization ID and subnet name

        @feature: Organizations

        @assert: subnet is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        subnet name is alpha
        subnet name is numeric
        subnet name is alpha_numeric
        subnet name is utf-8
        subnet name is latin1
        subnet name  is html
    """)
    def test_remove_subnet_3(self, test_data):
        """@test: Remove subnet by using organization name and subnet ID

        @feature: Organizations

        @assert: subnet is added then removed

        @status: manual

        """

        pass

    @run_only_on('sat')
    @stubbed()
    @data("""DATADRIVENGOESHERE
        subnet name is alpha
        subnet name is numeric
        subnet name is alpha_numeric
        subnet name is utf-8
        subnet name is latin1
        subnet name  is html
    """)
    def test_remove_subnet_4(self, test_data):
        """@test: Remove subnet by using organization ID and subnet ID

        @feature: Organizations

        @assert: subnet is added then removed

        @status: manual

        """

        pass
