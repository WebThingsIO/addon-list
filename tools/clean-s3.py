#!/usr/bin/env python3

import glob
import json
import os
import subprocess
import sys

_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
_ADDONS_DIR = os.path.join(_ROOT, 'addons')


def main():
    referenced_files = set(['builder'])
    for fname in glob.glob(os.path.join(_ADDONS_DIR, '*.json')):
        try:
            with open(fname, 'rt') as f:
                data = json.load(f)
        except (IOError, OSError, ValueError) as e:
            print('Failed to read {}: {}'.format(fname, e))
            sys.exit(1)

        for package in data['packages']:
            fname = package['url'].split('/')[-1]
            referenced_files.add(fname)
            referenced_files.add('{}.sha256sum'.format(fname))

    s3_files = set()
    try:
        ret = subprocess.check_output([
          'aws', 's3', 'ls',
          '--profile', 's3-copy-action',
          's3://mozilla-gateway-addons/'
        ])

        for line in ret.decode().splitlines():
            s3_files.add(line.split()[3])
    except subprocess.CalledProcessError as e:
        print('Failed to list files in S3: {}'.format(e))
        sys.exit(1)

    s3_files.difference_update(referenced_files)

    for fname in s3_files:
        try:
            print('Removing: {}'.format(fname))
            subprocess.check_output([
              'aws', 's3', 'rm',
              '--profile', 's3-copy-action',
              's3://mozilla-gateway-addons/{}'.format(fname)
            ])
        except subprocess.CalledProcessError as e:
            print('Failed to remove {} from S3: {}'.format(fname, e))
            sys.exit(1)


if __name__ == '__main__':
    main()
