from .. import __version__
from ..resource import ResourceManager
from argparse import _HelpAction
from datetime import date
import itertools

def add_common_args(p):
	# You must use the add_help=False argument to ArgumentParser or add_parser
    p.add_argument(
        '-h', '--help',
        action=_HelpAction,
        help="Show this help message and exit.",
    )
    p.add_argument(
        '-V', '--version',
        action='version',
        version='harmonica %s' % __version__,
        help="Show the harmonica version number and exit",
    )


def add_loc_model_args(p):
    # Required positional arguments
    # This combined argument is preferred but there is a bug in argparse with unpacking a multi-value metavar
    # p.add_argument(
    #     'loc',
    #     type=float,
    #     nargs=2,
    #     help='Desired location [latitude, longitude]',
    #     metavar=('LAT', 'LON'),
    # )
    p.add_argument(
        'lat',
        type=float,
        help='Desired latitude location',
        metavar='LAT',
    )
    p.add_argument(
        'lon',
        type=float,
        help='Desired longitude location',
        metavar='LON',
    )
    # Optional arguments
    p.add_argument(
        '-M', '--model',
        choices=ResourceManager.RESOURCES.keys(),
        default=ResourceManager.DEFAULT_RESOURCE,
        help='Optional constituent model specification, default: {}'.format(ResourceManager.DEFAULT_RESOURCE),
    )


def add_const_out_args(p):
    p.add_argument(
        '-C', '--cons',
        nargs='+',
        default=None,
        help='Optional list of constituents to retrieve; retrieves all by default',
    )
    p.add_argument(
        '-P', '--positive_phase',
        action='store_true',
        default=False,
        help='Boolean to indicate whether phase should be all positive [0,360] (True) or [-180,180] (False; default)',
    )
    p.add_argument(
        '-O', '--output',
        default=None,
        help='Write output to specified file',
    )