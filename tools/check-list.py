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
_SCHEMA = os.path.join(_ROOT, 'schema.json')
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


def verify_fields(fields, obj):
    for field in fields:
        if '.' in field:
            _fields = field.split('.')
        else:
            _fields = [field]

        e = obj
        for f in _fields:
            if f not in e:
                return False, field

            e = e[f]

    return True, None


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


def main():
    adapters = []
    if len(sys.argv) > 1:
        adapters = sys.argv[1:]

    # Load the schema.
    with open(_SCHEMA) as f:
        schema = json.load(f)

    try:
        jsonschema.Draft4Validator.check_schema(schema)
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
                    if entry['name'] != adapter:
                        print('Filename {} does not match adapter name {}'
                              .format(adapter, entry['name']))
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

                    if entry['name'] != adapter:
                        print('Filename {} does not match adapter name {}'
                              .format(adapter, entry['name']))
                        cleanup()

                    addon_list.append(entry)
            except (IOError, OSError, ValueError) as e:
                print('Failed to read {}: {}'.format(path, e))
                cleanup()

    required_in_manifest = [
        'name',
        'version',
        'author',
        'display_name',
        'homepage',
        'files',
        'moziot.api.min',
        'moziot.api.max',
    ]

    for entry in addon_list:
        jsonschema.validate(entry, schema)

        name = entry['name']

        print('Checking {} ...'.format(name))

        # Download the packages.
        for package in entry['packages']:
            version = package['version']
            url = package['url']
            checksum = package['checksum']

            for attempt in range(MAX_DOWNLOAD_ATTEMPTS):
                try:
                    urllib.request.urlretrieve(url, 'package.tgz')
                    break
                except urllib.error.URLError:
                    print('Failed to download package for "{}": {}'
                          .format(name, package['architecture']))
                    if (attempt + 1 >= MAX_DOWNLOAD_ATTEMPTS):
                        print('  aborting')
                        cleanup()
                    else:
                        print('  sleeping and retrying...')
                        time.sleep(DOWNLOAD_ATTEMPT_DELAY)

            # Verify the checksum.
            if checksum != hash_file('./package.tgz'):
                print('Checksum invalid for "{}": {}'
                      .format(name, package['architecture']))
                cleanup()

            # Check the package contents.
            try:
                with tarfile.open('./package.tgz', 'r:gz') as t:
                    t.extractall()
            except (IOError, OSError, tarfile.TarError):
                print('Failed to untar package for "{}": {}'
                      .format(name, package['architecture']))
                cleanup()

            try:
                with open('./package/package.json', 'rt') as f:
                    manifest = json.load(f)
            except (IOError, OSError, ValueError):
                print('Failed to read package.json for "{}"'.format(name))
                cleanup()

            licenses = glob.glob('./package/LICENSE*')
            if len(licenses) == 0:
                print('LICENSE not included in package "{}"'.format(name))
                cleanup()

            # Verify required fields in package.json.
            success, field = verify_fields(required_in_manifest, manifest)

            if not success:
                print('Field "{}" missing from:\n{}'
                      .format(field, json.dumps(manifest, indent=2)))
                cleanup()

            if 'enabled' in manifest['moziot'] and \
                    manifest['moziot']['enabled'] and \
                    entry['author'].lower() != 'mozilla iot':
                print('Add-on is enabled by default: {}'.format(name))
                # TODO: enforce once broadlink and nanoleaf are updated
                # cleanup()

            # Verify some additional fields.
            if not isinstance(manifest['files'], list) or \
                    len(manifest['files']) == 0:
                print('Invalid files array:\n{}'
                      .format(json.dumps(manifest, indent=2)))
                cleanup()

            # Verify the files list.
            for fname in manifest['files']:
                if not os.path.exists(os.path.join('package', fname)):
                    print('File missing for package "{}": {}'
                          .format(name, fname))
                    cleanup()

            # Verify SHA256SUMS, if present.
            if 'SHA256SUMS' in manifest['files']:
                try:
                    with open('./package/SHA256SUMS', 'rt') as f:
                        for line in f:
                            cksum, fname = \
                                re.split(r'\s+', line.strip(), maxsplit=1)
                            fname = os.path.join('package', fname)
                            if cksum != hash_file(fname):
                                print('Checksum failed in package "{}": {}'
                                      .format(name, fname))
                                cleanup()
                except (IOError, OSError, ValueError):
                    print('Failed to read SHA256SUMS file for package "{}"'
                          .format(name))
                    cleanup()

            # Verify that the name matches
            if manifest['name'] != name:
                print('Name mismatch for package "{}"'
                      'name from package.json "{}" doesn\'t match '
                      'name from list.json'
                      .format(name, manifest['name']))
                cleanup()

            # Verify that the version matches
            if manifest['version'] != version:
                print('Version mismatch for package "{}": '
                      'version from package.json "{}" doesn\'t match '
                      'version from list.json "{}"'
                      .format(name, manifest['version'], version))
                cleanup()

            # Verify that the author matches
            if 'author' not in manifest:
                print('Author missing for package "{}"'.format(name))
            elif type(manifest['author']) is dict and \
                    manifest['author']['name'] != entry['author']:
                print('Author mismatch for package "{}": '
                      'author from package.json "{}" doesn\'t match '
                      'author from list.json "{}"'
                      .format(name, manifest['author']['name'],
                              entry['author']))
                cleanup()
            elif manifest['author'].split('<')[0].strip() != entry['author']:
                print('Author mismatch for package "{}": '
                      'author from package.json "{}" doesn\'t match '
                      'author from list.json "{}"'
                      .format(name, manifest['author'], entry['author']))
                cleanup()

            # Verify that the display name matches
            if 'display_name' not in manifest:
                print('Display name missing for package "{}"'
                      .format(name))
            elif manifest['display_name'] != entry['display_name']:
                print('Display name mismatch for package "{}": '
                      'display_name from package.json "{}" doesn\'t '
                      'match display_name from list.json "{}"'
                      .format(name, manifest['display_name'],
                              entry['display_name']))
                cleanup()

            # Verify that the homepage matches
            if manifest['homepage'] != entry['homepage']:
                print('Homepage mismatch for package "{}": '
                      'homepage from package.json "{}" doesn\'t match '
                      'homepage from list.json "{}"'
                      .format(name, manifest['homepage'],
                              entry['homepage']))
                cleanup()

            # Verify that the type matches
            t = 'adapter'
            if 'type' in manifest['moziot']:
                t = manifest['moziot']['type']

            if t != entry['type']:
                print('type mismatch for package "{}": '
                      'type from package.json "{}" doesn\'t match type '
                      'from list.json "{}"'
                      .format(name, t, entry['type']))
                cleanup()

            # Verify that the API version matches
            if manifest['moziot']['api']['min'] != package['api']['min']:
                print('api.min Version mismatch for package "{}": '
                      'api.min version from package.json "{}" doesn\'t '
                      'match api.min version from list.json "{}"'
                      .format(name, manifest['moziot']['api']['min'],
                              package['api']['min']))
                cleanup()

            if manifest['moziot']['api']['max'] != package['api']['max']:
                print('api.max version mismatch for package "{}": '
                      'api.max version from package.json "{}" doesn\'t '
                      'match api.max version from list.json "{}"'
                      .format(name, manifest['moziot']['api']['max'],
                              package['api']['max']))
                cleanup()

            # Verify the plugin flag.
            if not manifest['moziot']['plugin']:
                print('Plugin flag set to false for package "{}"'
                      .format(name))
                cleanup()

            # Verify config is a dict (i.e. object) if present
            if 'config' in manifest and \
                    not isinstance(manifest['config'], dict):
                print('Invalid config object:\n{}'
                      .format(json.dumps(manifest, indent=2)))
                cleanup()

            # Validate the config schema, if present
            if 'schema' in manifest['moziot']:
                try:
                    jsonschema.Draft4Validator.check_schema(
                        manifest['moziot']['schema'])
                except jsonschema.SchemaError as e:
                    print('Invalid config schema for {}: {}'
                          .format(name, e))
                    cleanup()

            cleanup(exit=False)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
