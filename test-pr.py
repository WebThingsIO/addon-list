#!/usr/bin/env python3

import json
import os
import re
import shlex
import sys
import urllib.request


def main():
    with open(os.environ['GITHUB_EVENT_PATH']) as f:
        event = json.load(f)

    url = 'https://api.github.com/repos/{}/pulls/{}/files'.format(
        os.environ['GITHUB_REPOSITORY'],
        event['pull_request']['number'],
    )

    r = urllib.request.Request(url, headers={'Accept': 'application/json'})
    f = urllib.request.urlopen(r)
    files = json.load(f)
    files = [x['filename'] for x in files]

    addons_changed = []
    schema_changed = False
    checker_changed = False
    for fname in files:
        match = re.match(r'^addons/([^/]+)\.json$', fname)
        if match and os.path.exists(fname):
            addons_changed.append(match.group(1))
        elif re.match(r'^schema/.+$', fname):
            schema_changed = True
        elif fname == 'tools/check-list.py':
            checker_changed = True

    if schema_changed or checker_changed:
        return os.system('./tools/check-list.py')

    if len(addons_changed) > 0:
        return os.system('./tools/check-list.py {}'.format(
            ' '.join([shlex.quote(a) for a in addons_changed]))
        )

    return 0


if __name__ == '__main__':
    # Sometimes, check-list.py returns 256. Apparently, sys.exit() will only
    # accept 0-255, so we have to adjust. Weird.
    if main() > 0:
        sys.exit(1)
