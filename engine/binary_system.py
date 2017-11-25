'''
             _,--""--,_
        _,,-"          \
    ,-e"                ;
   (*             \     |
    \o\     __,-"  )    |
     `,_   (((__,-"     L___,,--,,__
        ) ,---\  /\    / -- '' -'-' )
      _/ /     )_||   /---,,___  __/
     """"     """"|_ /         ""
                  """"

 ______ _______ ______ _______ ______
|   __ \       |   __ \    ___|   __ \
|   __ <   -   |   __ <    ___|      <
|______/_______|______/_______|___|__|

    Because of funny Polish video

'''


from engine.system import System
from engine.star import Star
from engine.orbit import Orbit
from astropy import units as u
import numpy as np
import logging
from engine import const as c

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s : [%(levelname)s] : %(name)s : %(message)s')


class BinarySystem(System):

    KWARGS = ['gamma', 'inclination', 'period', 'eccentricity', 'argument_of_periastron', 'primary_minimum_time', 'phase_shift']

    def __init__(self, primary, secondary, name=None, **kwargs):
        self.is_property(kwargs)
        super(BinarySystem, self).__init__(name=name, **kwargs)

        # get logger
        self._logger = logging.getLogger(BinarySystem.__name__)
        self._logger.info("Initialising object {}".format(BinarySystem.__name__))

        # assign components to binary system
        if not isinstance(primary, Star):
            raise TypeError("Primary component is not instance of class {}".format(Star.__name__))

        if not isinstance(secondary, Star):
            raise TypeError("Secondary component is not instance of class {}".format(Star.__name__))

        self._logger.debug("Setting property components "
                           "of class instance {}".format(BinarySystem.__name__))
        self._primary = primary
        self._secondary = secondary

        # physical properties check
        self._mass_ratio = self.secondary.mass / self.primary.mass

        # default values of properties
        self._inclination = None
        self._period = None
        self._eccentricity = None
        self._argument_of_periastron = None
        self._orbit = None
        self._primary_minimum_time = None
        self._phase_shift = None

        # testing if parameters were initialized
        missing_kwargs = []
        for kwarg in BinarySystem.KWARGS:
            if kwarg not in kwargs:
                missing_kwargs.append("`{}`".format(kwarg))
                self._logger.error("Property {} "
                                   "of class instance {} was not initialized".format(kwarg, BinarySystem.__name__))
            else:
                setattr(self, kwarg, kwargs[kwarg])

        if len(missing_kwargs) != 0:
            raise ValueError('Mising argument(s): {} in class instance {}'.format(', '.join(missing_kwargs),
                                                                                  BinarySystem.__name__))

        # orbit initialisation
        self.init_orbit()




    def init(self):
        """
        function to reinitialize BinarySystem class instance after changing parameter(s) of binary system using setters

        :return:
        """
        self.__init__(primary=self.primary, secondary=self.secondary, **self._kwargs_serialize())

    def _kwargs_serialize(self):
        """
        creating dictionary of keyword arguments of BinarySystem class in order to be able to reinitialize the class
        instance in init()

        :return: dict
        """
        serialized_kwargs = {}
        for kwarg in self.KWARGS:
            serialized_kwargs[kwarg] = getattr(self, kwarg)
        return serialized_kwargs

    def init_orbit(self):
        """
        encapsulating orbit class into binary system

        :return:
        """
        self._logger.debug("Re/Initializing orbit in class instance {} ".format(BinarySystem.__name__))
        orbit_kwargs = {key: getattr(self, key) for key in Orbit.KWARGS}
        self._orbit = Orbit(**orbit_kwargs)

    @property
    def mass_ratio(self):
        """
        returns mass ratio m2/m1 of binary system components

        :return: numpy.float
        """
        return self._mass_ratio

    @mass_ratio.setter
    def mass_ratio(self, value):
        """
        disabled setter for binary system mass ratio

        :param value:
        :return:
        """
        raise Exception("Property ``mass_ratio`` is read-only.")

    @property
    def primary(self):
        """
        encapsulation of primary component into binary system

        :return: class Star
        """
        return self._primary

    @property
    def secondary(self):
        """
        encapsulation of secondary component into binary system

        :return: class Star
        """
        return self._secondary

    @property
    def orbit(self):
        """
        encapsulation of orbit class into binary system

        :return: class Orbit
        """
        return self._orbit

    @property
    def period(self):
        """
        returns orbital period of binary system

        :return: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        """
        return self._period

    @period.setter
    def period(self, period):
        """
        set orbital period of bonary star system, if unit is not specified, default unit is assumed

        :param period: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(period, u.quantity.Quantity):
            self._period = np.float64(period.to(self.get_period_unit()))
        elif isinstance(period, (int, np.int, float, np.float)):
            self._period = np.float64(period)
        else:
            raise TypeError('Input of variable `period` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance.')
        self._logger.debug("Setting property period "
                           "of class instance {} to {}".format(BinarySystem.__name__, self._period))

    @property
    def inclination(self):
        """
        inclination of binary star system

        :return: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        """
        return self._inclination

    @inclination.setter
    def inclination(self, inclination):
        """
        set orbit inclination of binary star system, if unit is not specified, default unit is assumed

        :param inclination: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """

        if isinstance(inclination, u.quantity.Quantity):
            self._inclination = np.float64(inclination.to(self.get_arc_unit()))
        elif isinstance(inclination, (int, np.int, float, np.float)):
            self._inclination = np.float64(inclination)
        else:
            raise TypeError('Input of variable `inclination` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance.')

        if not 0 <= self.inclination <= c.PI:
            raise ValueError('Eccentricity value of {} is out of bounds (0, pi).'.format(self.inclination))

        self._logger.debug("Setting property inclination "
                           "of class instance {} to {}".format(BinarySystem.__name__, self._inclination))

    @property
    def eccentricity(self):
        """
        eccentricity of orbit of binary star system

        :return: (np.)int, (np.)float
        """
        return self._eccentricity

    @eccentricity.setter
    def eccentricity(self, eccentricity):
        """
        set eccentricity

        :param eccentricity: (np.)int, (np.)float
        :return:
        """
        if eccentricity < 0 or eccentricity > 1 or not isinstance(eccentricity, (int, np.int, float, np.float)):
            raise TypeError('Input of variable `eccentricity` is not (np.)int or (np.)float or it is out of boundaries.')
        self._eccentricity = eccentricity
        self._logger.debug("Setting property eccentricity "
                           "of class instance {} to {}".format(BinarySystem.__name__, self._eccentricity))

    @property
    def argument_of_periastron(self):
        """
        argument of periastron

        :return: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        """
        return self._argument_of_periastron

    @argument_of_periastron.setter
    def argument_of_periastron(self, argument_of_periastron):
        """
        setter for argument of periastron

        :param argument_of_periastron: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(argument_of_periastron, u.quantity.Quantity):
            self._argument_of_periastron = np.float64(argument_of_periastron.to(self.get_arc_unit()))
        elif isinstance(argument_of_periastron, (int, np.int, float, np.float)):
            self._argument_of_periastron = np.float64(argument_of_periastron)
        else:
            raise TypeError('Input of variable `periastron` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance.')

    @property
    def primary_minimum_time(self):
        """
        returns time of primary minimum in default period unit

        :return: numpy.float
        """
        return self._primary_minimum_time

    @primary_minimum_time.setter
    def primary_minimum_time(self, primary_minimum_time):
        """
        setter for time of primary minima

        :param primary_minimum_time: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(primary_minimum_time, u.quantity.Quantity):
            self._primary_minimum_time = np.float64(primary_minimum_time.to(self.get_period_unit()))
        elif isinstance(primary_minimum_time, (int, np.int, float, np.float)):
            self._primary_minimum_time = np.float64(primary_minimum_time)
        else:
            raise TypeError('Input of variable `primary_minimum_time` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance.')
        self._logger.debug("Setting property primary_minimum_time "
                           "of class instance {} to {}".format(BinarySystem.__name__, self._primary_minimum_time))

    @property
    def phase_shift(self):
        """
        returns phase shift of the primary eclipse minimum with respect to ephemeris
        true_phase is used during calculations, where: true_phase = phase + phase_shift

        :return: numpy.float
        """
        return self._phase_shift

    @phase_shift.setter
    def phase_shift(self, phase_shift):
        """
        setter for phase shift of the primary eclipse minimum with respect to ephemeris
        this will cause usage of true_phase during calculations, where: true_phase = phase + phase_shift

        :param phase_shift: numpy.float
        :return:
        """
        self._phase_shift = phase_shift
        self._logger.debug("Setting property phase_shift "
                           "of class instance {} to {}".format(BinarySystem.__name__, self._phase_shift))

    def compute_lc(self):
        pass

    def get_info(self):
        pass

    @classmethod
    def is_property(cls, kwargs):
        """
        method for checking if keyword arguments are valid properties of this class

        :param kwargs: dict
        :return:
        """
        is_not = ['`{}`'.format(k) for k in kwargs if k not in cls.KWARGS]
        if is_not:
            raise AttributeError('Arguments {} are not valid {} properties.'.format(', '.join(is_not), cls.__name__))

    def primary_potential_derivative_x(self, x, *args):
        """
        derivative of potential function perspective of primary component

        :param x: (np.)float
        :param args: tuple ((np.)float, (np.)float); (components distance, synchronicity of primary component)
        :return:
        """
        d, synchronicity = args
        r_sqr, rw_sqr = x ** 2, (d - x) ** 2
        return - (x / r_sqr ** (3.0 / 2.0)) + (
            (self.mass_ratio * (d - x)) / rw_sqr ** (3.0 / 2.0)) + synchronicity ** 2 * (
            self.mass_ratio + 1) * x - self.mass_ratio / d ** 2

    def secondary_potential_derivative_x(self, x, *args):
        """
        derivative of potential function perspective of secondary component

        :param x: (np.)float
        :param args: tuple ((np.)float, (np.)float); (components distance, synchronicity of secondary component)
        :return:
        """
        d, synchronicity = args
        r_sqr, rw_sqr = x ** 2, (d - x) ** 2
        return - (x / r_sqr ** (3.0 / 2.0)) + (
            (self.mass_ratio * (d - x)) / rw_sqr ** (3.0 / 2.0)) - synchronicity ** 2 * (
            self.mass_ratio + 1) * (1 - x) + (1.0 / d ** 2)
