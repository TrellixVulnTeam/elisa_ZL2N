import json
from ...logger import getLogger
from copy import copy
import numpy as np

from ... import utils
from elisa.analytics.binary.least_squares import central_rv as lstsqr_central_rv
from elisa.analytics.binary.mcmc import central_rv as mcmc_central_rv
from elisa.analytics.binary_fit.plot import RVPlot
from elisa.analytics import utils as autils
from elisa.analytics.binary_fit import shared

logger = getLogger('analytics.binary_fit.rv_fit')


class RVFit(object):
    MANDATORY_KWARGS = ['radial_velocities', ]
    OPTIONAL_KWARGS = []
    ALL_KWARGS = MANDATORY_KWARGS + OPTIONAL_KWARGS

    PARAMS_DISTRIBUTION = {
        'MANDATORY_TYPES': ['system'],
        'OPTIONAL_TYPES': ['primary', 'secondary'],

        'MANDATORY_SYSTEM_PARAMS': ['eccentricity', 'argument_of_periastron', 'gamma'],
        'OPTIONAL_SYSTEM_PARAMS': ['period', 'primary_minimum_time', 'inclination', 'asini', 'mass_ratio'],

        'MANDATORY_STAR_PARAMS': [],
        'OPTIONAL_STAR_PARAMS': ['mass', 'synchronicity', 'metallicity', 't_eff', 'surface_potential',
                                 'gravity_darkening', 'albedo', 'spots', 'pulsations', 'spots', 'pulsations'],

        'MANDATORY_SPOT_PARAMS': shared.MANDATORY_SPOT_PARAMS,
        'OPTIONAL_SPOT_PARAMS': shared.OPTIONAL_SPOT_PARAMS,

        'MANDATORY_PULSATION_PARAMS': shared.MANDATORY_PULSATION_PARAMS,
        'OPTIONAL_PULSATION_PARAMS': shared.OPTIONAL_PULSATION_PARAMS,
    }

    PARAMS_DISTRIBUTION.update({
        'ALL_TYPES': PARAMS_DISTRIBUTION['MANDATORY_TYPES'] + PARAMS_DISTRIBUTION['OPTIONAL_TYPES'],
        'ALL_SYSTEM_PARAMS': PARAMS_DISTRIBUTION['MANDATORY_SYSTEM_PARAMS'] +
                             PARAMS_DISTRIBUTION['OPTIONAL_SYSTEM_PARAMS'],
        'ALL_STAR_PARAMS': PARAMS_DISTRIBUTION['MANDATORY_STAR_PARAMS'] + PARAMS_DISTRIBUTION['OPTIONAL_STAR_PARAMS'],
        'ALL_SPOT_PARAMS': PARAMS_DISTRIBUTION['MANDATORY_SPOT_PARAMS'] + PARAMS_DISTRIBUTION['OPTIONAL_SPOT_PARAMS'],
        'ALL_PULSATION_PARAMS': PARAMS_DISTRIBUTION['MANDATORY_PULSATION_PARAMS'] +
                                PARAMS_DISTRIBUTION['OPTIONAL_PULSATION_PARAMS'],
    })

    FIT_PARAMS_COMBINATIONS = {
        'standard': {
            'system': ['inclination', 'period', 'primary_minimum_time'] +
                      PARAMS_DISTRIBUTION['MANDATORY_SYSTEM_PARAMS'],
            'star': ['mass', 'synchronicity', 'metallicity', 't_eff', 'surface_potential', 'gravity_darkening',
                     'albedo', 'spots', 'pulsations'] + PARAMS_DISTRIBUTION['MANDATORY_STAR_PARAMS'],
            'spots': PARAMS_DISTRIBUTION['ALL_SPOT_PARAMS'],
            'pulsations': PARAMS_DISTRIBUTION['ALL_PULSATION_PARAMS']
        },
        'community': {
            'system': ['asini', 'mass_ratio', 'period', 'primary_minimum_time'] +
                      PARAMS_DISTRIBUTION['MANDATORY_SYSTEM_PARAMS'],
            'star': ['synchronicity', 'metallicity', 't_eff', 'surface_potential', 'gravity_darkening', 'albedo',
                     'spots', 'pulsations'] + PARAMS_DISTRIBUTION['MANDATORY_STAR_PARAMS'],
            'spots': PARAMS_DISTRIBUTION['ALL_SPOT_PARAMS'],
            'pulsations': PARAMS_DISTRIBUTION['ALL_PULSATION_PARAMS']
        }
    }

    def __init__(self, **kwargs):
        utils.invalid_kwarg_checker(kwargs, RVFit.ALL_KWARGS, RVFit)
        utils.check_missing_kwargs(self.__class__.MANDATORY_KWARGS, kwargs, instance_of=self.__class__)

        self.radial_velocities = None
        self.fit_params = None
        self.ranges = None
        self.period = None

        # MCMC specific variables
        self.flat_chain = None
        self.flat_chain_path = None
        self.normalization = None
        self.variable_labels = None

        self.plot = RVPlot(self)

        # values of properties
        logger.debug(f"setting properties of RVFit")
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    def fit(self, x0, method='least_squares', **kwargs):
        """
        Function encapsulates various fitting functions for fitting radial velocities.
        
        :param x0: Dict; starting values of the fit
        :param method: string;
        :param kwargs: dict; method-dependent
        :**kwargs options for least_squares**: passes arguments of scipy.optimize.least_squares method except
                                               `fun`, `x0` and `bounds`
        :**kwargs options for mcmc**:
            * ** nwalkers (int) ** * - The number of walkers in the ensemble. Minimum is 2 * number of free parameters.
            * ** nsteps (int) ** * - The number of steps to run. Default is 1000.
            * ** initial_state (numpy.ndarray) ** * - The initial state or position vector made of free parameters with
                    shape (nwalkers, number of free parameters). The order of the parameters is specified by their order
                    in `x0`. Be aware that initial states should be supplied in normalized form (0, 1). For example, 0
                    means value of the parameter at `min` and 1.0 at `max` value in `x0`. By default, they are generated
                    randomly uniform distribution.
            * ** burn_in ** * - The number of steps to run to achieve equilibrium where useful sampling can start.
                    Default value is nsteps / 10.
            * ** percentiles ** * - List of percentiles used to create error results and confidence interval from MCMC
                    chain. Default value is [16, 50, 84] (1-sigma confidence interval)
        :return: dict; fit_params
        """
        # checking that input dictionary has correct format and does not contain invalid values
        shared.check_initial_param_validity(x0, RVFit.PARAMS_DISTRIBUTION)

        # treating a lack of `value` key in constrained parameters
        x0 = autils.prep_constrained_params(x0)

        # transforming initial parameters to base units
        x0 = autils.transform_initial_values(x0)

        x_data, y_data, yerr = dict(), dict(), dict()
        for component, data in self.radial_velocities.items():
            x_data[component] = data.x_data
            y_data[component] = data.y_data
            yerr[component] = data.yerr

        if str(method).lower() == 'least_squares':
            self.fit_params = lstsqr_central_rv.fit(xs=x_data, ys=y_data, x0=x0, yerr=yerr, **kwargs)

        elif str(method).lower() in ['mcmc']:
            self.fit_params = mcmc_central_rv.fit(xs=x_data, ys=y_data, x0=x0, yerr=yerr, **kwargs)
            self.flat_chain = mcmc_central_rv.last_sampler.get_chain(flat=True)
            self.flat_chain_path = mcmc_central_rv.last_fname
            self.normalization = mcmc_central_rv.last_normalization
            self.variable_labels = mcmc_central_rv.labels

        logger.info('Fitting and processing of results finished successfully.')
        self.fit_summary()
        return self.fit_params

    def load_chain(self, filename, discard=0):
        """
        Function loads MCMC chain along with auxiliary data from json file created after each MCMC run.

        :param discard: int; Discard the first discard steps in the chain as burn-in. (default: 0)
        :param filename: str; full name of the json file
        :return: Tuple[numpy.ndarray, list, Dict]; flattened mcmc chain, labels of variables in `flat_chain` columns,
                                                  {var_name: (min_boundary, max_boundary), ...} dictionary of
                                                  boundaries defined by user for each variable needed
                                                  to reconstruct real values from normalized `flat_chain` array
        """
        return shared.load_mcmc_chain(self, filename, discard=discard)

    def store_parameters(self, parameters=None, filename=None):
        """
        Function converts model parameters to json compatibile format and stores model parameters.

        :param parameters: Dict; {'name': {'value': numpy.ndarray, 'unit': Union[astropy.unit, str], ...}, ...}
        :param filename: str;
        :return:
        """
        parameters = copy(self.fit_params) if parameters is None else parameters

        parameters = autils.unify_unit_string_representation(parameters)

        with open(filename, 'w') as f:
            json.dump(parameters, f, separators=(',\n', ': '))

    def load_parameters(self, filename=None):
        with open(filename, 'r') as f:
            prms = json.load(f)

        self.period = prms['system']['period']['value']
        self.fit_params = prms

        return prms

    def fit_summary(self, filename=None):
        """
        Producing a summary of the fit in more human readable form.

        :param filename: Union[str, None]; if not None, summary is stored in file, otherwise it is printed into console
        :return:
        """
        if filename is not None:
            f = open(filename, 'w')
            write_fn = f.write
            line_sep = '\n'
        else:
            write_fn = print
            line_sep = ''

        shared.write_ln(write_fn, '# Parameter', 'value', '-1 sigma', '+1 sigma', 'unit', 'status', line_sep)
        write_fn(f"#{'-'*123}{line_sep}")
        if 'mass_ratio' in self.fit_params['system'].keys():
            shared.write_param_ln(self.fit_params['system'], 'mass_ratio', 'Mass ratio (q=M_2/M_1):', write_fn, line_sep, 3)
            shared.write_param_ln(self.fit_params['system'], 'asini', 'a*sin(i):', write_fn, line_sep, 2)
        else:
            shared.write_param_ln(self.fit_params['primary'], 'mass', 'Primary mass:', write_fn, line_sep, 3)
            shared.write_param_ln(self.fit_params['secondary'], 'mass', 'Secondary mass:', write_fn, line_sep, 3)
            shared.write_param_ln(self.fit_params['system'], 'inclination', 'Inclination(i):', write_fn, line_sep, 3)
        shared.write_param_ln(self.fit_params['system'], 'eccentricity', 'Eccentricity (e):', write_fn, line_sep)
        shared.write_param_ln(self.fit_params['system'], 'argument_of_periastron', 'Argument of periastron (omega):', write_fn,
                              line_sep)
        shared.write_param_ln(self.fit_params['system'], 'gamma', 'Centre of mass velocity (gamma):', write_fn, line_sep)
        shared.write_param_ln(self.fit_params['system'], 'period', 'Orbital period (P):', write_fn, line_sep)
        if 'primary_minimum_time' in self.fit_params['system'].keys():
            shared.write_param_ln(self.fit_params['system'], 'primary_minimum_time', 'Time of primary minimum (T0):', write_fn,
                                  line_sep)

        if self.fit_params['system']['r_squared']['value'] is not None:
            shared.write_param_ln(self.fit_params['system'], 'r_squared', 'Fit R^2: ', write_fn, line_sep, 4)

        if filename is not None:
            f.close()
