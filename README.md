List of installable add-ons for the Mozilla IoT Gateway. These are discoverable from the **Settings** page.

# Building Add-ons

The add-on API is described in [this document](https://github.com/mozilla-iot/wiki/wiki/Adapter-API).

# Packaging Add-ons

Your add-on should be packaged as an npm-compatible package. If it is written in Javascript and is actually npm-compatible, you can simply package it with `npm pack`. If not, the [layout](https://github.com/mozilla-iot/wiki/wiki/Add-On-System-Design#package-layout) needs to be the same.

# Publishing Add-ons to this List

You can submit a [pull request](https://github.com/mozilla-iot/addon-list/pulls) or an [issue](https://github.com/mozilla-iot/addon-list/issues) to this project. You must include the following information:

* `name` - The package name. This should be the same as in your `package.json`.
* `display_name` - A friendly display name for your package. This will be shown in the Gateway's UI.
* `description` - A friendly description for your package. This will be shown in the Gateway's UI.
* `version` - The package version. This should be the same as in your `package.json`.
* `url` - A URL to download the packaged tarball (`.tar.gz` or `.tgz`) from.
