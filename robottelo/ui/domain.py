# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

"""
Implements Domain UI
"""
from robottelo.ui.base import Base
from robottelo.ui.locators import locators, common_locators
from robottelo.ui.navigator import Navigator
from selenium.webdriver.support.select import Select


class Domain(Base):
    "Manipulates Foreman's domain from UI"

    def _configure_domain(self, description=None, dns_proxy=None):
        """
        Configures domain description and dns proxy
        """

        if description:
            if self.wait_until_element(locators["domain.description"]):
                self.field_update("domain.description", description)
        if dns_proxy:
            element = self.find_element(locators["domain.dns_proxy"])
            Select(element).select_by_visible_text(dns_proxy)
        self.find_element(common_locators["submit"]).click()
        self.wait_for_ajax()

    def create(self, name, description=None, dns_proxy=None):
        """
        Creates new domain with name, description and dns_proxy
        """

        self.wait_until_element(locators["domain.new"]).click()

        if self.wait_until_element(locators["domain.name"]):
            self.find_element(locators["domain.name"]).send_keys(name)
            self._configure_domain(description, dns_proxy)
        else:
            raise Exception(
                "Could not create new domain '%s'" % name)

    def search(self, description, timeout=None):
        """
        Searches existing domain from UI
        """
        Navigator(self.browser).go_to_domains()
        self.wait_for_ajax()
        if len(description) <= 30:
            element = self.search_entity(
                description, locators["domain.domain_description"],
                timeout=timeout)
        else:
            element = self.search_entity(
                description, common_locators["select_filtered_entity"],
                timeout=timeout)
        return element

    def delete(self, description, really):
        """
        Delete existing domain from UI
        """
        self.delete_entity(description, really,
                           locators['domain.domain_description'],
                           locators['domain.delete'])

    def update(self, old_description, new_name=None,
               description=None, dns_proxy=None):
        """
        Update an existing domain's name, description and dns_proxy
        """
        element = self.search(old_description)

        if element:
            element.click()
            if self.wait_until_element(locators["domain.name"]):
                self.field_update("domain.name", new_name)
            self._configure_domain(description, dns_proxy)
        else:
            raise Exception(
                "Could not update the domain '%s'" % old_description)

    def set_domain_parameter(self, domain_description,
                             param_name, param_value):
        """
        Add new parameter for domain
        """

        element = self.search(domain_description)

        if element:
            element.click()
            self.set_parameter(param_name, param_value)
        else:
            raise Exception(
                "Could not set parameter '%s'" % param_name)

    def remove_domain_parameter(self, domain_description, param_name):
        """
        Remove new parameter from domain
        """

        element = self.search(domain_description)

        if element:
            element.click()
            self.remove_parameter(param_name)
        else:
            raise Exception(
                "Could not remove parameter '%s'" % param_name)
