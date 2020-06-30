#!/usr/bin/env python3

import glob
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
_ADDONS_DIR = os.path.join(_ROOT, 'addons')
_S3_URL = 'https://s3-us-west-2.amazonaws.com/mozilla-gateway-addons/'


def copy_to_s3(url):
    print('Moving package to S3: {}'.format(url))

    fname = url.split('/')[-1]

    try:
        urllib.request.urlretrieve(url, fname)
    except urllib.error.URLError as e:
        print('Failed to download {}: {}'.format(url, e))
        sys.exit(1)

    try:
        subprocess.check_output([
          'aws', 's3', 'cp',
          '--acl', 'public-read',
          fname,
          's3://mozilla-gateway-addons/'
        ])
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print('Failed to move {} to S3: {}'.format(fname, e))
        sys.exit(1)

    try:
        os.unlink(fname)
    except OSError as e:
        print('Failed to delete {}: {}'.format(fname, e))
        sys.exit(1)

    return _S3_URL + fname


def main():
    for fname in glob.glob(os.path.join(_ADDONS_DIR, '*.json')):
        try:
            with open(fname, 'rt') as f:
                data = json.load(f)
        except (IOError, OSError, ValueError) as e:
            print('Failed to read {}: {}'.format(fname, e))
            sys.exit(1)

        modified = False
        for package in data['packages']:
            if package['url'].startswith(_S3_URL):
                continue

            updated_url = copy_to_s3(package['url'])

            modified = True
            package['url'] = updated_url

        if modified:
            try:
                with open(fname, 'wt') as f:
                    json.dump(data, f, indent=2)
                    f.write('\n')
            except (IOError, OSError) as e:
                print('Failed to write {}: {}'.format(fname, e))
                sys.exit(1)


if __name__ == '__main__':
    main()
