#!/usr/bin/env python3

import json

_LIST = './list.json'


def main():
    with open(_LIST, 'rt') as f:
        addons = json.load(f)

    contributors = set([a['author'] for a in addons])

    print('Total contributors: {}'.format(len(contributors)))
    for c in contributors:
        print('    {}'.format(c))

    print('\nTotal add-ons: {}'.format(len(addons)))
    for a in addons:
        print('    {}'.format(a['name']))


if __name__ == '__main__':
    main()
