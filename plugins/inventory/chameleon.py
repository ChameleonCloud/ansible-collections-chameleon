#!/usr/bin/env python

import collections

from ansible.errors import AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin

try:
    import openstack

    HAS_SDK = True
except ImportError:
    HAS_SDK = False


class InventoryModule(BaseInventoryPlugin):
    NAME = "chameleon"  # used internally by Ansible, it should match the file name but not required

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache=cache)

        if not HAS_SDK:
            raise AnsibleParserError("Could not import Python library openstacksdk")

        # Redirect logging to stderr so it does not mix with output, in
        # particular JSON output of ansible-inventory.
        # TODO: Integrate openstack's logging with Ansible's logging.
        # if self.display.verbosity > 3:
        #     openstack.enable_logging(debug=True, stream=sys.stderr)
        # else:
        #     openstack.enable_logging(stream=sys.stderr)

        config = self._read_config_data(path)

        if "plugin" not in config and "clouds" not in config:
            raise AnsibleParserError(
                "Invalid OpenStack inventory configuration file found,"
                " missing 'plugin' and 'clouds' keys."
            )

        nodes = self._fetch_nodes(path, cache)

        # determine inventory hostnames

        count = collections.Counter(s["name"] for s in nodes)

        # use name as hostname, except on conflict, use uuid in that case
        inventory = dict(
            ((node["name"], node) if count[node["name"]] == 1 else (node["id"], node))
            for node in nodes
        )

        for hostname, node in inventory.items():
            host_vars = self._generate_host_vars(hostname, node)
            self._add_host(hostname, host_vars)

    def _generate_host_vars(self, hostname, node):
        """generate ansible variables for an ironic idrac node"""

        host_vars = dict(ironic=node)

        host_vars["bmc_ip"] = node.driver_info.get("ipmi_address")
        host_vars["bmc_user"] = node.driver_info.get("ipmi_username")
        host_vars["bmc_password"] = node.driver_info.get("ipmi_password")

        return host_vars

    def _add_host(self, hostname, host_vars):
        self.inventory.add_host(hostname, group="all")

        for k, v in host_vars.items():
            self.inventory.set_variable(hostname, k, v)

    def _fetch_nodes(self, path, cache):
        nodes = None

        self.display.vvvv("Retrieving servers from Openstack clouds")

        cloud = openstack.connect()

        nodes = []

        try:
            for node in cloud.baremetal.nodes(details=True, associated=False):
                nodes.append(node)
        except openstack.exceptions.OpenStackCloudException as e:
            self.display.warning(
                "Fetching servers for cloud {0} failed with: {1}".format(
                    cloud.name, str(e)
                )
            )
            if self.get_option("fail_on_errors"):
                raise

        return nodes

    def verify_file(self, path):
        if super(InventoryModule, self).verify_file(path):
            for fn in ("chameleon", "openstack", "clouds"):
                for suffix in ("yaml", "yml"):
                    maybe = "{fn}.{suffix}".format(fn=fn, suffix=suffix)
                    if path.endswith(maybe):
                        self.display.vvvv(
                            "OpenStack inventory configuration file found:"
                            " {0}".format(maybe)
                        )
                        return True
        return False
