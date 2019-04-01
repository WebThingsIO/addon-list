List of installable add-ons for the Mozilla WebThings Gateway. These are discoverable from the **Settings** page.

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

Furthermore, your packages may have to be distributed separately if the runtime requires it. For instance, if you're distributing a Node.js package with binaries, it will also need to be compiled for different Node.js versions.

# Publishing Add-ons to this List

You can submit a [pull request](https://github.com/mozilla-iot/addon-list/pulls) or an [issue](https://github.com/mozilla-iot/addon-list/issues) to this project. You must include the following information:

* `name`: The package name. This should be the same as in your `package.json`.
* `display_name`: A friendly display name for your package. This will be shown in the Gateway's UI.
* `description`: A friendly description for your package. This will be shown in the Gateway's UI.
* `author`: Name of the add-on author.
* `homepage`: Homepage of the add-on, i.e. the Github repository.
* `license`: Link to the add-on's license.
* `packages`: An object describing supported architectures and their packages. Each entry should be of the form:

    ```javascript
    {
      "architecture": "my architecture",
      "language": {
        "name": "my language",
        "versions": [
          "any"
        ]
      },
      "url": "https://path.to/my/package.tgz",
      "version": "x.y.z",
      "checksum": "SHA256 of package",
      "api": {
        "min": 1,
        "max": 2
      }
    }
    ```

  * `architecture`: Replace this with the actual architecture (see the previous section).
  * `language`: Description of the language the add-on is written in.
    * `name`: Name of the language. Currently supported:
      * `nodejs`
      * `python`
      * `binary`
    * `versions`: Versions of the language this package will run with.
      * `any`: Any version
      * If using Node.js, you should use the [NODE_MODULE_VERSION](https://nodejs.org/en/download/releases/).
      * If using Python, you can include an array such as `["3.5", "3.6", "3.7"]`.
  * `url`: A URL to download the packaged tarball (`.tar.gz` or `.tgz`) from.
  * `version`: The package version. This should be the same as in your `package.json`.
  * `checksum`: Checksum of the tarball
  * `api`: The API levels supported by this package. This should be the same as in your `package.json`, so an object with the following 2 properties:
    * `min`: The minimum supported API level
    * `max`: The maximum supported API level

## Example Entry

```javascript
{
  "name": "thing-url-adapter",
  "display_name": "Web Thing",
  "description": "Native web thing support",
  "author": "Mozilla IoT",
  "homepage": "https://github.com/mozilla-iot/thing-url-adapter",
  "license": "https://github.com/mozilla-iot/thing-url-adapter/blob/master/LICENSE",
  "packages": [
    {
      "architecture": "linux-arm",
      "language": {
        "name": "nodejs",
        "versions": [
          "57"
        ]
      },
      "version": "0.2.5",
      "url": "https://s3-us-west-2.amazonaws.com/mozilla-gateway-addons/thing-url-adapter-0.2.5-linux-arm-v8.tgz",
      "checksum": "c58eb9c99294a9905fd00b5ca38c73e2337ea54d4db6daebb7c3b0eb64df5b92",
      "api": {
        "min": 2,
        "max": 2
      }
    },
    {
      "architecture": "linux-x64",
      "language": {
        "name": "nodejs",
        "versions": [
          "57"
        ]
      },
      "version": "0.2.5",
      "url": "https://s3-us-west-2.amazonaws.com/mozilla-gateway-addons/thing-url-adapter-0.2.5-linux-x64-v8.tgz",
      "checksum": "2e778ad976cb469be1d41af13716a7d65a9cc4e371c452be2ff2da4ed932941c",
      "api": {
        "min": 2,
        "max": 2
      }
    },
    {
      "architecture": "darwin-x64",
      "language": {
        "name": "nodejs",
        "versions": [
          "57"
        ]
      },
      "version": "0.2.5",
      "url": "https://s3-us-west-2.amazonaws.com/mozilla-gateway-addons/thing-url-adapter-0.2.5-darwin-x64-v8.tgz",
      "checksum": "e287c61d844fe832b9dca609546ec2454fe23e4a7753b3ce6f9ee53332fdf53f",
      "api": {
        "min": 2,
        "max": 2
      }
    }
  ]
}
```
