#!/usr/bin/env python3

import json
import os
import sys


def translate(package_json):
    dname = os.path.dirname(package_json)
    manifest_json = os.path.join(dname, 'manifest.json')

    try:
        with open(package_json, 'rt') as f:
            package = json.load(f)
    except (IOError, OSError, ValueError) as e:
        print('Error loading package.json:', e)
        sys.exit(1)

    manifest = {
        'description': package['description'],
        'gateway_specific_settings': {
            'webthings': {
                'exec': package['moziot']['exec'],
                'strict_min_version': '0.10.0',
                'strict_max_version': '*',
            },
        },
        'homepage_url': package['homepage'],
        'id': package['name'],
        'license': package['license'],
        'manifest_version': 1,
        'name': package['display_name'],
        'short_name': package['display_name'][0:12],
        'version': package['version'],
    }

    if type(package['author']) is str or unicode:
        manifest['author'] = package['author']
    else:
        manifest['author'] = package['author']['name']

    if 'type' in package['moziot']:
        manifest['gateway_specific_settings']['webthings']['primary_type'] = \
            package['moziot']['type']
    else:
        manifest['gateway_specific_settings']['webthings']['primary_type'] = \
            'adapter'

    if 'config' in package['moziot'] or 'schema' in package['moziot']:
        manifest['options'] = {}

        if 'config' in package['moziot']:
            manifest['options']['default'] = package['moziot']['config']

        if 'schema' in package['moziot']:
            manifest['options']['schema'] = package['moziot']['schema']

    try:
        with open(manifest_json, 'wt') as f:
            json.dump(manifest, f, ensure_ascii=True, indent=2, sort_keys=True)
    except (IOError, OSError, ValueError) as e:
        print('Error writing manifest.json:', e)
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:\n\t{} /path/to/package.json'.format(sys.argv[0]))
        sys.exit(1)

    translate(sys.argv[1])
