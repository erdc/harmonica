from .resource import ResourceManager
from bisect import bisect
import os
import numpy as np
import pandas as pd
import sys


class Constituents:
    """Harmonica tidal constituents."""

    # Dictionary of NOAA constituent speed constants (deg/hr)
    # Source: https://tidesandcurrents.noaa.gov
    # The speed is the rate change in the phase of a constituent, and is equal to 360 degrees divided by the
    # constituent period expressed in hours
    NOAA_SPEEDS = {
        'OO1': 16.139101,
        '2Q1': 12.854286,
        '2MK3': 42.92714,
        '2N2': 27.895355,
        '2SM2': 31.015896,
        'K1': 15.041069,
        'K2': 30.082138,
        'J1': 15.5854435,
        'L2': 29.528479,
        'LAM2': 29.455626,
        'M1': 14.496694,
        'M2': 28.984104,
        'M3': 43.47616,
        'M4': 57.96821,
        'M6': 86.95232,
        'M8': 115.93642,
        'MF': 1.0980331,
        'MK3': 44.025173,
        'MM': 0.5443747,
        'MN4': 57.423832,
        'MS4': 58.984104,
        'MSF': 1.0158958,
        'MU2': 27.968208,
        'N2': 28.43973,
        'NU2': 28.512583,
        'O1': 13.943035,
        'P1': 14.958931,
        'Q1': 13.398661,
        'R2': 30.041067,
        'RHO': 13.471515,
        'S1': 15.0,
        'S2': 30.0,
        'S4': 60.0,
        'S6': 90.0,
        'SA': 0.0410686,
        'SSA': 0.0821373,
        'T2': 29.958933,
    }

    def __init__(self):
        # constituent information dataframe:
        #   amplitude (meters)
        #   phase (degrees)
        #   speed (degrees/hour, UTC/GMT)
        self.data = pd.DataFrame(columns=['amplitude', 'phase', 'speed'])


    def get_components(self, loc, model=ResourceManager.DEFAULT_RESOURCE, cons=[], positive_ph=False):
        """Query the a tide model database and return amplitude, phase and speed for a location.

        Currently written to query tpxo7, tpxo8, and tpxo9 tide models.

        Args:
            loc (tuple(float, float)): latitude [-90, 90] and longitude [-180 180] or [0 360] of the requested point.
            model (str, optional): Model name, defaults to 'tpxo8'.
            cons (list(str), optional): List of constituents requested, defaults to all constituents if None or empty.
            positive_ph (bool, optional): Indicate if the returned phase should be all positive [0 360] (True) or
                [-180 180] (False, the default).

        Returns:
            A dataframe of constituent information including amplitude (meters), phase (degrees) and
                speed (degrees/hour, UTC/GMT)
                
        """

        # ensure lower case
        model = model.lower()
        if model == 'tpxo7_2':
            model = 'tpxo7'

        lat, lon = loc
        # check the phase of the longitude
        if lon < 0:
            lon = lon + 360.

        resources = ResourceManager(model=model)
        # if no constituents were requested, return all available
        if cons is None or not len(cons):
            cons = resources.available_constituents()
        # open the netcdf database(s)
        for d in resources.get_datasets(cons):
            # remove unnecessary data array dimensions if present (e.g. tpxo7.2)
            if 'nx' in d.lat_z.dims:
                d['lat_z'] = d.lat_z.sel(nx=0, drop=True)
            if 'ny' in d.lon_z.dims:
                d['lon_z'] = d.lon_z.sel(ny=0, drop=True)
            # get the dataset constituent name array from data cube
            nc_names = [x.tostring().decode('utf-8').strip().upper() for x in d.con.values]
            for c in set(cons) & set(nc_names):
                # get constituent and bounding indices within the data cube
                idx = {'con': nc_names.index(c)}
                idx['top'] = bisect(d.lat_z[idx['con']], lat)
                idx['right'] = bisect(d.lon_z[idx['con']], lon)
                idx['bottom'] = idx['top'] - 1
                idx['left'] = idx['right'] - 1
                # get distance from the bottom left to the requested point
                dx = (lon - d.lon_z.values[idx['con'], idx['left']]) / \
                     (d.lon_z.values[idx['con'], idx['right']] - d.lon_z.values[idx['con'], idx['left']])
                dy = (lat - d.lat_z.values[idx['con'], idx['bottom']]) / \
                     (d.lat_z.values[idx['con'], idx['top']] - d.lat_z.values[idx['con'], idx['bottom']])
                # calculate weights for bilinear spline
                weights = np.array([
                    (1. - dx) * (1. - dy),  # w00 :: bottom left
                    (1. - dx) * dy,         # w01 :: bottom right
                    dx * (1. - dy),         # w10 :: top left
                    dx * dy                 # w11 :: top right
                ]).reshape((2,2))
                weights = weights / weights.sum()
                # devise the slice to subset surrounding values
                query = np.s_[idx['con'], idx['left']:idx['right']+1, idx['bottom']:idx['top']+1]
                # calculate the weighted tide from real and imaginary components
                h = np.complex((d.hRe.values[query] * weights).sum(), -(d.hIm.values[query] * weights).sum())
                # get the phase and amplitude
                ph = np.angle(h, deg=True)
                # place info into data table
                self.data.loc[c] = [
                    # amplitude
                    np.absolute(h) * resources.get_units_multiplier(),
                    # phase
                    ph + (360. if positive_ph and ph < 0 else 0),
                    # speed
                    self.NOAA_SPEEDS[c]
                ]

        return self