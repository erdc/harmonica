
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

import os.path

config = {
	'pre_existing_data_dir': '', # ignored if empty string
    'data_dir': os.path.join(os.path.dirname(__file__), 'data'),
}
