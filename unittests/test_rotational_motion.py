# keep it first
# due to stupid astropy units/constants implementation
from unittests import set_astropy_units

import numpy as np
import elisa.const as c

from numpy.testing import assert_array_equal
from elisa.single_system.orbit import orbit
from unittests.utils import ElisaTestCase

set_astropy_units()


class RotationalMotionTestCase(ElisaTestCase):
    def setUp(self):
        super(RotationalMotionTestCase, self).setUp()
        self.params_combination = np.array(
            [{"phase_shift": 0, "rotation_period": 0.9, "inclination": c.HALF_PI},

             {"phase_shift": np.pi / 2.0, "rotation_period": 0.9, "inclination": c.HALF_PI},

             {"rotation_period": 0.9, "inclination": c.HALF_PI},

             {"phase_shift": np.pi / 2.0, "rotation_period": 0.9, "inclination": np.radians(86.4)},
             ])

    def test_rotational_motion(self):
        phases = np.array([-0.1, 0.0, 0.1, 0.5, 1.0, 1.1])
        obtained = []
        expected = [np.array([[-0.6283, np.nan, -0.1],
                              [0., np.nan, 0.],
                              [0.6283, np.nan, 0.1],
                              [3.1416, np.nan, 0.5],
                              [6.2832, np.nan, 1.],
                              [6.9115, np.nan, 1.1]]), ]
        for i, combo in enumerate(self.params_combination[np.array([0])]):
            o = orbit.Orbit(**combo)
            obtained.append(np.round(o.rotational_motion(phases), 4))
        assert_array_equal(expected, obtained)

    def test_rotational_motion_from_azimuths(self):
        azimuths = np.array([-0.1, 0.0, 0.1, 0.5, 1.0, 1.1]) * c.FULL_ARC
        obtained = []
        expected = [np.array([[-0.6283, np.nan, -0.1],
                              [0., np.nan, 0.],
                              [0.6283, np.nan, 0.1],
                              [3.1416, np.nan, 0.5],
                              [6.2832, np.nan, 1.],
                              [6.9115, np.nan, 1.1]]), ]
        for i, combo in enumerate(self.params_combination[np.array([0])]):
            o = orbit.Orbit(**combo)
            obtained.append(np.round(o.rotational_motion_from_azimuths(azimuths), 4))
        assert_array_equal(expected, obtained)
