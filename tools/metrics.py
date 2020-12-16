#!/usr/bin/env python3

import glob
import json
import os

_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
_ADDONS_DIR = os.path.join(_ROOT, 'addons')


def main():
    addons = []

    for path in sorted(glob.glob(os.path.join(_ADDONS_DIR, '*.json'))):
        with open(path, 'rt') as f:
            addons.append(json.load(f))

    contributors = set([a['author'] for a in addons])

    print('Total contributors: {}'.format(len(contributors)))
    for c in sorted(contributors, key=lambda x: x.lower()):
        print('    {}'.format(c))

    print('\nTotal add-ons: {}'.format(len(addons)))
    for a in sorted(addons, key=lambda x: x['name'].lower()):
        print('    {}'.format(a['name']))


if __name__ == '__main__':
    main()
