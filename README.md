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

## Dependencies:

To use this collection, you will need the following python dependencies in your virtualenv:

```
# Our fork of openstacksdk, which adds support for blazar
git+https://github.com/ChameleonCloud/openstacksdk@chameleoncloud/blazar

# if using the dell idrac related methods, you'll need the following packages
omsdk
pysnmp < 6.0.0
```