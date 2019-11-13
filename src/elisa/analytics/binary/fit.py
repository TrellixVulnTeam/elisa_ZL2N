import functools
import numpy as np

from copy import copy
from typing import Tuple, List
from scipy.optimize import least_squares

from elisa.atm import atm_file_prefix_to_quantity_list
from elisa.binary_system.system import BinarySystem
from elisa.conf import config
from elisa.observer.observer import Observer
from elisa.logger import getLogger

from elisa.analytics.binary import (
    utils as analutils,
    model
)

logger = getLogger('analytics.binary.fit')

ALL_PARAMS = ['inclination',
              'p__mass',
              'p__t_eff',
              'p__surface_potential',
              'p__gravity_darkening',
              'p__albedo',
              'p__metallicity',
              's__mass',
              's__t_eff',
              's__surface_potential',
              's__gravity_darkening',
              's__albedo',
              's__metallicity']

TEMPERATURES = atm_file_prefix_to_quantity_list("temperature", config.ATM_ATLAS)
METALLICITY = atm_file_prefix_to_quantity_list("metallicity", config.ATM_ATLAS)


NORMALIZATION_MAP = {
    'inclination': (0, 180),
    'p__mass': (0.5, 20),
    's__mass': (0.5, 20),
    'p__t_eff': (np.min(TEMPERATURES), np.max(TEMPERATURES)),
    's__t_eff': (np.min(TEMPERATURES), np.max(TEMPERATURES)),
    'p__metallicity': (np.min(METALLICITY), np.max(METALLICITY)),
    's__metallicity': (np.min(METALLICITY), np.max(METALLICITY)),
    'p__surface_potential': (2.0, 50.0),
    's__surface_potential': (2.0, 50.0),
    'p__albedo': (0, 1),
    's__albedo': (0, 1),
    'p__gravity_darkening': (0, 1),
    's__gravity_darkening': (0, 1)
}


def update_normalization_map(update):
    """
    Update module normalization map with supplied dict.

    :param update: Dict;
    """
    NORMALIZATION_MAP.update(update)


def _renormalize_value(val, _min, _max):
    """
    Renormalize value `val` to value from interval specific for given parameter defined my `_min` and `_max`.

    :param val: float;
    :param _min: float;
    :param _max: float;
    :return: float;
    """
    return (val * (_max - _min)) + _min


def _renormalize(x, kwords):
    """
    Renormalize values from `x` to their native form.

    :param x: Iterable[float]; iterable of normalized parameter values
    :param kwords: Iterable[str]; related parmaeter names from `x`
    :return: List[float];
    """
    return [_renormalize_value(_x, *_get_param_boundaries(_kword)) for _x, _kword in zip(x, kwords)]


def _normalize_value(val, _min, _max):
    """
    Normalize value `val` to value from interval (0, 1) based on `_min` and `_max`.

    :param val: float;
    :param _min: float;
    :param _max: float;
    :return: float;
    """
    return (val - _min) / (_max - _min)


def _normalize(x: List, kwords: List) -> List:
    """
    Normalize values from `x` to value between (0, 1).

    :param x: Iterable[float]; iterable of values in their native form
    :param kwords: Iterable[str]; iterable str of names related to `x`
    :return: List[float];
    """
    return [_normalize_value(_x, *_get_param_boundaries(_kword)) for _x, _kword in zip(x, kwords)]


def _get_param_boundaries(param):
    """
    Return normalization boundaries for given parmeter.

    :param param: str; name of parameter to get boundaries for
    :return: Tuple[float, float];
    """
    return NORMALIZATION_MAP[param]


def _serialize_param_boundaries(x0):
    """
    Serialize boundaries of parameters if exists and parameter is not fixed.

    :param x0: List[Dict[str, Union[float, str, bool]]]; initial parmetres in JSON form
    :return: Dict[str, Tuple[float, float]]
    """
    return {record['param']: (record.get('min', NORMALIZATION_MAP[record['param']]),
                              record.get('max', NORMALIZATION_MAP[record['param']]))
            for record in x0 if not record['fixed']}


def _x0_vectorize(x0) -> Tuple:
    """
    Transform native JSON form of initial parameters to Tuple.
    JSON form::

        [
            {
                'value': 2.0,
                'param': 'p__mass',
                'fixed': False,
                'min': 1.0,
                'max': 3.0
            },
            {
                'value': 4000.0,
                'param': 'p__t_eff',
                'fixed': True,
                'min': 3500.0,
                'max': 4500.0
            },
            ...
        ]

    :param x0: List[Dict[str, Union[float, str, bool]]]; initial parmetres in JSON form
    :return: Tuple;
    """
    _x0 = [record['value'] for record in x0 if not record['fixed']]
    _kwords = [record['param'] for record in x0 if not record['fixed']]
    return _x0, _kwords


def _x0_to_kwargs(x0):
    """
    Transform native JSON input form to `key, value` form::

        {
            key: value,
            ...
        }

    :param x0: List[Dict[str, Union[float, str, bool]]];
    :return: Dict[str, float];
    """
    return {record['param']: record['value'] for record in x0}


def _x0_to_fixed_kwargs(x0):
    """
    Transform native JSON input form to `key, value` form, but select `fixed` parametres only::

        {
            key: value,
            ...
        }

    :param x0: List[Dict[str, Union[float, str, bool]]];
    :return: Dict[str, float];
    """
    return {record['param']: record['value'] for record in x0 if record['fixed']}


def _logger_decorator(suppress_logger=False):
    def do(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not suppress_logger:
                logger.info(f'current xn value: {kwargs}')
            return func(*args, **kwargs)
        return wrapper
    return do


def circular_sync_model_to_fit(x, *args):
    """
    Molde to find minimum.

    :param x: Iterable[float];
    :param args: Tuple;
     :**args*::
        * **xs** * -- numpy.array; phases
        * **ys** * -- numpy.array; supplied fluxes (lets say fluxes from observation) normalized to max value
        * **period** * -- float;
        * **discretization** * -- flaot;
        * **suppress_logger** * -- bool;
        * **passband** * -- Iterable[str];
        * **observer** * -- elisa.observer.observer.Observer;
    :return: float;
    """
    xs, ys, period, kwords, fixed, discretization, suppress_logger, passband, observer = args
    x = _renormalize(x, kwords)
    kwargs = {k: v for k, v in zip(kwords, x)}
    kwargs.update(fixed)
    fn = model.circular_sync_synthetic
    synthetic = _logger_decorator(suppress_logger)(fn)(xs, period, discretization, observer, **kwargs)
    synthetic = analutils.normalize_to_max(synthetic)
    return np.array([np.sum(synthetic[band] - ys[band]) for band in synthetic])


def r_squared(*args, **x):
    """
    Compute R^2 (coefficient of determination).

    :param args: Tuple;
    :**args*::
        * **xs** * -- numpy.array; phases
        * **ys** * -- numpy.array; supplied fluxes (lets say fluxes from observation) normalized to max value
        * **period** * -- float;
        * **passband** * -- Union[str, List[str]];
        * **discretization** * -- flaot;
    :param x: Dict;
    :** x options**: kwargs of current parameters to compute binary system
    :return: float;
    """
    xs, ys, period, passband, discretization = args
    observed_means = np.array([np.repeat(np.mean(ys[band]), len(xs)) for band in ys])
    variability = np.sum([np.sum(np.power(ys[band] - observed_means, 2)) for band in ys])

    observer = Observer(passband=passband, system=None)
    observer._system_cls = BinarySystem
    synthetic = model.circular_sync_synthetic(xs, period, discretization, observer, **x)

    synthetic = analutils.normalize_to_max(synthetic)
    residual = np.sum([np.power(np.sum(synthetic[band] - ys[band]), 2) for band in ys])
    return 1.0 - (residual / variability)


class Fit(object):
    @staticmethod
    def circular_sync(xs, ys, period, x0, passband, discretization, xtol=1e-15, max_nfev=None, suppress_logger=False):
        initial_x0 = copy(x0)
        boundaries = _serialize_param_boundaries(initial_x0)
        update_normalization_map(boundaries)

        fixed = _x0_to_fixed_kwargs(x0)
        x0_vectorized, kwords = _x0_vectorize(x0)
        x0 = _normalize(x0_vectorized, kwords)

        observer = Observer(passband=passband, system=None)
        observer._system_cls = BinarySystem

        args = (xs, ys, period, kwords, fixed, discretization, suppress_logger, passband, observer)

        logger.info("fitting circular synchronous system...")
        result = least_squares(circular_sync_model_to_fit, x0, bounds=(0, 1), args=args, max_nfev=max_nfev, xtol=xtol)
        logger.info("fitting finished")

        result = _renormalize(result.x, kwords)
        result_dict = {k: v for k, v in zip(kwords, result)}
        result_dict.update(_x0_to_fixed_kwargs(initial_x0))

        r_squared_args = xs, ys, period, passband, discretization
        logger.info(f'r_squared: {r_squared(*r_squared_args, **result_dict)}')

        return result_dict


fit = Fit()
