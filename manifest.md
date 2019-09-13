# Add-on Manifest

Add-ons must contain a `manifest.json` file. The format is based on the
WebExtension `manifest.json` [specification][manifest.json].

## Add-on Packaging

The add-on should be packaged in a gzip-compressed tarball, and shall contain
the following files and directories:
* `package/` - top-level directory, everything else must be contained within
  * `manifest.json` - as specified below
  * `SHA256SUMS` - file containing SHA-256 checksums of every file in the
    package, excluding itself. This must be compatible with the `sha256sum`
    application from GNU's coreutils.
  * `_locales/` - (Optional) localization files. See specification
    [here][locales].
  * Any other code, dependencies, and assets required for your add-on to run.
    The only exception to this is that the `gateway-addon` Python and Node.js
    libraries will be provided on the system, so you _should not_ include them
    in your add-on.
  * If the add-on contains binary, platform-specific executables or libraries,
    a separate package must be generated for each supported platform.

## Supported Keys in manifest.json

| Key | Mandatory | Description | Specification | Notes | Gateway Support |
| --- | --------- | ----------- | ------------- | ----- | --------------- |
| `author` | Yes | The add-on's author, intended for display in the browser's user interface. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/author | We previously supported the extended author field from [package.json][author]. That will no longer be the case. | 0.10.0 |
| `content_scripts` | No | Instructs the browser to load content scripts into web pages whose URL matches a given pattern. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/content_scripts | Right now, only the "js" and "css" keys will be used. They will be injected into the UI at load time. | 0.10.0 |
| `default_locale` | Contingent | This key must be present if the add-on contains the `_locales` directory, and must be absent otherwise. It identifies a subdirectory of `_locales`, and this subdirectory will be used to find the default strings for your add-on. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/default_locale | | |
| `description` | Yes | A short description of the add-on, intended for display in the browser's user interface. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/description | | 0.10.0 |
| `gateway_specific_settings` | Yes | The `gateway_specific_settings` object contains keys that are specific to a particular gateway implementation. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/browser_specific_settings | Based on [`browser_specific_settings`][browser_specific_settings]. | 0.10.0 |
| <pre>  .webthings</pre> | Yes | WebThings Gateway settings | | | 0.10.0 |
| <pre>    .exec</pre> | Yes | The execution command. This command may include:<ul><li>`{nodeLoader}`, which will be replaced with Node.js add-on loader command.</li><li>`{path}`, which will be replaced with the path of your add-on's directory.</li><li>`{name}`, which will be replaced with the id value.</li></ul> | | This replaces `moziot.exec`. | 0.10.0 |
| <pre>    .primary_type</pre> | Yes | Primary add-on type. While an add-on may implement multiple types, such as and adapter and a notifier, this key specifies which of those is the primary functionality. | | This replaces `moziot.type`. Must be one of: `adapter`, `notifier`, `extension`, `service` | 0.10.0 |
| <pre>    .strict_min_version</pre> | No | Minimum WebThings Gateway version to support. If the WebThings Gateway version on which the add-on is being installed or run is below this version, then the add-on will be disabled, or not permitted to be installed. | | This replaces `moziot.api.min`. Defaults to "0.10.0". | 0.10.0 |
| <pre>    .strict_max_version</pre> | No | Maximum WebThings Gateway version to support. If the WebThings Gateway version on which the add-on is being installed or run is above this version, then the add-on will be disabled, or not permitted to be installed. | | This replaces `moziot.api.max`. Defaults to "\*", which disables checking for a maximum version. | 0.10.0 |
| `homepage_url` | Yes | URL for the add-on's homepage. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/homepage_url | This replaces `homepage`. | 0.10.0 |
| `id` | Yes | ID of the add-on. Must be unique. | | This replaces `name`. | 0.10.0 |
| `license` | Yes | SPDX license identifier that governs this add-on. | https://spdx.org/licenses/ | | 0.10.0 |
| `manifest_version` | Yes | This key specifies the version of manifest.json used by this add-on. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/manifest_version | Currently, this must always be 1. | 0.10.0 |
| `name` | Yes | Name of the add-on. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/name | This replaces `display_name`. | 0.10.0 |
| `optional_permissions` | No | Use the `optional_permissions` key to list permissions that you want to ask for at runtime, after your add-on has been installed. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/optional_permissions | The permission keywords from the specification do not apply to gateway add-ons, but the format of the key and value do. | |
| `options` | No | A set of options that define how the add-on should operate. | | | 0.10.0 |
| <pre>  .default</pre> | No | An object containing a set of default options. | | This replaces `moziot.config`. | 0.10.0 |
| <pre>  .schema</pre> | No | An object containing a validation schema to validate user-provided options. This must conform to the JSON Schema Validation specification. | https://json-schema.org/latest/json-schema-validation.html | This replaces `moziot.schema`. | 0.10.0 |
| `options_ui` | No | Defines an options page for the add-on. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/options_ui | If this key is used, options.defaults will still be used, but options.schema will be ignored in favor of the options page doing the validation. | |
| `permissions` | No | This key is an array of strings, and each string is a request for a permission. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/permissions | The permission keywords from the specification do not apply to gateway add-ons, but the format of the key and value do. | |
| `short_name` | No | Short name for the add-on. If given, this will be used in contexts where the name field is too long. It's recommended that the short name should not exceed 12 characters. If the short name field is not included in manifest.json, then name will be used instead and may be truncated. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/short_name | | 0.10.0 |
| `version` | Yes | Version of the add-on, formatted as numbers and ASCII characters separated by dots. Add-ons must use [semantic versioning][semver]. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/version | | 0.10.0 |
| `web_accessible_resources` | No | List of add-on resources (scripts, images, etc.) which should be accessible via the UI. | https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/web_accessible_resources | | 0.10.0 |

## Converting Existing Add-ons

A convenience script is available [here][script] to make the transition from
`package.json` to `manifest.json` easy.

## Examples

### Adapter

```json
{
  "author": "Mozilla IoT",
  "description": "HomeKit device adapter.",
  "gateway_specific_settings": {
    "webthings": {
      "strict_min_version": "0.10.0",
      "primary_type": "adapter",
      "exec": "{nodeLoader} {path}"
    }
  },
  "homepage_url": "https://github.com/mozilla-iot/homekit-adapter",
  "id": "homekit-adapter",
  "license": "MPL-2.0",
  "manifest_version": 1,
  "name": "HomeKit",
  "options": {
    "default": {
      "enableBluetooth": true
    },
    "schema": {
      "type": "object",
      "required": [
        "enableBluetooth"
      ],
      "properties": {
        "enableBluetooth": {
          "type": "boolean",
          "description": "Whether or not to enable Bluetooth device support."
        }
      }
    }
  },
  "version": "0.4.1"
}
```

### Notifier

```json
{
  "author": "Mozilla IoT",
  "description": "Send notifications through Pushover.",
  "gateway_specific_settings": {
    "webthings": {
      "strict_min_version": "0.10.0",
      "primary_type": "notifier",
      "exec": "{nodeLoader} {path}"
    }
  },
  "homepage_url": "https://github.com/mozilla-iot/pushover-notifier",
  "id": "pushover-notifier",
  "license": "MPL-2.0",
  "manifest_version": 1,
  "name": "Pushover Notifier",
  "options": {
    "default": {
      "userKey": "",
      "token": ""
    },
    "schema": {
      "type": "object",
      "required": [
        "userKey",
        "token"
      ],
      "properties": {
        "userKey": {
          "description": "Your user key",
          "type": "string"
        },
        "token": {
          "description": "Your app token",
          "type": "string"
        }
      }
    }
  },
  "version": "0.0.1"
}
```

### Extension

TODO

### Service

TODO

[manifest.json]: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json
[locales]: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Internationalization
[author]: https://docs.npmjs.com/files/package.json#people-fields-author-contributors
[browser_specific_settings]: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/browser_specific_settings
[semver]: https://semver.org/
[script]: https://github.com/mozilla-iot/addon-list/blob/master/tools/package-to-manifest.py
