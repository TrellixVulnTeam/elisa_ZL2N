from typing import Dict

import numpy as np

from numpy import ndarray
from elisa.engine import utils, logger
from elisa.engine import const


class Orbit(object):

    MANDATORY_KWARGS = ['period', 'inclination', 'eccentricity', 'argument_of_periastron']
    OPTIONAL_KWARGS = []
    ALL_KWARGS = MANDATORY_KWARGS + OPTIONAL_KWARGS

    def __init__(self, suppress_logger: bool = False, **kwargs) -> None:
        utils.invalid_kwarg_checker(kwargs, Orbit.ALL_KWARGS, Orbit)
        utils.check_missing_kwargs(self.__class__.MANDATORY_KWARGS, kwargs, instance_of=self.__class__)

        self._logger = logger.getLogger(name=self.__class__.__name__, suppress=suppress_logger)

        # default valeus of properties
        self._period: np.float64 = np.nan
        self._inclination: np.float64 = np.nan
        self._eccentricity: np.float64 = np.nan
        self._argument_of_periastron: np.float64 = np.nan
        self._periastron_distance: np.float64 = np.nan
        self._perastron_phase: np.float64 = np.nan
        self._semimajor_axis: np.float64 = np.nan

        # values of properties
        for kwarg in kwargs:
            self._logger.debug(f"setting property {kwarg} "
                               f"of class instance {self.__class__.__name__} to {kwargs[kwarg]}")
            setattr(self, kwarg, kwargs[kwarg])

        self._periastron_distance = self.compute_periastron_distance()
        self._perastron_phase = - self.get_conjuction()["primary_eclipse"]["true_phase"] % 1

    @property
    def semimajor_axis(self) -> np.float64:
        """
        :return:
        """
        return self._semimajor_axis

    @semimajor_axis.setter
    def semimajor_axis(self, semimajor_axis: np.float64):
        """
        :return:
        """
        self._semimajor_axis = semimajor_axis
    
    @property
    def periastron_phase(self) -> np.float64:
        """
        photometric phase of periastron
        :return:
        """
        return self._perastron_phase

    @property
    def period(self) -> np.float64:
        """
        returns orbital period of the binary system in default period unit

        :return: numpy.float
        """
        return self._period

    @period.setter
    def period(self, period: np.float64):
        """
        setter for orbital period of binary system orbit

        :param period: np.float
        :return:
        """
        self._period = period

    @property
    def inclination(self) -> np.float64:
        """
        returns inclination of binary system orbit

        :return: numpy.float
        """
        return self._inclination

    @inclination.setter
    def inclination(self, inclination: np.float64):
        """
        setter for inclination of binary system orbit

        :param inclination: numpy.float
        :return:
        """
        self._inclination = inclination

    @property
    def eccentricity(self) -> np.float64:
        """
        returns eccentricity of binary system orbit

        :return: numpy.float
        """
        return self._eccentricity

    @eccentricity.setter
    def eccentricity(self, eccentricity: np.float64):
        """
        setter for eccentricity of binary system orbit

        :param eccentricity: numpy.float
        :return:
        """
        self._eccentricity = eccentricity

    @property
    def argument_of_periastron(self) -> np.float64:
        """
        returns argument of periastron of binary system orbit

        :return: numpy.float
        """
        return self._argument_of_periastron

    @argument_of_periastron.setter
    def argument_of_periastron(self, argument_of_periastron: np.float64):
        """
        setter for argument of periastron, if unit is not supplied, value in degrees is assumed

        :param argument_of_periastron: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """
        self._argument_of_periastron = argument_of_periastron

    @classmethod
    def true_phase(cls, phase: ndarray, phase_shift: ndarray) -> ndarray:
        """
        returns shifted phase of the orbit by the amount phase_shift

        :param phase: numpy.array
        :param phase_shift: numpy.float
        :return:
        """
        return phase + phase_shift

    @classmethod
    def phase(cls, true_phase, phase_shift):
        """
        reverts the phase shift introduced in function true phase

        :param true_phase: np.array
        :param phase_shift: np.float
        :return:
        """
        return true_phase - phase_shift

    @classmethod
    def phase_to_mean_anomaly(cls, phase: ndarray) -> ndarray:
        """
        returns mean anomaly of points on orbit as a function of phase

        :param phase: numpy.array
        :return: numpy.array
        """
        return const.FULL_ARC * phase

    @classmethod
    def mean_anomaly_to_phase(cls, mean_anomaly):
        """
        returns phase of points on orbit as a function of mean anomaly

        :param mean_anomaly: numpy.array
        :return:
        """
        return mean_anomaly / const.FULL_ARC

    def mean_anomaly_fn(self, eccentric_anomaly: float, *args) -> float:
        """
        definition of Kepler equation for scipy _solver in Orbit.eccentric_anomaly

        :param eccentric_anomaly: numpy.float
        :param args: mean_anomaly: numpy.float
        :return: numpy.float
        """
        mean_anomaly, = args
        return eccentric_anomaly - self.eccentricity * np.sin(eccentric_anomaly) - mean_anomaly

    def mean_anomaly_to_eccentric_anomaly(self, mean_anomaly: float) -> float:
        """
        solves Kepler equation for eccentric anomaly via mean anomaly

        :param mean_anomaly: numpy.float
        :return: numpy.float
        """
        import scipy.optimize
        try:
            solution = scipy.optimize.newton(self.mean_anomaly_fn, 1.0, args=(mean_anomaly, ), tol=1e-10)
            if not np.isnan(solution):
                if solution < 0:
                    solution += const.FULL_ARC
                return solution
            else:
                return False
        except Exception as e:
            self._logger.debug(f"Solver scipy.optimize.newton in function Orbit.eccentric_anomaly did not provide "
                               f"solution.\n Reason: {e}")
            return False

    def eccentric_anomaly_to_mean_anomaly(self, eccentric_anomaly):
        """
        returns mean anomaly as a function of eccentric anomaly calculated using Kepler equation

        :param eccentric_anomaly: np.array
        :return:
        """
        return (eccentric_anomaly - self.eccentricity * np.sin(eccentric_anomaly)) % const.FULL_ARC

    def eccentric_anomaly_to_true_anomaly(self, eccentric_anomaly: ndarray) -> ndarray:
        """
        returns true anomaly as a function of eccentric anomaly and eccentricity

        :param eccentric_anomaly: numpy.array
        :return: numpy.array
        """
        true_anomaly = 2.0 * np.arctan(
            np.sqrt((1.0 + self.eccentricity) / (1.0 - self.eccentricity)) * np.tan(eccentric_anomaly / 2.0))
        true_anomaly[true_anomaly < 0] += const.FULL_ARC
        return true_anomaly

    def true_anomaly_to_eccentric_anomaly(self, true_anomaly):
        """
        returns eccentric anomaly as a function of true anomaly and eccentricity

        :param true_anomaly: numpy.array
        :return:
        """
        eccentric_anomaly = \
            2.0 * np.arctan(np.sqrt((1.0 - self.eccentricity) / (1.0 + self.eccentricity)) * np.tan(true_anomaly / 2.0))
        eccentric_anomaly[eccentric_anomaly < 0] += const.FULL_ARC
        return eccentric_anomaly

    def relative_radius(self, true_anomaly: ndarray) -> ndarray:
        """
        calculates the length of radius vector of elipse where a=1

        :param true_anomaly: numpy.array
        :return: numpy.array
        """
        return (1.0 - self.eccentricity ** 2) / (1.0 + self.eccentricity * np.cos(true_anomaly))

    def true_anomaly_to_azimuth(self, true_anomaly: ndarray) -> ndarray:
        azimut = true_anomaly + self.argument_of_periastron
        azimut %= const.FULL_ARC
        return azimut

    def azimuth_to_true_anomaly(self, azimuth):
        """
        calculates the azimuth form given true anomaly
        :param azimuth: np.array
        :return:
        """
        return (azimuth - self.argument_of_periastron) % const.FULL_ARC

    def orbital_motion(self, phase: ndarray) -> ndarray:
        """
        function takes photometric phase of the binary system as input and calculates positions of the secondary
        component in the frame of reference of primary component

        :param phase: np.array or np.float
        :return: np.array: matrix consisting of column stacked vectors distance, azimut angle, true anomaly and phase
                           np.array((r1, az1, ni1, phs1),
                                    (r2, az2, ni2, phs2),
                                    ...
                                    (rN, azN, niN, phsN))
        """
        # ability to accept scalar as input
        if isinstance(phase, (int, np.int, float, np.float)):
            phase = np.array([np.float(phase)])
        # photometric phase to phase measured from periastron
        true_phase = self.true_phase(phase=phase, phase_shift=self.get_conjuction()['primary_eclipse']['true_phase'])

        mean_anomaly = self.phase_to_mean_anomaly(phase=true_phase)
        eccentric_anomaly = np.array([self.mean_anomaly_to_eccentric_anomaly(mean_anomaly=xx)
                                      for xx in mean_anomaly])
        true_anomaly = self.eccentric_anomaly_to_true_anomaly(eccentric_anomaly=eccentric_anomaly)
        distance = self.relative_radius(true_anomaly=true_anomaly)
        azimut_angle = self.true_anomaly_to_azimuth(true_anomaly=true_anomaly)

        return np.column_stack((distance, azimut_angle, true_anomaly, phase))

    def orbital_motion_from_azimuths(self, azimuth):
        """
        function takes azimuths of the binary system (angle between ascending node (-y) as input and calculates
        positions of the secondary component in the frame of reference of primary component

        :param azimuths: np.array or np.float
        :return: np.array: matrix consisting of column stacked vectors distance, azimut angle, true anomaly and phase
                           np.array((r1, az1, ni1, phs1),
                                    (r2, az2, ni2, phs2),
                                    ...
                                    (rN, azN, niN, phsN))
        """
        true_anomaly = self.azimuth_to_true_anomaly(azimuth)
        distance = self.relative_radius(true_anomaly=true_anomaly)
        eccentric_anomaly = self.true_anomaly_to_eccentric_anomaly(true_anomaly)
        mean_anomaly = self.eccentric_anomaly_to_mean_anomaly(eccentric_anomaly)
        true_phase = self.mean_anomaly_to_phase(mean_anomaly)
        phase = self.phase(true_phase, phase_shift=self.get_conjuction()['primary_eclipse']['true_phase'])
        return np.column_stack((distance, azimuth, true_anomaly, phase))

    def get_conjuction(self) -> Dict:
        """
        compute and return photometric phase of conjunction (eclipses)

        we assume that primary component is situated in center of coo system and observation unit
        vector is [-1, 0, 0]

        return dictionary is in shape {type_of_eclipse: {'true_phase': ,
                                                         'true_anomaly': ,
                                                         'mean_anomaly': ,
                                                         eccentric_anomaly: }, ...}

        :return: dict(dict)
        """
        # determining order of eclipses
        conjuction_arc_list = []
        try:
            if 0 <= self.inclination <= const.PI / 2.0:
                conjuction_arc_list = [const.PI / 2.0, 3.0 * const.PI / 2.0]
            elif const.PI / 2.0 < self.inclination <= const.PI:
                conjuction_arc_list = [3.0 * const.PI / 2.0, const.PI / 2.0]
        except:
            raise TypeError('Invalid type of {0}.inclination.'.format(Orbit.__name__))

        conjunction_quantities = {}
        for alpha, idx in list(zip(conjuction_arc_list, ['primary_eclipse', 'secondary_eclipse'])):
            # true anomaly of conjunction (measured from periastron counter-clokwise)
            true_anomaly_of_conjuction = (alpha - self.argument_of_periastron) % const.FULL_ARC  # \nu_{con}

            # eccentric anomaly of conjunction (measured from apse line)
            eccentric_anomaly_of_conjunction = (2.0 * np.arctan(
                np.sqrt((1.0 - self.eccentricity) / (1.0 + self.eccentricity)) *
                np.tan(true_anomaly_of_conjuction / 2.0))) % const.FULL_ARC

            # mean anomaly of conjunction (measured from apse line)
            mean_anomaly_of_conjunction = (eccentric_anomaly_of_conjunction -
                                           self.eccentricity *
                                           np.sin(eccentric_anomaly_of_conjunction)) % const.FULL_ARC

            # true phase of conjunction (measured from apse line)
            true_phase_of_conjunction = (mean_anomaly_of_conjunction / const.FULL_ARC) % 1.0

            conjunction_quantities[idx] = {}
            conjunction_quantities[idx]["true_anomaly"] = true_anomaly_of_conjuction
            conjunction_quantities[idx]["eccentric_anomaly"] = eccentric_anomaly_of_conjunction
            conjunction_quantities[idx]["mean_anomaly"] = mean_anomaly_of_conjunction
            conjunction_quantities[idx]["true_phase"] = true_phase_of_conjunction

        return conjunction_quantities

    @property
    def periastron_distance(self) -> np.float64:
        """
        return periastron distance

        :return:
        """
        return self._periastron_distance

    def compute_periastron_distance(self) -> float:
        """
        calculates relative periastron distance in SMA units

        :return: float
        """
        periastron_distance = self.relative_radius(true_anomaly=np.array([0])[0])
        self._logger.debug(f"Setting property periastron_distance "
                           f"of class instance {self.__class__.__name__} to {periastron_distance}")
        return periastron_distance
