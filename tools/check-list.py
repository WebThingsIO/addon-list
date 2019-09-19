#!/usr/bin/env python3

import glob
import hashlib
import json
import jsonschema
import os
import re
import shutil
import sys
import tarfile
import time
import urllib.error
import urllib.request

_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
_LIST_SCHEMA = os.path.join(_ROOT, 'schema', 'list.json')
_PACKAGE_SCHEMA = os.path.join(_ROOT, 'schema', 'package.json')
_MANIFEST_SCHEMA = os.path.join(_ROOT, 'schema', 'manifest.json')
_ADDONS_DIR = os.path.join(_ROOT, 'addons')

MAX_DOWNLOAD_ATTEMPTS = 5
DOWNLOAD_ATTEMPT_DELAY = 3  # seconds


def cleanup(exit=True):
    if os.path.exists('package.tgz'):
        os.unlink('package.tgz')

    if os.path.exists('package'):
        shutil.rmtree('package')

    if exit:
        sys.exit(1)


def hash_file(fname):
    hasher = hashlib.sha256()
    try:
        with open(fname, 'rb') as f:
            while True:
                buf = f.read(4096)
                if len(buf) == 0:
                    break

                hasher.update(buf)

        return hasher.hexdigest()
    except (IOError, OSError):
        return None


def verify_package_json(package_json, list_entry, package):
    _id = list_entry['id']

    if 'enabled' in package_json['moziot'] and \
            package_json['moziot']['enabled'] and \
            list_entry['author'].lower() != 'mozilla iot':
        print('Add-on is enabled by default: {}'.format(_id))
        cleanup()

    # Verify the files list.
    for fname in package_json['files']:
        if not os.path.exists(os.path.join('package', fname)):
            print('File missing for package "{}": {}'.format(_id, fname))
            cleanup()

    # Verify SHA256SUMS.
    if 'SHA256SUMS' in package_json['files']:
        try:
            with open('./package/SHA256SUMS', 'rt') as f:
                for line in f:
                    cksum, fname = re.split(r'\s+', line.strip(), maxsplit=1)
                    fname = os.path.join('package', fname)
                    if cksum != hash_file(fname):
                        print('Checksum failed in package "{}": {}'
                              .format(_id, fname))
                        cleanup()
        except (IOError, OSError, ValueError):
            print('Failed to read SHA256SUMS file for package "{}"'
                  .format(_id))
            cleanup()
    else:
        print('SHA256SUMS file is missing from package "{}"'.format(_id))
        cleanup()

    # Verify that the ID matches
    if package_json['name'] != _id:
        print('ID mismatch for package "{}"'
              'name from package.json "{}" doesn\'t match '
              'id from list.json'
              .format(_id, package_json['name']))
        cleanup()

    # Verify that the version matches
    if package_json['version'] != package['version']:
        print('Version mismatch for package "{}": '
              'version from package.json "{}" doesn\'t match '
              'version from list.json "{}"'
              .format(_id, package_json['version'], package['version']))
        cleanup()

    # Verify that the author matches
    if type(package_json['author']) is dict and \
            package_json['author']['name'] != list_entry['author']:
        print('Author mismatch for package "{}": '
              'author from package.json "{}" doesn\'t match '
              'author from list.json "{}"'
              .format(_id, package_json['author']['name'],
                      list_entry['author']))
        cleanup()
    elif package_json['author'].split('<')[0].strip() != list_entry['author']:
        print('Author mismatch for package "{}": '
              'author from package.json "{}" doesn\'t match '
              'author from list.json "{}"'
              .format(_id, package_json['author'], list_entry['author']))
        cleanup()

    # Verify that the display name matches
    if package_json['display_name'] != list_entry['name']:
        print('Name mismatch for package "{}": '
              'display_name from package.json "{}" doesn\'t '
              'match name from list.json "{}"'
              .format(_id, package_json['display_name'],
                      list_entry['name']))
        cleanup()

    # Verify that the homepage matches
    if package_json['homepage'] != list_entry['homepage_url']:
        print('Homepage mismatch for package "{}": '
              'homepage from package.json "{}" doesn\'t match '
              'homepage_url from list.json "{}"'
              .format(_id, package_json['homepage'],
                      list_entry['homepage_url']))
        cleanup()

    # Verify that the type matches
    t = 'adapter'
    if 'type' in package_json['moziot']:
        t = package_json['moziot']['type']

    if t != list_entry['primary_type']:
        print('type mismatch for package "{}": '
              'type from package.json "{}" doesn\'t match primary_type '
              'from list.json "{}"'
              .format(_id, t, list_entry['primary_type']))
        cleanup()

    # Verify that the API version matches
    if package_json['moziot']['api']['min'] != package['api']['min']:
        print('api.min Version mismatch for package "{}": '
              'api.min version from package.json "{}" doesn\'t '
              'match api.min version from list.json "{}"'
              .format(_id, package_json['moziot']['api']['min'],
                      package['api']['min']))
        cleanup()

    if package_json['moziot']['api']['max'] != package['api']['max']:
        print('api.max version mismatch for package "{}": '
              'api.max version from package.json "{}" doesn\'t '
              'match api.max version from list.json "{}"'
              .format(_id, package_json['moziot']['api']['max'],
                      package['api']['max']))
        cleanup()

    # Validate the config schema, if present
    if 'schema' in package_json['moziot']:
        try:
            jsonschema.Draft7Validator.check_schema(
                package_json['moziot']['schema'])
        except jsonschema.SchemaError as e:
            print('Invalid config schema for {}: {}'
                  .format(_id, e))
            cleanup()


def verify_manifest_json(manifest_json, list_entry, package):
    _id = list_entry['id']
    webthings = manifest_json['gateway_specific_settings']['webthings']

    if 'enabled' in webthings and \
            webthings['enabled'] and \
            list_entry['author'].lower() != 'mozilla iot':
        print('Add-on is enabled by default: {}'.format(_id))
        cleanup()

    # Verify that SHA256SUMS exists and that every listed file exists
    if not os.path.exists('./package/SHA256SUMS'):
        print('SHA256SUMS file is missing from package "{}"'.format(_id))
        cleanup()

    sums_file = os.path.realpath('./package/SHA256SUMS')
    sums = {}
    try:
        with open(sums_file, 'rt') as f:
            for line in f:
                cksum, fname = re.split(r'\s+', line.strip(), maxsplit=1)
                fname = os.path.realpath(os.path.join('package', fname))

                if not os.path.exists(fname):
                    print('File "{}" missing for add-on "{}"'
                          .format(fname, _id))
                    cleanup()

                sums[fname] = cksum
    except (IOError, OSError, ValueError):
        print('Failed to read SHA256SUMS file for package "{}"'.format(_id))
        cleanup()

    # Verify that every file has a checksum, and verify the checksum
    files = []
    for (dpath, _, fnames) in os.walk('package'):
        files.extend(
            [os.path.realpath(os.path.join(dpath, fname)) for fname in fnames]
        )

    for fname in files:
        if fname == sums_file:
            continue

        if fname not in sums:
            print('Checksum missing for file "{}" in package "{}"'
                  .format(fname, _id))
            cleanup()

        if sums[fname] != hash_file(fname):
            print('Checksum failed in package "{}": {}'.format(_id, fname))
            cleanup()

    # Verify that the ID matches
    if manifest_json['id'] != _id:
        print('ID mismatch for package "{}"'
              'ID from manifest.json "{}" doesn\'t match '
              'ID from list.json'
              .format(_id, manifest_json['id']))
        cleanup()

    # Verify that the version matches
    if manifest_json['version'] != package['version']:
        print('Version mismatch for package "{}": '
              'version from manifest.json "{}" doesn\'t match '
              'version from list.json "{}"'
              .format(_id, manifest_json['version'], package['version']))
        cleanup()

    # Verify that the author matches
    if manifest_json['author'].split('<')[0].strip() != list_entry['author']:
        print('Author mismatch for package "{}": '
              'author from manifest.json "{}" doesn\'t match '
              'author from list.json "{}"'
              .format(_id, manifest_json['author'], list_entry['author']))
        cleanup()

    # Verify that the name matches
    if manifest_json['name'] != list_entry['name']:
        print('Name mismatch for package "{}": '
              'name from manifest.json "{}" doesn\'t '
              'match name from list.json "{}"'
              .format(_id, manifest_json['name'], list_entry['name']))
        cleanup()

    # Verify that the homepage matches
    if manifest_json['homepage_url'] != list_entry['homepage_url']:
        print('Homepage mismatch for package "{}": '
              'homepage_url from manifest.json "{}" doesn\'t match '
              'homepage_url from list.json "{}"'
              .format(_id, manifest_json['homepage_url'],
                      list_entry['homepage_url']))
        cleanup()

    # Verify that the type matches
    t = webthings['primary_type']
    if t != list_entry['primary_type']:
        print('type mismatch for package "{}": '
              'primary_type from manifest.json "{}" doesn\'t match '
              'primary_type from list.json "{}"'
              .format(_id, t, list_entry['primary_type']))
        cleanup()

    # Verify that exec is present if primary_type is not extension
    if ('exec' not in webthings or not webthings['exec']) and t != 'extension':
        print('exec missing for package "{}"'.format(_id))
        cleanup()

    # Verify min gateway version matches
    gw_min = '0.10.0'
    if 'strict_min_version' in webthings:
        gw_min = webthings['strict_min_version']

    if package['gateway']['min'] != gw_min:
        print('Minimum gateway version mismatch for package "{}": '
              'strict_min_version from manifest.json "{}" doesn\'t match '
              'min from list.json "{}"'
              .format(_id, gw_min, package['gateway']['min']))
        cleanup()

    # Verify max gateway version matches
    gw_max = '*'
    if 'strict_max_version' in webthings:
        gw_max = webthings['strict_max_version']

    if package['gateway']['max'] != gw_max:
        print('Maximum gateway version mismatch for package "{}": '
              'strict_max_version from manifest.json "{}" doesn\'t match '
              'max from list.json "{}"'
              .format(_id, gw_max, package['gateway']['max']))
        cleanup()

    # Validate the config schema, if present
    if 'options' in manifest_json and 'schema' in manifest_json['options']:
        try:
            jsonschema.Draft7Validator.check_schema(
                manifest_json['options']['schema'])
        except jsonschema.SchemaError as e:
            print('Invalid config schema for {}: {}'.format(_id, e))
            cleanup()

    # Verify that the default locale actually exists
    if 'default_locale' in manifest_json:
        dname = os.path.join(
            '.',
            'package',
            '_locales',
            manifest_json['default_locale']
        )

        if not os.path.exists(dname):
            print('Default locale "{}" does not exist in package "{}"'
                  .format(manifest_json['default_locale'], _id))
            cleanup()


def main():
    adapters = []
    if len(sys.argv) > 1:
        adapters = sys.argv[1:]

    # Load the schema.
    with open(_LIST_SCHEMA) as f:
        list_schema = json.load(f)

    with open(_PACKAGE_SCHEMA) as f:
        package_schema = json.load(f)

    with open(_MANIFEST_SCHEMA) as f:
        manifest_schema = json.load(f)

    try:
        jsonschema.Draft7Validator.check_schema(list_schema)
        jsonschema.Draft7Validator.check_schema(package_schema)
        jsonschema.Draft7Validator.check_schema(manifest_schema)
    except jsonschema.SchemaError as e:
        print('Schema validation failed: {}'.format(e))
        cleanup()

    addon_list = []

    # Make sure the file is valid JSON
    if len(adapters) > 0:
        for adapter in adapters:
            fname = os.path.join(_ADDONS_DIR, '{}.json'.format(adapter))
            try:
                with open(fname, 'rt') as f:
                    entry = json.load(f)
                    if entry['id'] != adapter:
                        print('Filename {} does not match adapter ID {}'
                              .format(adapter, entry['id']))
                        cleanup()

                    addon_list.append(entry)
            except (IOError, OSError, ValueError) as e:
                print('Failed to read {}: {}'.format(fname, e))
                cleanup()
    else:
        for path in sorted(glob.glob(os.path.join(_ADDONS_DIR, '*.json'))):
            try:
                with open(path, 'rt') as f:
                    entry = json.load(f)
                    adapter = os.path.splitext(os.path.basename(path))[0]

                    if entry['id'] != adapter:
                        print('Filename {} does not match adapter ID {}'
                              .format(adapter, entry['id']))
                        cleanup()

                    addon_list.append(entry)
            except (IOError, OSError, ValueError) as e:
                print('Failed to read {}: {}'.format(path, e))
                cleanup()

    for entry in addon_list:
        jsonschema.validate(entry, list_schema)

        _id = entry['id']

        print('Checking {} ...'.format(_id))

        # Download the packages.
        for package in entry['packages']:
            url = package['url']
            checksum = package['checksum']

            for attempt in range(MAX_DOWNLOAD_ATTEMPTS):
                try:
                    urllib.request.urlretrieve(url, 'package.tgz')
                    break
                except urllib.error.URLError:
                    print('Failed to download package for "{}": {}'
                          .format(_id, package['architecture']))
                    if (attempt + 1 >= MAX_DOWNLOAD_ATTEMPTS):
                        print('  aborting')
                        cleanup()
                    else:
                        print('  sleeping and retrying...')
                        time.sleep(DOWNLOAD_ATTEMPT_DELAY)

            # Verify the checksum.
            if checksum != hash_file('./package.tgz'):
                print('Checksum invalid for "{}": {}'
                      .format(_id, package['architecture']))
                cleanup()

            # Check the package contents.
            try:
                with tarfile.open('./package.tgz', 'r:gz') as t:
                    t.extractall()
            except (IOError, OSError, tarfile.TarError):
                print('Failed to untar package for "{}": {}'
                      .format(_id, package['architecture']))
                cleanup()

            manifest_json = None
            if os.path.exists('./package/manifest.json'):
                try:
                    with open('./package/manifest.json', 'rt') as f:
                        manifest_json = json.load(f)
                except (IOError, OSError, ValueError):
                    print('Failed to read manifest.json for "{}"'.format(_id))
                    cleanup()
            else:
                print('manifest.json is missing for "{}"'.format(_id))
                # TODO: enforce this once all add-ons have transitioned
                # cleanup()

            package_json = None
            try:
                with open('./package/package.json', 'rt') as f:
                    package_json = json.load(f)
            except (IOError, OSError, ValueError):
                # Only allow package.json to be missing if this is an extension
                # add-on, which is inherently only supported by Gateway 0.10+
                if manifest_json is None or \
                        manifest_json['gateway_specific_settings']['webthings']['primary_type'] != 'extension':  # noqa
                    print('Failed to read package.json for "{}"'.format(_id))
                    cleanup()

            licenses = glob.glob('./package/LICENSE*')
            if len(licenses) == 0:
                print('LICENSE not included in package "{}"'.format(_id))
                cleanup()

            # Verify required fields in package.json.
            if package_json is not None:
                jsonschema.validate(package_json, package_schema)
                verify_package_json(package_json, entry, package)

            # Verify required fields in manifest.json.
            if manifest_json is not None:
                jsonschema.validate(manifest_json, manifest_schema)
                verify_manifest_json(manifest_json, entry, package)

            cleanup(exit=False)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
