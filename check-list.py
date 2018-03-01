#!/usr/bin/env python3

import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import urllib.error
import urllib.request


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
    for l in _LISTS:
        # Make sure the file is valid JSON
        try:
            with open(l, 'rt') as f:
                addon_list = json.load(f)
        except (IOError, OSError, ValueError):
            print('Failed to read list file.')
            sys.exit(1)

        required_in_list = [
            'name',
            'display_name',
            'description',
            'version',
            'url',
            'packages',
            'checksum',
            'api.min',
            'api.max',
        ]

        required_in_manifest = [
            'name',
            'version',
            'files',
            'moziot.api.min',
            'moziot.api.max',
        ]

        known_architectures = [
            'any',
            'darwin-x64',
            'linux-arm',
            'linux-ia32',
            'linux-x64',
            'win32-ia32',
            'win32-x64',
        ]

        for entry in addon_list:
            success, field = verify_fields(required_in_list, entry)
            if not success:
                print('Field "{}" missing from:\n{}'
                      .format(field, json.dumps(entry, indent=2)))
                sys.exit(1)

            name = entry['name']

            # Ensure list of architectures is valid.
            for arch in entry['packages'].keys():
                if arch not in known_architectures:
                    print('Unknown architecture for package "{}": {}'
                          .format(name, arch))
                    cleanup()

            legacy_entry = [
                {
                    'url': entry['url'],
                    'checksum': entry['checksum'],
                }
            ]

            # Download the packages.
            for package in list(entry['packages'].values()) + legacy_entry:
                if 'url' not in package or 'checksum' not in package:
                    print('Invalid package entry for "{}": {}'
                          .format(name, package))
                    cleanup()

                url = package['url']
                checksum = package['checksum']

                try:
                    urllib.request.urlretrieve(url, 'package.tgz')
                except urllib.error.URLError:
                    print('Failed to download package for "{}"'.format(name))
                    cleanup()

                # Verify the checksum.
                if checksum != hash_file('./package.tgz'):
                    print('Checksum invalid for "{}"'.format(name))
                    cleanup()

                # Check the package contents.
                try:
                    with tarfile.open('./package.tgz', 'r:gz') as t:
                        t.extractall()
                except (IOError, OSError, tarfile.TarError):
                    print('Failed to untar package for "{}"'.format(name))
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

                # Verify some additional fields.
                if not isinstance(manifest['files'], list) or \
                        len(manifest['files']) == 0:
                    print('Invalid files array:\n{}'
                          .format(json.dumps(manifest, indent=2)))
                    cleanup()

                if 'config' in manifest and \
                        not isinstance(manifest['config'], dict):
                    print('Invalid config object:\n{}'
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
                    print('Name mismatch for package "{}"')
                    print('name from package.json "{}" doesn\'t match '
                          'name from list.json'.format(name, manifest['name']))
                    cleanup()

                # Verify that the version matches
                if manifest['version'] != entry['version']:
                    print('Version mismatch for package "{}": '
                          'version from package.json "{}" doesn\'t match '
                          'version from list.json "{}"'
                          .format(name, manifest['version'], entry['version']))
                    cleanup()

                # Verify that the API version matches
                if manifest['moziot']['api']['min'] != entry['api']['min']:
                    print('api.min Version mismatch for package "{}": '
                          'api.min version from package.json "{}" doesn\'t '
                          'match api.min version from list.json "{}"'
                          .format(name, manifest['moziot']['api']['min'],
                                  entry['api']['min']))
                    cleanup()

                if manifest['moziot']['api']['max'] != entry['api']['max']:
                    print('api.max version mismatch for package "{}": '
                          'api.max version from package.json "{}" doesn\'t '
                          'match api.max version from list.json "{}"'
                          .format(name, manifest['moziot']['api']['max'],
                                  entry['api']['max']))
                    cleanup()

                cleanup(exit=False)


if __name__ == '__main__':
    main()
