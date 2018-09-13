from ..resource import ResourceManager
import argparse
import sys

DESCR = 'Download and pre-position model resources for subsequent analysis calls.'
EXAMPLE = """
Example:

    harmonica download tpxo8
"""

def config_parser(p, sub=False):
    # Subparser info
    if sub:
        p = p.add_parser(
            'download',
            description=DESCR,
            help=DESCR,
            epilog=EXAMPLE,
            add_help=False,
        )

    p.add_argument(
        'model',
        choices=ResourceManager.RESOURCES.keys(),
        default=ResourceManager.DEFAULT_RESOURCE,
        help='Constituent model specification, default: tpxo8',
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
    ResourceManager(model=args.model).download_model()
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