from copy import copy
from astropy import units as u

from elisa.analytics.binary import params
from elisa.logger import getPersistentLogger


logger = getPersistentLogger('analytics.utils')


def convert_dict_to_json_format(dictionary):
    """
    Converts initial vector to JSON compatibile format.

    :param dictionary: Dict; vector of initial parameters

    ::

    :return: List; [{param: paramname, value: value, ...}, ...]
    """
    return dictionary


def convert_json_to_dict_format(json):
    """
    Converts initial vector to JSON compatibile format.

    :param json: List; vector of initial parameters {paramname:{value: value, min: ...}, ...}
    :return: List; [{param: paramname, value: value, ...}, ...]
    """
    retval = dict()
    for item in json:
        param = item.pop('param')
        retval.update({param: item, })
    return retval


def transform_initial_values(x0):
    """
    Transforms initial vector to base units.

    :param x0: Dict; initial vector, {param_name: {value: value, unit: astropy.unit...}, ...}
    :return: Dict;
    """
    def transform_variable(key, item):
        if 'unit' in item.keys() and 'value' in item.keys():
            if item['value'] is None:
                return
            item['unit'] = u.Unit(item['unit']) if isinstance(item['unit'], str) else item['unit']
            if 'value' in item.keys():
                item['value'] = (item['value'] * item['unit']).to(
                    params.PARAMS_UNITS_MAP[key]).value
            if 'min' in item.keys():
                item['min'] = (item['min'] * item['unit']).to(params.PARAMS_UNITS_MAP[key]).value
            if 'max' in item.keys():
                item['max'] = (item['max'] * item['unit']).to(params.PARAMS_UNITS_MAP[key]).value
            item['unit'] = params.PARAMS_UNITS_MAP[key]

    for param_type in x0.values():
        for system_key, system_val in param_type.items():
            if system_key in params.COMPOSITE_PARAMS:  # testing if item are spots or pulsations
                for composite_item in system_val.values():  # particular spot or pulsation mode
                    # iterating over params of the spot or pulsation mode
                    for composite_item_key, composite_item_val in composite_item.items():
                        transform_variable(composite_item_key, composite_item_val)

            transform_variable(system_key, system_val)
    return x0


def unify_unit_string_representation(dictionary):
    """
    transform user units to unified format

    :param dictionary: dict; model parameter
    :return: dict; model parameter
    """
    for type_name, param_type in dictionary.items():
        for key, val in param_type.items():
            if 'unit' in val.keys():
                val['unit'] = u.Unit(val['unit']) if isinstance(val['unit'], str) else val['unit']
                val['unit'] = val['unit'].to_string()

        composite_params = {key: val for key, val in param_type.items() if key in params.COMPOSITE_PARAMS}
        for composite_name, composite_value in composite_params.items():
            for key, val in composite_value.items():
                if 'unit' in val.keys():
                    val['unit'] = u.Unit(val['unit']) if isinstance(val['unit'], str) else val['unit']
                    val['unit'] = val['unit'].to_string()

    return dictionary


def prep_constrained_params(x0):
    """
    Function treats constrained parameters by assingning None to `value`
    :param x0: dict;
    :return: dict;
    """
    def check_value_in_constrained(item):
        if 'constraint' in item.keys():
            if 'value' in item.keys():
                logger.warning(
                    f'Parameter `value` is meaningless and will not be used in case of contrained parameter '
                    '{key}.')
            item['value'] = None

    for param_type in x0.values():
        for system_key, system_val in param_type.items():
            if system_key in params.COMPOSITE_PARAMS:  # testing if item are spots or pulsations
                for composite_item in system_val.values():  # particular spot or pulsation mode
                    # iterating over params of the spot or pulsation mode
                    for composite_item_val in composite_item.values():
                        check_value_in_constrained(composite_item_val)
            else:
                check_value_in_constrained(system_val)
    return x0
