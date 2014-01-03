# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

"""
Implements Host Group UI
"""

from robottelo.ui.base import Base
from robottelo.ui.locators import locators
from selenium.webdriver.support.select import Select


class Hostgroup(Base):
    """
    Manipulates hostgroup from UI
    """

    def __init__(self, browser):
        """
        Sets up the browser object.
        """
        self.browser = browser

    def create(self, name, parent=None, environment=None):
        """
        Creates a new hostgroup from UI
        """

        self.wait_until_element(locators["hostgroups.new"]).click()

        if self.wait_until_element(locators["hostgroups.name"]):
            self.find_element(locators["hostgroups.name"]).send_keys(name)
            if parent:
                Select(self.find_element(
                    locators["hostgroups.parent"])
                ).select_by_visible_text(parent)
            if environment:
                Select(self.find_element(
                    locators["hostgroups.environment"])
                ).select_by_visible_text(environment)
            self.find_element(locators["submit"]).click()
        else:
            raise Exception("Could not create new hostgroup.")

    def delete(self, name, really=False):
        """
        Deletes existing hostgroup from UI
        """

        dropdown = self.search(name, locators["hostgroups.dropdown"])
        if dropdown:
            dropdown.click()
            self.wait_for_ajax()
            element = self.wait_until_element(
                (locators["hostgroups.delete"][0],
                 locators["hostgroups.delete"][1] % name))
            if element:
                element.click()
                if really:
                    alert = self.browser.switch_to_alert()
                    alert.accept()
                else:
                    alert = self.browser.switch_to_alert()
                    alert.dismiss()
            else:
                raise Exception(
                    "Could not select the hostgroup for deletion.")
        else:
            raise Exception("Could not find hostgroup '%s'" % name)

    def update(self, name, new_name=None, parent=None, environment=None):
        """
        Updates existing hostgroup from UI
        """

        element = self.search(name, locators["hostgroups.hostgroup"])

        if element:
            element.click()
            self.wait_for_ajax()
            if parent:
                Select(self.find_element(
                    locators["hostgroups.parent"])
                ).select_by_visible_text(parent)
            if environment:
                Select(self.find_element(
                    locators["hostgroups.environment"])
                ).select_by_visible_text(environment)
            if new_name:
                self.field_update("hostgroups.name", new_name)
            self.find_element(locators["submit"]).click()
        else:
            raise Exception("Could not find hostgroup '%s'" % name)