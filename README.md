# Ansible Collection - chameleon.ciab

## Usage:

Place a `clouds.yaml` file from the intended openstakc cloud into your working directory.
then, at the top of that file, add `plugin: chameleon.ciab.chameleon` so that it looks like the following:
```
plugin: chameleon.ciab.chameleon
clouds:
    openstack:
```

Internally, the inventory plugin merely calls `cloud = openstack.connect()`, and as such is compatible with any openstacksdk configurations.


This plugin will return an ansible host for each ironic node registered for the site.
For safety, it is excluding any nodes in an "associated" state.

A future version will make this configurable.


each node will have the following `host_vars` set from the ironic "driver_info":

- "bmc_ip": "ipmi_address"
- "bmc_user": "ipmi_username"
- "bmc_password": "ipmi_password"

The full dict returned from the ironic API is available under the host_var `ironic`, so you can, for example, fetch the ironic uuid via `ironic.id`

## Dependencies:

To use this collection, you will need the following python dependencies in your virtualenv:

```
# Our fork of openstacksdk, which adds support for blazar
git+https://github.com/ChameleonCloud/openstacksdk@chameleoncloud/blazar

# if using the dell idrac related methods, you'll need the following packages
omsdk
pysnmp < 6.0.0
```

## Example usage

An example playbook would look like the following:

```
---
- hosts: all
  connection: local
  gather_facts: false
  collections:
    - "chameleon.ciab"
  roles:
    - chameleon.ciab.update_bios_settings
    - chameleon.ciab.update_firmware
```

And you will want to execute it using the `--limit` keyword, such as:

ansible-playbook -i clouds.yaml  --limit nc27  playbooks/my_node_playbook.yml