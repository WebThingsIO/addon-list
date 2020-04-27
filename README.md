List of installable add-ons for the Mozilla WebThings Gateway. These are
discoverable from the **Settings -> Add-ons** page.

# Building Add-ons

See [here](https://github.com/mozilla-iot/wiki/wiki#general-1) for lots of
resources.

# Packaging Add-ons

Your add-on should be packaged according to [this document][manifest].

## Packages with Binaries

If your package contains any binaries, i.e. executables, shared libraries,
etc., you must cross-compile for any architecture(s) you want to support and
distribute a package for each. The currently supported architectures are:

* `any`: Use this if your package does not contain binaries, i.e. if it's pure
  Javascript/Python.
* `darwin-x64`: 64-bit Mac OS X
* `linux-arm`: Linux on 32-bit ARM (this should be built to support armv6, such
  as older Raspberry Pi generations)
* `linux-arm64`: Linux on 64-bit ARM
* `linux-ia32`: Linux on 32-bit x86
* `linux-x64`: Linux on 64-bit x86

Furthermore, your packages may have to be distributed separately if the runtime
requires it. For instance, if you're distributing a Node.js package with
binaries, it will also need to be compiled for different Node.js versions.

# Publishing Add-ons to this List

You can submit a [pull request][PR] or an [issue][issue] to this project. You
must include the following information:

* `id`: The package ID. This should be the same as in your `manifest.json`.
* `name`: A friendly display name for your package. This will be shown in the
  Gateway's UI. This should be the same as in your `manifest.json`.
* `description`: A friendly description for your package. This will be shown in
  the Gateway's UI.
* `author`: Name of the add-on author.
* `homepage_url`: URL which points to the homepage of the add-on, i.e. the
  GitHub repository. This should be the same as in your `manifest.json`.
* `license_url`: URL which points to the add-on's license.
* `primary_type`: Primary type of this add-on. This should be the same as in
  your `manifest.json`. Should be one of: adapter, notifier, extension
* `packages`: An object describing supported architectures and their packages.
  Each entry should be of the form:

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
        "min": 2,
        "max": 2
      },
      "gateway": {
        "min": "0.10.0",
        "max": "*"
      }
    }
    ```

  * `architecture`: Replace this with the actual architecture (see the previous
    section).
  * `language`: Description of the language the add-on is written in.
    * `name`: Name of the language. Currently supported:
      * `nodejs`
      * `python`
      * `binary`
      * `none` - used only in the case of pure UI extensions
    * `versions`: Versions of the language this package will run with.
      * `any`: Any version
      * If using Node.js, you should use the
        [NODE_MODULE_VERSION][node-versions].
      * If using Python, you can include an array such as
        `["3.5", "3.6", "3.7"]`.
      * If `name` is `none`, `versions` can be omitted.
  * `url`: A URL to download the packaged tarball (`.tar.gz` or `.tgz`) from.
  * `version`: The package version. This should be the same as in your
    `manifest.json`.
  * `checksum`: Checksum of the tarball
  * `api`: The API levels supported by this package. This is only necessary if
    your add-on supports gateway versions <= 0.9.X. This should be the same as
    in your `package.json`, so an object with the following 2 properties:
    * `min`: The minimum supported API level
    * `max`: The maximum supported API level
  * `gateway`: The gateway versions supported by this package.
    * `min`: The minimum supported gateway version. This should correspond to
      the `strict_min_version` in your `manifest.json`.
    * `max`: The maximum supported gateway version. This should correspond to
      the `strict_max_version` in your `manifest.json`.

## Example Entry

```javascript
{
  "id": "thing-url-adapter",
  "name": "Web Thing",
  "description": "Native web thing support",
  "author": "Mozilla IoT",
  "homepage_url": "https://github.com/mozilla-iot/thing-url-adapter",
  "license_url": "https://github.com/mozilla-iot/thing-url-adapter/blob/master/LICENSE",
  "primary_type": "adapter",
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
      },
      "gateway": {
        "min": "0.10.0",
        "max": "*"
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
      },
      "gateway": {
        "min": "0.10.0",
        "max": "*"
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
      },
      "gateway": {
        "min": "0.10.0",
        "max": "*"
      }
    }
  ]
}
```

[adapter-api]: https://github.com/mozilla-iot/wiki/wiki/Adapter-API
[guidelines]: https://github.com/mozilla-iot/addon-list/blob/master/guidelines.md
[manifest]: https://github.com/mozilla-iot/addon-list/blob/master/manifest.md
[PR]: https://github.com/mozilla-iot/addon-list/pulls
[issue]: https://github.com/mozilla-iot/addon-list/issues
[node-versions]: https://nodejs.org/en/download/releases/
