import numpy as np
import logging
from engine import utils
from astropy import units as u
from engine import units as U

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s : [%(levelname)s] : %(name)s : %(message)s')


class PulsationMode(object):
    """
    pulsation mode data container
    """
    KWARGS = ["l", "m", "amplitude", "frequency", "start_phase"]
    MANDATORY_KWARGS = ["l", "m", "amplitude", "frequency"]

    def __init__(self, **kwargs):
        utils.invalid_kwarg_checker(kwargs=kwargs, kwarglist=PulsationMode.KWARGS, instance=PulsationMode)

        # get logger
        self._logger = logging.getLogger(PulsationMode.__name__)
        self._logger.info("Initialising object {}".format(PulsationMode.__name__))

        self._logger.debug("Setting property components "
                           "of class instance {}".format(PulsationMode.__name__))

        # self._n = None
        self._l = None
        self._m = None
        self._amplitude = None
        self._frequency = None
        self._start_phase = None

        self._logger = logging.getLogger(PulsationMode.__name__)

        self.check_mandatory_kwargs(kwargs)

        missing_kwargs = []
        for key in PulsationMode.MANDATORY_KWARGS:
            if key not in kwargs:
                missing_kwargs.append("`{}`".format(key))
                self._logger.error("Property {} "
                                   "of class instance {} was not initialized".format(key, PulsationMode.__name__))
            else:
                self._logger.debug("Setting property {} "
                                   "of class instance {} to {}".format(key, PulsationMode.__name__, kwargs[key]))
                setattr(self, key, kwargs.get(key))

    # @property
    # def n(self):
    #     """
    #     returns radial degree `n` of pulsation mode
    #     :return: int
    #     """
    #     return self._n
    #
    # @n.setter
    # def n(self, radial_degree):
    #     """
    #     setter for radial degree of pulsation mode
    #     :param radial_degree: int
    #     :return:
    #     """
    #     try:
    #         self._n = np.int(radial_degree)
    #     except ValueError:
    #         raise ValueError('Value for radial degree `n`={0} in pulsation mode class instance {1} is not valid.'
    #                          .format(radial_degree, PulsationMode.__name__))

    @property
    def l(self):
        """
        returns number of surface nodal planes
        :return: int
        """
        return self._l

    @l.setter
    def l(self, surface_nodal_planes):
        """
        setter for number of surface nodal planes
        :param surface_nodal_planes: int
        :return:
        """
        try:
            self._l = np.int(surface_nodal_planes)
        except ValueError:
            raise ValueError('Value for number of surface nodal planes is `l`={0} in pulsation mode class instance {1} '
                             'is not valid.'.format(surface_nodal_planes, PulsationMode.__name__))

    @property
    def m(self):
        """
        returns number of azimutal surface nodal planes for given pulsation mode
        :return:
        """
        return self._m

    @m.setter
    def m(self, azimutal_nodal_planes):
        """
        setter for number of azimutal nodal planes
        :param azimutal_nodal_planes: int
        :return:
        """
        try:
            self._m = np.int(azimutal_nodal_planes)
        except:
            raise ValueError('Value for number of azimutal nodal planes is `m`={0} in pulsation mode class instance '
                             '{1} is not valid.'.format(azimutal_nodal_planes, PulsationMode.__name__))

    @property
    def amplitude(self):
        """
        returns amplitude of pulsation mode in kelvins
        :return: float
        """
        return self._amplitude

    @amplitude.setter
    def amplitude(self, amplitude):
        """
        setter for temperature amplitude of pulsation mode
        :param amplitude: float or astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(amplitude, u.quantity.Quantity):
            self._amplitude = np.float64(amplitude.to(U.TEMPERATURE_UNIT))
        elif isinstance(amplitude, (int, np.int, float, np.float)):
            self._amplitude = np.float64(amplitude)
        else:
            raise TypeError('Value of `amplitude` is not (np.)int or (np.)float nor astropy.unit.quantity.Quantity '
                            'instance.')

    @property
    def frequency(self):
        """
        returns frequency of pulsation mode in default frequency unit
        :return: float
        """
        return self._frequency

    @frequency.setter
    def frequency(self, frequency):
        """
        frequency setter, if unit in astropy format is not given, default frequency unit is assumed

        :param frequency: float or astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(frequency, u.quantity.Quantity):
            self._frequency = np.float64(frequency.to(U.FREQUENCY_UNIT))
        elif isinstance(frequency, (int, np.int, float, np.float)):
            self._frequency = np.float64(frequency)
        else:
            raise TypeError('Value of `frequency` is not (np.)int or (np.)float nor astropy.unit.quantity.Quantity '
                            'instance.')

    @property
    def start_phase(self):
        """
        phase shift of the pulsation mode, basically constant that will be added to time dependent part of the equation.

        :return: float
        """
        return self._start_phase

    @start_phase.setter
    def start_phase(self, phase):
        """
        setter for phase shift of the given pulsation mode,

        :param phase: float
        :return:
        """
        try:
            self._start_phase = np.float(phase) if phase is not None else 0
        except TypeError:
            raise TypeError('Invalid data type {0} for `start_phase` parameter for {1} pulsation mode '
                            'instance.'.format(type(phase), PulsationMode.__name__))

    @staticmethod
    def check_mandatory_kwargs(kwargs):
        keys = list(kwargs.keys())
        diff = list(set(PulsationMode.MANDATORY_KWARGS) - set(keys))

        if diff:
            raise ValueError('Missing mandatory argument(s) {} for spot w/ params {}'.format(', '.join(diff), kwargs))
