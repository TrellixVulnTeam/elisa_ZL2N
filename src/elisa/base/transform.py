import numpy as np

from .. import (
    units as u,
    const,
    settings
)
from .. units import (
    DefaultStarInputUnits,
    DefaultBinarySystemInputUnits,
    DefaultSystemInputUnits,
    DefaultSystemUnits
)

WHEN_FLOAT64 = (int, np.int, np.int32, np.int64, float, np.float, np.float32, np.float64)
WHEN_ARRAY = (list, np.ndarray, tuple)


def quantity_transform(value, unit, when_float64=WHEN_FLOAT64, default_input_unit=None):
    """
    General transform function for quantities which fit such interface.

    :param value: Union[(numpy.)float, (numpy.)int, astropy.units.quantity.Quantity, str]; string accepts the string
                                                                                           representation of the astropy
                                                                                           units
    :param unit: astropy.units.Quantity; unit of the output
    :param when_float64: Tuple(Types)
    :param default_input_unit: astropy.units.Unit; assumed unit of input it unit is not supplied in `value`
    :return: float
    """
    if isinstance(value, (u.Quantity, str)):
        value = u.Quantity(value) if isinstance(value, str) else value
        value = np.float64(value.to(unit))
    elif isinstance(value, when_float64):
        value = np.float64(value) if default_input_unit is None \
            else (value * default_input_unit).to(unit).value
    else:
        raise TypeError('Input of variable is not (numpy.)int or (numpy.)float '
                        'nor astropy.unit.quantity.Quantity instance (or its string representation).')
    return value


def deg_transform(value, unit, when_float64, default_input_unit=u.deg):
    """
    General transform function for angular quantities which fit such interface.

    :param value: Union[(numpy.)float, (numpy.)int, astropy.units.quantity.Quantity, str]; string accepts the string
                                                                                           representation of the astropy
                                                                                           units
    :param unit: astropy.units.Quantity; unit of the output
    :param when_float64:
    :param default_input_unit: astropy.units.Unit; assumed unit of input it unit is not supplied in `value`
    :return: float;
    """
    if isinstance(value, (u.Quantity, str)):
        value = u.Quantity(value) if isinstance(value, str) else value
        value = np.float64(value.to(unit))
    elif isinstance(value, when_float64):
        value = np.float64(value)*default_input_unit.to(unit)
    else:
        raise TypeError('Input of the angular variable is not (numpy.)int or (numpy.)float '
                        'nor astropy.unit.quantity.Quantity instance (or its string representation).')
    return value


class TransformProperties(object):
    @classmethod
    def transform_input(cls, **kwargs):
        """
        Function transforms input dictionary of keyword arguments of the System to internally usable state
        (conversion and stripping of units).

        :param kwargs: Dict;
        :return: Dict;
        """
        return {key: getattr(cls, key)(val) if hasattr(cls, key) else val for key, val in kwargs.items()}


class SystemProperties(TransformProperties):

    @staticmethod
    def inclination(value):
        """
        Transform and validity check for inclination of the system.
        If unit is not supplied, value in degrees is assumed.

        :param value: Union[(numpy.)float, (numpy.)int, astropy.units.quantity.Quantity, str]
        :return:
        """
        if isinstance(value, (u.Quantity, str)):
            value = u.Quantity(value) if isinstance(value, str) else value
            value = np.float64(value.to(u.DefaultSystemUnits.inclination))
        elif isinstance(value, (int, np.int, float, np.float)):
            value = np.float64((value * DefaultSystemInputUnits.inclination).to(DefaultSystemUnits.inclination))
        else:
            raise TypeError('Input of variable `inclination` is not (numpy.)int or (numpy.)float '
                            'nor astropy.unit.quantity.Quantity instance (or its string representation).')

        if not 0 <= value <= const.PI:
            raise ValueError(f'Inclination value of {value} is out of bounds (0, pi).')
        return value

    @staticmethod
    def period(value):
        """
        Transform and validate orbital period of binary star system.
        If unit is not specified, default period unit is assumed.

        :param value: Union[(numpy.)float, (numpy.)int, astropy.units.quantity.Quantity]
        :return: float
        """
        return quantity_transform(value, DefaultSystemUnits.period, WHEN_FLOAT64, u.DefaultSystemInputUnits.period)

    @staticmethod
    def gamma(value):
        """
        Validate and transform center of mass velocity.
        Expected type is astropy.units.quantity.Quantity, numpy.float or numpy.int othervise TypeError will be raised.
        If unit is not specified, default velocity unit is assumed.

        :param value: Union[(numpy.)float, (numpy.)int, astropy.units.quantity.Quantity]
        :return:
        """
        return quantity_transform(value, u.DefaultSystemUnits.gamma, WHEN_FLOAT64, u.DefaultSystemInputUnits.gamma)

    @staticmethod
    def additional_light(value):
        """
        Validate and transform for additional light - light that does not originate from any member of system.

        :param value: float (0, 1)
        :return:
        """
        if not 0.0 <= value <= 1.0:
            raise ValueError('Invalid value of additional light. Valid values are between 0 and 1.')
        return np.float64(value)

    @staticmethod
    def semi_major_axis(value):
        """
        Validate and transform for semi major axis.

        :param value:
        :return:
        """
        if isinstance(value, (u.Quantity, str)):
            value = u.Quantity(value) if isinstance(value, str) else value
            value = np.float64(value.to(u.DefaultBinarySystemUnits.system.semi_major_axis))
        elif isinstance(value, WHEN_FLOAT64):
            value = np.float64(value * DefaultBinarySystemInputUnits.system.semi_major_axis.
                               to(u.DefaultBinarySystemUnits.system.semi_major_axis))
        else:
            raise TypeError('User input is not (numpy.)int or (numpy.)float '
                            'nor astropy.unit.quantity.Quantity instance (or its string representation).')
        if value <= 0:
            raise ValueError("Invalid value of semi_major_axis, use value > 0!")
        return value

    @staticmethod
    def distance(value):
        if isinstance(value, (u.Quantity, str)):
            value = u.Quantity(value) if isinstance(value, str) else value
            value = np.float64(value.to(u.DefaultSystemUnits.distance))
        elif isinstance(value, WHEN_FLOAT64):
            value = np.float64(value * DefaultBinarySystemInputUnits.system.distance.to(u.DefaultSystemUnits.distance))
        else:
            raise TypeError('User input is not (numpy.)int or (numpy.)float '
                            'nor astropy.unit.quantity.Quantity instance (or its string representation).')
        if value <= 0:
            raise ValueError("Invalid value of system`s distance, use value > 0!")

        return value


class BodyProperties(TransformProperties):
    @staticmethod
    def synchronicity(value):
        """
        Object synchronicity (F = omega_rot/omega_orb) validator.
        Expects number input convertible to numpy float64 / float.

        :param value: float
        """
        if value <= 0:
            raise ValueError("Invalid synchronicity, use value > 0!")
        return np.float64(value)

    @staticmethod
    def albedo(value):
        """
        Validate and transform bolometric albedo (reradiated energy/ irradiance energy).
        Accepts value of albedo in range (0, 1).

        :param value: float;
        :return: float;
        """
        if value < 0 or value > 1:
            raise ValueError(f'Parameter albedo = {value} is out of range <0, 1>')
        return np.float64(value)

    @staticmethod
    def discretization_factor(value):
        """
        Discretization factor. Degrees is considered as default value.

        :param value: Union[float, astropy.quantity.Quantity]
        :return: float
        """
        value = deg_transform(value, u.DefaultStarUnits.discretization_factor, WHEN_FLOAT64,
                              u.DefaultStarInputUnits.discretization_factor)
        if value > const.HALF_PI:
            raise ValueError("Invalid value of alpha parameter. Use value less than 90.")
        return value

    @staticmethod
    def t_eff(value):
        """
        This function accepts value in Any temperature unit.
        If your input is without unit, function assumes that supplied value is in Kelvins.

        :param value: Union[int, numpy.int, float, numpy.float, astropy.unit.quantity.Quantity]
        :return: float
        """
        return quantity_transform(value, u.DefaultStarUnits.t_eff, WHEN_FLOAT64, u.DefaultStarInputUnits.t_eff)


class StarProperties(BodyProperties):
    @staticmethod
    def equivalent_radius(value):
        """
        Expected type is astropy.units.quantity.Quantity, numpy.float or numpy.int othervise TypeError will be raised.
        If quantity is not specified, default distance unit is assumed.

        :param value: float
        :return:
        """
        if isinstance(value, (u.Quantity, str)):
            value = u.Quantity(value) if isinstance(value, str) else value
            value = np.float64(value.to(u.DefaultStarUnits.equivalent_radius))
        elif isinstance(value, WHEN_FLOAT64):
            value = np.float64(value * DefaultStarInputUnits.equivalent_radius.to(u.DefaultStarUnits.equivalent_radius))
        else:
            raise TypeError('User input is not (numpy.)int or (numpy.)float '
                            'nor astropy.unit.quantity.Quantity instance (or its string representation).')
        if value <= 0:
            raise ValueError("Invalid value of equivalent_radius, use value > 0!")
        return value

    @staticmethod
    def mass(value):
        """
       If mass is int, np.int, float, np.float, program assumes solar mass as it's unit.
       If mass astropy.unit.quantity.Quantity instance, program converts it to default units and stores it's value in
       attribute _mass.

       :param value: Union[int, numpy.int, float, numpy.float, astropy.unit.quantity.Quantity, str];
       :return: float
       """
        if isinstance(value, (u.Quantity, str)):
            value = u.Quantity(value) if isinstance(value, str) else value
            value = np.float64(value.to(u.DefaultStarUnits.mass))
        elif isinstance(value, WHEN_FLOAT64):
            value = np.float64(value * DefaultStarInputUnits.mass.to(u.DefaultStarUnits.mass))
        else:
            raise TypeError('User input is not (numpy.)int or (numpy.)float '
                            'nor astropy.unit.quantity.Quantity instance (or its string representation).')
        if value <= 0:
            raise ValueError("Invalid mass, use value > 0!")
        return value

    @staticmethod
    def surface_potential(value):
        """
        Returns surface potential of Star.

        :param value: float
        :return: float
        """
        if value < 0:
            raise ValueError("Invalid surface potential, use value > 0!")
        return np.float64(value)

    @staticmethod
    def metallicity(value):
        if not isinstance(value, WHEN_FLOAT64):
            raise TypeError('Input of variable `metallicity` is not (np.)int or (np.)float instance.')
        return np.float64(value)

    @staticmethod
    def polar_log_g(value):
        """
        Setter for polar surface gravity.
        If unit is not specified in astropy.units format, value in cgs unit is assumed (it means log(g) in cgs).

        :param value: float or astropy.unit.quantity.Quantity
        :return: float
        """
        if isinstance(value, (u.Quantity, str)):
            value = u.Dex(value, unit=u.Unit(' '.join(value.split()[1:]))) if isinstance(value, str) else value
            value = np.float64(value.to(u.LOG_ACCELERATION_UNIT))
        elif isinstance(value, WHEN_FLOAT64):
            # conversion from cgs to SI
            value -= 2
        else:
            raise TypeError('User input is not (numpy.)int or (numpy.)float '
                            'nor astropy.unit.quantity.Quantity instance (or its string representation).')
        return value

    @staticmethod
    def gravity_darkening(value):
        """
        Gravity darkening validator.

        :param value: float;
        :return: float
        """
        if value > 1 or value < 0:
            raise ValueError(f'Parameter gravity darkening = {value} is out of range <0, 1>')
        return np.float64(value)

    @staticmethod
    def limb_darkening_coefficients(value):
        """
        Validates custom limb darkening coefficients.

        :param value: Union[none, dict];
        :return: Union[none, dict];
        """
        if value is None:
            retval = None  # default case of interpolated LD coefficients
        elif isinstance(value, dict):
            retval = dict()
            for passband, ld_coeffs in value.items():
                if isinstance(ld_coeffs, WHEN_FLOAT64):
                    if settings.LIMB_DARKENING_LAW in ['linear', 'cosine']:
                        retval[passband] = [ld_coeffs, ]
                    else:
                        raise TypeError('Scalar limb darkening coefficient is available only for linear (cosine) law.')
                elif isinstance(ld_coeffs, WHEN_ARRAY):
                    desired_vector_length = len(settings.LD_LAW_CFS_COLUMNS[settings.LIMB_DARKENING_LAW])
                    if np.shape(ld_coeffs)[0] != desired_vector_length:
                        raise ValueError(f'{settings.LIMB_DARKENING_LAW} limb-darkening law requires '
                                         f'{desired_vector_length} components in a vector with shape '
                                         f'({desired_vector_length}, ), however, you provided a vector with '
                                         f'{len(ld_coeffs)} components with shape {np.shape(ld_coeffs)}')
                    else:
                        retval[passband] = ld_coeffs
        else:
            raise TypeError('Limb darkening coefficients needs to be supplied as dictionary in format '
                            '{`passband`: ld_coeffs, }, where `ld_coeffs` is float (for linear law) '
                            'and/or list (numpy.array) in other cases.')

        return retval


class SpotProperties(BodyProperties):
    @staticmethod
    def latitude(value):
        """
        Expecting value in degrees or as astropy units instance.

        :param value: Union[(numpy.)float, (numpy.)int, astropy.units.quantity.Quantity]
        :return: float
        """
        return deg_transform(value, u.DefaultSpotUnits.latitude, WHEN_FLOAT64, u.DefaultSpotInputUnits.latitude)

    @staticmethod
    def longitude(value):
        """
        Expecting value in degrees or as astropy units instance.

        :param value: Union[(numpy.)float, (numpy.)int, astropy.units.quantity.Quantity]
        :return: float
        """
        return deg_transform(value, u.DefaultSpotUnits.longitude, WHEN_FLOAT64, u.DefaultSpotInputUnits.longitude)

    @staticmethod
    def angular_radius(value):
        """
        Expecting value in degrees or as astropy units instance.

        :param value: Union[(numpy.)float, (numpy.)int, astropy.units.quantity.Quantity]
        :return:
        """
        return deg_transform(value, u.DefaultSpotUnits.angular_radius, WHEN_FLOAT64,
                             u.DefaultSpotInputUnits.angular_radius)

    @staticmethod
    def temperature_factor(value):
        """
        Validate and transform temperature factor.

        :param value: flaot
        :return: float
        """
        if not isinstance(value, (int, np.int, float, np.float)):
            raise TypeError('Input of variable `temperature_factor` is not (numpy.)int or (numpy.)float.')
        return np.float64(value)

    @staticmethod
    def discretization_factor(value):
        """
        Discretization factor. Degrees is considered as default value.

        :param value: Union[float, astropy.quantity.Quantity]
        :return: float
        """
        value = deg_transform(value, u.DefaultSpotUnits.discretization_factor, WHEN_FLOAT64,
                              u.DefaultSpotInputUnits.discretization_factor)
        if value > const.HALF_PI:
            raise ValueError("Invalid value of alpha parameter. Use value less than 90.")
        return value
