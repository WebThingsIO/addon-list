# Add-on Guidelines

## Add-on Types and Purposes

### Adapter Add-on

An adapter add-on essentially adapts an existing device into a web thing. For
instance, the Zigbee adapter communicates with Zigbee devices via the Zigbee
protocol and represents them as web things with properties, actions, and
events.

This type of add-on can also handle directly connected hardware devices, such
as GPIO pins, as well as cloud services, such as a weather website.

### Notifier Add-on

A notifier add-on allows a user to be notified via some specific mechanism,
e.g. email or SMS. The notifier is used as an output for a rule.

### Extension Add-on

An extension add-on allows a developer to modify the gateway's UI through a set
of predefined extension points.

## Guidelines

There are certain things that add-ons should and should not do. Some things
will prevent the add-on from being accepted into the official add-on list.

### Should Do

#### Data Storage

If the add-on needs to store something persistently, it should only do so in
the gateway's profile directory, i.e. ~/.mozilla-iot. This directory is
guaranteed to persist through system, gateway, and add-on updates.

### Should Not Do

#### Install System Dependencies

Add-ons **MUST NOT** install system-wide dependencies. Doing so affects
everything on the system, so it makes it impossible to guarantee the stability
of the gateway and other add-ons.

#### Use Root Privileges

Add-ons **MUST NOT** use root privileges to do anything on the system. If such
things are required, there may be ways for the gateway to facilitate that in a
safer manner. Likewise, the system image could potentially be modified, if
necessary. Please file issues to the gateway for discussion.

#### Crash on Start-up

Add-ons should not crash when they first start up. Necessary configurations and
such should be properly checked such that exceptions are not thrown, causing
things to crash. This is just good practice.

#### Use IP Address as Part of Device ID

Using an IP address or some other ephemeral data as part of a device's ID can
lead to numerous issues. For instance, if the router assigns a new IP address
to the device, it will no longer be usable via the WebThings UI. Instead,
something more static should be used.
