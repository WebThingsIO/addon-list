#!/usr/bin/env python3

import json
import subprocess
import sys
import urllib.error
import urllib.request

_LIST = './list.json'
_URL = 'https://s3-us-west-2.amazonaws.com/mozilla-gateway-addons/'

def get_builder_files(prefix):
    try:
        output = subprocess.check_output([
          'aws', 's3api', 'list-objects',
          '--bucket', 'mozilla-gateway-addons',
          '--prefix', prefix])
    except (FileNotFoundError):
        print('Please install aws cli tool')
        sys.exit(1)
    if len(output) == 0:
        return []
    try:
        aws_files = json.loads(output)
    except json.decoder.JSONDecodeError:
        print('Invalid AWS json output')
        print(output)
        sys.exit(1)
    return aws_files


def move_aws_builder_files(prefix):
    try:
        output = subprocess.check_output([
          'aws', 's3', 'mv',
          '--recursive',
          '--exclude', '*',
          '--include', '{}*'.format(prefix),
          '--acl', 'public-read',
          's3://mozilla-gateway-addons/builder/',
          's3://mozilla-gateway-addons/'])
    except (FileNotFoundError):
        print('Failed to move files from builder/ directory on AWS')
        sys.exit(1)


def get_sha256sum(filename):
    url = '{}{}.sha256sum'.format(_URL, filename)
    try:
        with urllib.request.urlopen(url) as response:
            sha256sum = response.read().decode('utf-8').split()[0]
    except urllib.error.URLError:
        print('Failed to download {}'.format(url))
        sys.exit(1)
    return sha256sum


def update_file(entry, adapter, version, filename):
    # Grab the contents of the sha256sum file.
    sha256sum = get_sha256sum(filename)
    for package in entry['packages']:
        old_version = package['version']
        old_url = package['url']
        new_filename_prefix = 'builder/{}-{}'.format(adapter, version)
        new_filename_suffix = filename[len(new_filename_prefix):]
        expected_old_url = '{}{}-{}{}'.format(_URL, adapter,
                                              old_version, new_filename_suffix)
        new_url = '{}{}-{}{}'.format(_URL, adapter,
                                     version, new_filename_suffix)
        if old_url == expected_old_url:
            package['url'] = new_url
            package['version'] = version
            package['checksum'] = sha256sum
            return True
    return False


def main():
    if len(sys.argv) != 3:
        print('Usage: update.py ADAPTER VERSION')
        sys.exit(1)
    adapter = sys.argv[1]
    version = sys.argv[2]

    # Make sure the file is valid JSON
    try:
        with open(_LIST, 'rt') as f:
            addon_list = json.load(f)
    except (IOError, OSError, ValueError):
        print('Failed to read file {}'.format(_LIST))
        sys.exit(1)

    for entry in addon_list:
        name = entry['name']
        if adapter != name:
            continue

        # Get a list of files which match the adapter/version
        # from the AWS server

        aws_prefix = 'builder/{}-{}'.format(adapter, version)
        aws_files = get_builder_files(aws_prefix)
        if len(aws_files) == 0:
            print('No files found in builder/ that match {}'.format(aws_prefix))
            sys.exit(1)

        print('Updating {} ...'.format(name))

        list_updated = False
        for file in aws_files['Contents']:
            filename = file['Key']
            if not filename.endswith('.sha256sum'):
                if update_file(entry, adapter, version, filename):
                    print('Updated {}'.format(filename[len('builder/'):]))
                    list_updated = True
    if list_updated:
        try:
            with open(_LIST, 'wt') as f:
                json.dump(addon_list, f, indent=2, ensure_ascii=False)
                f.write('\n')
        except (IOError, OSError):
            print('Failed to read file {}'.format(_LIST))
            sys.exit(1)
        # Move the files from the builder directory out to the main
        # directory.
        move_aws_builder_files(aws_prefix)


if __name__ == '__main__':
    main()
