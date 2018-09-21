from .. import harmonica
from .common import add_common_args, add_const_out_args
from pytides.tide import Tide as pyTide
from datetime import datetime
import argparse
import numpy as np
import pandas as pd
import sys

DESCR = 'Deconstruct the signal into its tidal constituents.'
EXAMPLE = """
Example:

    harmonica deconstruct CO-OPS__8760922__wl.csv --columns "Date Time" "Water Level" \
        --datetime_format '%Y-%m-%d %H:%M' -C M2 S2 N2 K1
"""

def config_parser(p, sub=False):
    # Subparser info
    if sub:
        p = p.add_parser(
            'deconstruct',
            description=DESCR,
            help=DESCR,
            epilog=EXAMPLE,
            add_help=False,
        )

    # Required positional arguments
    p.add_argument(
        'signal',
        type=str,
        help='File to read the tidal signal to deconstruct (CSV formatted)',
        metavar='SIGNAL',
    )

    add_common_args(p)
    p.add_argument(
        '--datetime_format',
        default='%Y-%m-%d %H:%M:%S',
        help="Format of 'datetime' values in signal file, default: '%%Y-%%m-%%d %%H:%%M:%%S' (used by Pandas " \
            "datetime parser)",
        dest='dt_format',
    )
    p.add_argument(
        '--columns',
        nargs='+',
        default=[0, 1],
        help="Name or index of columns in signal file to extract times and water levels; multiple columns can be " \
            "specified to combine and parse as a datetime; the last column specified is assumed to be water levels, " \
            "default: '0 1'",
        dest='dt_cols',
        metavar='COL',
    )
    p.add_argument(
        '--header',
        default=0,
        help="Row number that contains the column names (specify 'None' if no column names), default: '0'",
    )
    p.add_argument(
        '--sep',
        default=',',
        help="Field delimiter of the signal file, default: ',' (comma)",
    )
    add_const_out_args(p)
    p.add_argument(
        '--num_periods',
        type=int,
        default=6,
        help="Number of periods a constituent must complete during signal length to be considered, default: 6",
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
    args.dt_cols = [int(x) if isinstance(x, str) and x.isdigit() else x for x in args.dt_cols]
    opts = {
        'date_parser': lambda x: [pd.datetime.strptime(d, args.dt_format) for d in x],
        'parse_dates': {'datetimes': args.dt_cols[:-1]},
        'header': args.header,
        'sep': args.sep,
    }
    try:
        df = pd.read_csv(args.signal, **opts)
    except ValueError as e:
        if 'not in list' in str(e):
            print("\nThe column name '{}' is not recognized.".format(str(e).split("'")[1]))
        elif 'match format' in str(e):
            print("\nThe signal's datetime does not match the given format: {}. Verify format and/or header row " \
                "number".format(args.dt_format))
        else:
            print(str(e))
    except KeyError:
        print("\nThe column name(s) to parse the signal's datetime are not recognized.")

    wl = args.dt_cols[-1]
    wl = df.columns[wl] if isinstance(wl, int) else wl
    try:
        tide = harmonica.Tide().deconstruct_tide(df[wl], df['datetimes'], cons=args.cons,
            n_period=args.num_periods, positive_ph=args.positive_phase)
    except RuntimeWarning as w:
        if 'Number of calls to function has reached maxfev' in str(w):
            print("\nThe solver failed to converge to a solution. Provide a longer signal.")
        else:
            print(str(w))
        print('\nFailed.\n')
        return

    out = tide.constituents.data.to_csv(args.output, sep='\t', header=True, index=True, index_label='constituent')
    if args.output is None:
        print(out)
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