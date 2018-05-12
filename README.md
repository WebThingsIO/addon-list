List of installable add-ons for the Mozilla IoT Gateway. These are discoverable from the **Settings** page.

# Building Add-ons

The add-on API is described in [this document](https://github.com/mozilla-iot/wiki/wiki/Adapter-API).

# Packaging Add-ons

Your add-on should be packaged as an npm-compatible package. If it is written in Javascript and is actually npm-compatible, you can simply package it with `npm pack`. If not, the [layout](https://github.com/mozilla-iot/wiki/wiki/Add-On-System-Design#package-layout) needs to be the same.

The add-on package should also include a `SHA256SUMS` file, containing checksums of all included files (other than itself), and it should bundle all required dependencies other than `gateway-addon`, i.e. your entire `node_modules` directory. This applies to add-ons written in other languages, as well.

## Packages with Binaries

If your package contains any binaries, i.e. executables, shared libraries, etc., you must cross-compile for any architecture(s) you want to support and distribute a package for each. The currently supported architectures are:

* `any`: Use this if your package does not contain binaries, i.e. if it's pure Javascript/Python.
* `darwin-x64`: 64-bit Mac OS X
* `linux-arm`: Linux on 32-bit ARM (this should be built to support armv6, such as older Raspberry Pi generations)
* `linux-arm64`: Linux on 64-bit ARM
* `linux-ia32`: Linux on 32-bit x86
* `linux-x64`: Linux on 64-bit x86
* `win32-ia32`: Windows on 32-bit x86
* `win32-x64`: Windows on 64-bit x86

# Publishing Add-ons to this List

You can submit a [pull request](https://github.com/mozilla-iot/addon-list/pulls) or an [issue](https://github.com/mozilla-iot/addon-list/issues) to this project. You must include the following information:

* `name`: The package name. This should be the same as in your `package.json`.
* `display_name`: A friendly display name for your package. This will be shown in the Gateway's UI.
* `description`: A friendly description for your package. This will be shown in the Gateway's UI.
* `author`: Name of the add-on author.
* `homepage`: Homepage of the add-on, i.e. the Github repository.
* `packages`: An object describing supported architectures and their packages. Each entry should be of the form:

    ```javascript
    "architecture": {
      "url": "https://path.to/my/package.tgz",
      "version": "x.y.z",
      "checksum": "sha256 of package"
    }
    ```

  * `architecture`: Replace this with the actual architecture (see the previous section).
  * `url`: A URL to download the packaged tarball (`.tar.gz` or `.tgz`) from.
  * `version`: The package version. This should be the same as in your `package.json`.
  * `checksum`: Checksum of the tarball
* `api`: The API levels supported by this add-on. This should be the same as in your `package.json`, so an object with the following 2 properties:
    * `min`: The minimum supported API level
    * `max`: The maximum supported API level
