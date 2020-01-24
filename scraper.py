#!/usr/bin/python

__author__ = ['[Majid Rouhi](https://thiswayyoufools.com)']
__date__ = '2020.01.24'

import getopt
import sys

from scraper.instagram import Instagram


def main(argv):
    target_username = None
    post_limit = None
    help_text = '''\nUsage:  scraper [OPTIONS]
    \nOptions:
    \n\t-t, --target\tTargeted username for scraping
    \n\t-l, --limit\tNumber of posts for scraping from the last post
    \nRun \'scraper --help\' for more information.\n'''

    try:
        opts, args = getopt.getopt(argv, 'ht:l:', ['target=', 'limit='])
    except getopt.GetoptError:
        sys.stdout.write(help_text)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            sys.stdout.write(help_text)
            sys.exit()
        elif opt in ('-t', '--target'):
            target_username = arg
        elif opt in ('-l', '--limit'):
            post_limit = arg

    if target_username:
        ins = Instagram(target_username)

        if not ins.check_username():
            sys.stderr.write(
                f'\nCan\'t find `{target_username}` page\'s.\n\n')
            sys.exit(1)

        ins.clone(post_limit)
    else:
        sys.stdout.write(help_text)
        sys.exit(2)


if __name__ == '__main__':
    main(sys.argv[1:])
