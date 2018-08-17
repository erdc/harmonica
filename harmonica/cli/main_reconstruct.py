from ..tidal_constituents import Constituents
from ..harmonica import Tide
from .common import add_common_args, add_loc_model_args, add_const_out_args
from pytides.tide import Tide as pyTide
from datetime import date, datetime
import argparse
import numpy as np
import pandas as pd
import sys

DESCR = 'Reconstruct the tides at specified location and times.'
EXAMPLE = """
Example:

    harmonica reconstruct 38.375789 -74.943915
"""

def validate_date(value):
    try:
        # return date.fromisoformat(value) # python 3.7
        return pd.datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(value)
        raise argparse.ArgumentTypeError(msg)


def check_positive(value):
    flt = float(value)
    if flt <= 0:
        msg = "Not a valid time length: {0}".format(value)
        raise argparse.ArgumentTypeError(msg)
    return flt


def config_parser(p, sub=False):
    # Subparser info
    if sub:
        p = p.add_parser(
            'reconstruct',
            description=DESCR,
            help=DESCR,
            epilog=EXAMPLE,
            add_help=False,
        )

    add_common_args(p)
    p.add_argument(
        '-S', '--start_date',
        type=validate_date,
        default=date.today(),
        help='Start Date [YYYY-MM-DD], default: today'
    )
    p.add_argument(
        '-L', '--length',
        type=check_positive,
        default=7.,
        help='Length of series in days [positive non-zero], default: 7'
    )
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
    times = pyTide._times(datetime.fromordinal(args.start_date.toordinal()), np.arange(args.length * 24., dtype=float))
    tide = Tide().reconstruct_tide(loc=[args.lat, args.lon], times=times, model=args.model, cons=args.cons,
        positive_ph=args.positive_phase)
    out = tide.data.to_csv(args.output, sep='\t', header=True, index=False)
    if args.output is None:
        print(out)
    print('\nComplete.\n')


def main(*args, **kwargs):
    if not args:
        args = sys.argv
    try:
        execute(parse_args(args[1:]))
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)
    return