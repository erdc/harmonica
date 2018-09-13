from ..resource import ResourceManager
import argparse
import sys

DESCR = 'Manage model resources for subsequent analysis calls.'
EXAMPLE = """
Example:

    harmonica resources download tpxo8
"""
actions = {
    'download': 'download_model',
    'remove': 'remove_model',
}


def config_parser(p, sub=False):
    # Subparser info
    if sub:
        p = p.add_parser(
            'resources',
            description=DESCR,
            help=DESCR,
            epilog=EXAMPLE,
            add_help=False,
        )

    p.add_argument(
        'action',
        choices=actions.keys(),
        help='Action to perform on model resources',
    )

    p.add_argument(
        'model',
        choices=ResourceManager.RESOURCES.keys(),
        help='Constituent model specification',
    )


def parse_args(args):
    p = argparse.ArgumentParser(
        description=DESCR,
        epilog=EXAMPLE,
        add_help=False,
    )
    config_parser(p)
    return p.parse_args(args)


def execute(args):
    eval('ResourceManager(model=args.model).{}()'.format(actions[args.action]))
    print('\nComplete.\n')


def main(args=None):
    if not args:
        args = sys.argv[1:]
    try:
        execute(parse_args(args))
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)
    return