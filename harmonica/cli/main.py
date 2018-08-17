from .. import __version__
from .common import add_common_args
from .main_constituents import config_parser as config_parser_constituents
from .main_deconstruct import config_parser as config_parser_deconstruct
from .main_reconstruct import config_parser as config_parser_reconstruct
from .main_resources import config_parser as config_parser_resources
from importlib import import_module
import argparse
import sys

def main():
    p = argparse.ArgumentParser(
        description='harmonica is a tool for working with tidal harmonics.',
        add_help=False,
    )
    add_common_args(p)
    sps = p.add_subparsers(
        metavar='command',
        dest='cmd',
    )
    sps.required = True
    config_parser_constituents(sps, True)
    config_parser_deconstruct(sps, True)
    config_parser_reconstruct(sps, True)
    config_parser_resources(sps, True)

    args = p.parse_args(sys.argv[1:])
    try:
        getattr(sys.modules['harmonica.cli.main_{}'.format(args.cmd)], 'execute')(args)
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)
    return


if __name__ == '__main__':
    sys.exit(main())