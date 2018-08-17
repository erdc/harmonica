from .tidal_constituents import Constituents
from .resource import ResourceManager
from pytides.astro import astro
from pytides.tide import Tide as pyTide
import pytides.constituent as pycons
from datetime import datetime
import numpy as np
import pandas as pd
import sys


class Tide:
    """Harmonica tide object."""

    # Dictionary to convert generic uppercase constituent name to pytides name;
    # if name isn't listed, then the associated pytides name is all uppercase 
    PYTIDES_CON_MAPPER = {
        'SA': 'Sa',
        'SSA': 'Ssa',
        'MM': 'Mm',
        'MF': 'Mf',
        'NU2': 'nu2',
        'LAMBDA2': 'lambda2',
        'RHO1': 'rho1',
        'MU2': 'mu2',
    }

    def __init__(self):
        # tide dataframe:
        #   date_times (year, month, day, hour, minute, second; UTC/GMT)
        self.data = pd.DataFrame(columns=['datetimes', 'water_level'])
        self.constituents = Constituents()


    def reconstruct_tide(self, loc, times, model=ResourceManager.DEFAULT_RESOURCE,
            cons=[], positive_ph=False, offset=None):
        """Rescontruct a tide signal water levels at the given location and times

        Args:
            loc (tuple(float, float)): latitude [-90, 90] and longitude [-180 180] or [0 360] of the requested point.
            times (ndarray(datetime)): Array of datetime objects associated with each water level data point.
            model (str, optional): Model name, defaults to 'tpxo8'.
            cons (list(str), optional): List of constituents requested, defaults to all constituents if None or empty.
            positive_ph (bool, optional): Indicate if the returned phase should be all positive [0 360] (True) or
                [-180 180] (False, the default).
            offset (float, optional): If not None, includes a generic constituent with a phase of the given value.

        """

        # get constituent information
        self.constituents.get_components(loc, model, cons, positive_ph)

        ncons = len(self.constituents.data) + (1 if offset is not None else 0)
        tide_model = np.zeros(ncons, dtype=pyTide.dtype)
        # load specified model constituent components into pytides model object
        for i, key in enumerate(self.constituents.data.index.values):
            tide_model[i]['constituent'] = eval('pycons._{}'.format(self.PYTIDES_CON_MAPPER.get(key, key)))
            tide_model[i]['amplitude'] = self.constituents.data.loc[key].amplitude
            tide_model[i]['phase'] = self.constituents.data.loc[key].phase
        # if an offset is provided then add as spoofed constituent Z0
        if offset is not None:
            tide_model[-1]['constituent'] = pycons._Z0
            tide_model[-1]['amplitude'] = 0.
            tide_model[-1]['phase'] = offset

        # reconstruct the tides, store in self
        self.data['datetimes'] = pd.Series(times)
        self.data['water_level'] = pd.Series(pyTide(model=tide_model, radians=False).at(times), index=self.data.index)

        return self


    def deconstruct_tide(self, water_level, times, cons=[], n_period=6, positive_ph=False):
        """Method to use pytides to deconstruct the tides and reorganize results back into the class structure.

        Args:
            water_level (ndarray(float)): Array of water levels.
            times (ndarray(datetime)): Array of datetime objects associated with each water level data point.
            cons (list(str), optional): List of constituents requested, defaults to all constituents if None or empty.
            n_period(int): Number of periods a constituent must complete during times to be considered in analysis.
            positive_ph (bool, optional): Indicate if the returned phase should be all positive [0 360] (True) or
                [-180 180] (False, the default).

        Returns:
            A dataframe of constituents information in Constituents class

        """
        # Fit the tidal data to the harmonic model using pytides
        if not cons:
            cons = pycons.noaa
        else:
            cons = [eval('pycons._{}'.format(self.PYTIDES_CON_MAPPER.get(c, c))) for c in cons
                if c in self.constituents.NOAA_SPEEDS]
        self.model_to_dataframe(pyTide.decompose(water_level, times, constituents=cons, n_period=n_period),
            times[0], positive_ph=positive_ph)
        return self


    def model_to_dataframe(self, tide, t0=datetime.now(), positive_ph=False):
        """Method to reorganize data from the pytides tide model format into the native dataframe format.

        Args:
            tide (pytides object): Tide model object from pytides.
            t0 (datetime, optional): Time at which to evaluate speed based on astronomical parameters (speeds vary
                slowly over time), defaults to current date and time.
            positive_ph (bool, optional): Indicate if the returned phase should be all positive [0 360] (True) or
                [-180 180] (False, the default).

        Returns:
            A dataframe of constituents information in Constituents class

        """
        # helper function to extract constituent information from Tide model
        def extractor(c):
            # info: name, amplitude, phase, speed
            return (c[0].name.upper(), c[1], c[2], c[0].speed(astro(t0)))
        # create a filtered array of constituent information
        cons = np.asarray(np.vectorize(extractor)(tide.model[tide.model['constituent'] != pycons._Z0])).T
        # convert into dataframe
        df = pd.DataFrame(cons[:,1:], index=cons[:,0], columns=['amplitude', 'phase', 'speed'], dtype=float)
        self.constituents.data = pd.concat([self.constituents.data, df], axis=0, join='inner')
        # convert phase if necessary
        if not positive_ph:
            self.constituents.data['phase'] = np.where(self.constituents.data['phase'] > 180.,
                self.constituents.data['phase'] - 360., self.constituents.data['phase'])