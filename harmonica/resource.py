from harmonica import config
from urllib.request import urlopen
import os.path
import string
import xarray as xr

class ResourceManager(object):
    """Harmonica resource manager to retrieve and access tide models"""

    # Dictionay of model information
    RESOURCES = {
        'tpxo9': {
            'resource_atts': {
                'url': "ftp://ftp.oce.orst.edu/dist/tides/Global/tpxo9_netcdf.tar.gz",
                'archive': 'gz',
            },
            'dataset_atts': {
                'units_multiplier': 1., # meters
            },
            'consts': [{ # grouped by dimensionally compatiable files
                '2N2': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'K1': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'K2': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'M2': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'M4': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'MF': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'MM': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'MN4': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'MS4': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'N2': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'O1': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'P1': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'Q1': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'S1': 'tpxo9_netcdf/h_tpxo9.v1.nc',
                'S2': 'tpxo9_netcdf/h_tpxo9.v1.nc',
            },],
        },
        'tpxo8': {
            'resource_atts': {
                'url': "ftp://ftp.oce.orst.edu/dist/tides/TPXO8_atlas_30_v1_nc/",
                'archive': None,
            },
            'dataset_atts': {
                'units_multiplier': 0.001, # mm to meter
            },
            'consts': [ # grouped by dimensionally compatiable files 
                { # 1/30 degree
                    'K1': 'hf.k1_tpxo8_atlas_30c_v1.nc',
                    'K2': 'hf.k2_tpxo8_atlas_30c_v1.nc',
                    'M2': 'hf.m2_tpxo8_atlas_30c_v1.nc',
                    'M4': 'hf.m4_tpxo8_atlas_30c_v1.nc',
                    'N2': 'hf.n2_tpxo8_atlas_30c_v1.nc',
                    'O1': 'hf.o1_tpxo8_atlas_30c_v1.nc',
                    'P1': 'hf.p1_tpxo8_atlas_30c_v1.nc',
                    'Q1': 'hf.q1_tpxo8_atlas_30c_v1.nc',
                    'S2': 'hf.s2_tpxo8_atlas_30c_v1.nc',
                },
                { # 1/6 degree
                    'MF': 'hf.mf_tpxo8_atlas_6.nc',
                    'MM': 'hf.mm_tpxo8_atlas_6.nc',
                    'MN4': 'hf.mn4_tpxo8_atlas_6.nc',
                    'MS4': 'hf.ms4_tpxo8_atlas_6.nc',
                },
            ],
        },
        'tpxo7': {
            'resource_atts': {
                'url': "ftp://ftp.oce.orst.edu/dist/tides/Global/tpxo7.2_netcdf.tar.Z",
                'archive': 'gz', # gzip compression
            },
            'dataset_atts': {
                'units_multiplier': 1., # meter
            },
            'consts': [{ # grouped by dimensionally compatiable files
                'K1': 'DATA/h_tpxo7.2.nc',
                'K2': 'DATA/h_tpxo7.2.nc',
                'M2': 'DATA/h_tpxo7.2.nc',
                'M4': 'DATA/h_tpxo7.2.nc',
                'MF': 'DATA/h_tpxo7.2.nc',
                'MM': 'DATA/h_tpxo7.2.nc',
                'MN4': 'DATA/h_tpxo7.2.nc',
                'MS4': 'DATA/h_tpxo7.2.nc',
                'N2': 'DATA/h_tpxo7.2.nc',
                'O1': 'DATA/h_tpxo7.2.nc',
                'P1': 'DATA/h_tpxo7.2.nc',
                'Q1': 'DATA/h_tpxo7.2.nc',
                'S2': 'DATA/h_tpxo7.2.nc',
            },],
        },
    }
    DEFAULT_RESOURCE = 'tpxo9'

    def __init__(self, model=DEFAULT_RESOURCE):
        if model not in self.RESOURCES:
            raise ValueError('Model not recognized.')
        self.model = model
        self.model_atts = self.RESOURCES[self.model]
        self.datasets = []


    def __del__(self):
        for d in self.datasets:
            d.close()


    def available_constituents(self):
        # get keys from const groups as list of lists and flatten
        return [c for sl in [grp.keys() for grp in self.model_atts['consts']] for c in sl]


    def get_units_multiplier(self):
        return self.model_atts['dataset_atts']['units_multiplier']
    

    def download(self, resource, destination_dir):
        """Download a specified model resource."""
        if not os.path.isdir(destination_dir):
            os.makedirs(destination_dir)

        rsrc_atts = self.model_atts['resource_atts']
        url = rsrc_atts['url']
        if rsrc_atts['archive'] is None:
            url = "".join((url, resource))

        print('Downloading resource: {}'.format(url))
        response = urlopen(url)

        path = os.path.join(destination_dir, resource)
        if rsrc_atts['archive'] is not None:
            import tarfile

            try:
                tar = tarfile.open(mode='r:{}'.format(rsrc_atts['archive']), fileobj=response)
            except IOError as e:
                print(str(e))
            else:
                rsrcs = set(c for sl in [x.values() for x in self.model_atts['consts']] for c in sl)
                tar.extractall(path = destination_dir, members = [m for m in tar.getmembers() if m.name in rsrcs])
                tar.close()
        else:
            with open(path, 'wb') as f:
                f.write(response.read())

        return path


    def download_model(self):
        """Download all of the model's resources for later use."""
        resources = set(r for sl in [grp.values() for grp in self.model_atts['consts']] for r in sl)
        resource_dir = os.path.join(config['data_dir'], self.model)
        for r in resources:
            path = os.path.join(resource_dir, r)
            if not os.path.exists(path):
                self.download(r, resource_dir)


    def remove_model(self):
        """Remove all of the model's resources."""
        resource_dir = os.path.join(config['data_dir'], self.model)
        if os.path.exists(resource_dir):
            import shutil

            shutil.rmtree(resource_dir, ignore_errors=True)


    def get_datasets(self, constituents):
        """Returns a list of xarray datasets."""
        available = self.available_constituents()
        if any(const not in available for const in constituents):
            raise ValueError('Constituent not recognized.')
        # handle compatiable files together
        self.datasets = []
        for const_group in self.model_atts['consts']:
            rsrcs = set(const_group[const] for const in set(constituents) & set(const_group))

            paths = set()
            if (config['pre_existing_data_dir']):
                missing = set()
                for r in rsrcs:
                    path = os.path.join(config['pre_existing_data_dir'], self.model, r)
                    paths.add(path) if os.path.exists(path) else missing.add(r)
                rsrcs = missing
                if not rsrcs and paths:
                    self.datasets.append(xr.open_mfdataset(paths, engine='netcdf4', concat_dim='nc'))
                    continue

            resource_dir = os.path.join(config['data_dir'], self.model)
            for r in rsrcs:
                path = os.path.join(resource_dir, r)
                if not os.path.exists(path):
                    self.download(r, resource_dir)
                paths.add(path)

            if paths:
                self.datasets.append(xr.open_mfdataset(paths, engine='netcdf4', concat_dim='nc'))

        return self.datasets