#!/usr/bin/env python3

import hashlib
import json
import jsonschema
import os
import re
import shutil
import sys
import tarfile
import urllib.error
import urllib.request

_SCHEMA = './schema.json'
_LISTS = [
    './list.json',
    './test.json',
]


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
    adapter = None
    if len(sys.argv) > 1:
        adapter = sys.argv[1]

    # Load the schema.
    with open(_SCHEMA) as f:
        schema = json.load(f)

    try:
        jsonschema.Draft4Validator.check_schema(schema)
    except jsonschema.SchemaError as e:
        print('Schema validation failed: {}'.format(e))
        sys.exit(1)

    for l in _LISTS:
        # Make sure the file is valid JSON
        try:
            with open(l, 'rt') as f:
                addon_list = json.load(f)
        except (IOError, OSError, ValueError):
            print('Failed to read list file.')
            sys.exit(1)

        jsonschema.validate(addon_list, schema)

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
            name = entry['name']

            if adapter and adapter != name:
                continue

            print('Checking {} ...'.format(name))

            # Download the packages.
            for package in entry['packages']:
                version = package['version']
                url = package['url']
                checksum = package['checksum']

                try:
                    urllib.request.urlretrieve(url, 'package.tgz')
                except urllib.error.URLError:
                    print('Failed to download package for "{}": {}'
                          .format(name, package['architecture']))
                    cleanup()

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
                elif manifest['author'] != entry['author']:
                    print('Author mismatch for package "{}": '
                          'author from package.json "{}" doesn\'t match '
                          'author from list.json "{}"'
                          .format(name, manifest['author'], entry['author']))
                    cleanup()

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
    main()
