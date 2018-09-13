from ..tidal_constituents import Constituents
from .common import add_common_args, add_loc_model_args, add_const_out_args
import argparse
import sys

DESCR = 'Get specified tidal constituents at specified locations.'
EXAMPLE = """
Example:

    harmonica constituents 38.375789 -74.943915 -C M2 K1 -M tpxo8
"""

def config_parser(p, sub=False):
    # Subparser info
    if sub:
        p = p.add_parser(
            'constituents',
            description=DESCR,
            help=DESCR,
            epilog=EXAMPLE,
            add_help=False,
        )

    add_common_args(p)
    add_loc_model_args(p)
    add_const_out_args(p)


def parse_args(args):
    p = argparse.ArgumentParser(
        description=DESCR,
        epilog=EXAMPLE,
        add_help=False,
    )
    config_parser(p)
    return p.parse_args(args)


def execute(args):
    cons = Constituents().get_components([args.lat, args.lon], model=args.model, cons=args.cons,
        positive_ph=args.positive_phase)
    out = cons.data.to_csv(args.output, sep='\t', header=True, index=True, index_label='constituent')
    if args.output is None:
        print(out)
    print("\nComplete.\n")


def main(args=None):
    if not args:
        args = sys.argv[1:]
    try:
        execute(parse_args(args))
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)
    return