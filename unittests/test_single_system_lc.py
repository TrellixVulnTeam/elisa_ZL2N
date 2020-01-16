import os.path as op
import numpy as np

from importlib import reload

from elisa.conf import config
from elisa.observer.observer import Observer
from unittests.utils import (
    ElisaTestCase,
    prepare_single_system,
    load_light_curve,
    normalize_lc_for_unittests,
)
from elisa import (
    units,
    umpy as up,
)
from elisa.single_system.curves import (
    lc
)

TOL = 5e-3


class ComputeLightCurvesTestCase(ElisaTestCase):
    PARAMS = {
        'solar':
        {
            "mass": 1.0,
            "t_eff": 5772 * units.K,
            "gravity_darkening": 0.32,
            "polar_log_g": 4.43775*units.dex(units.cm/units.s**2),
            "gamma": 0.0,
            # "inclination": 82.5 * units.deg,
            "inclination": 90.0 * units.deg,
            "rotation_period": 25.38 * units.d,
        },
    }

    SPOTS_META = {
    "standard":
        [
            {"longitude": 80,
             "latitude": 58,
             "angular_radius": 5,
             "temperature_factor": 0.7},
            {"longitude": 60,
             "latitude": 53,
             "angular_radius": 6,
             "temperature_factor": 0.68},
        ],
    }

    def setUp(self):
        # raise unittest.SkipTest(message)
        self.base_path = op.join(op.dirname(op.abspath(__file__)), "data", "light_curves")
        self.law = config.LIMB_DARKENING_LAW

        config.VAN_HAMME_LD_TABLES = op.join(self.base_path, "limbdarkening")
        config.CK04_ATM_TABLES = op.join(self.base_path, "atmosphere")
        config.ATM_ATLAS = "ck04"
        config._update_atlas_to_base_dir()

    def tearDown(self):
        config.LIMB_DARKENING_LAW = self.law
        reload(lc)

    def test_clear_single_system(self):
        config.LIMB_DARKENING_LAW = "linear"
        reload(lc)

        s = prepare_single_system(self.PARAMS['solar'])
        o = Observer(passband=['Generic.Bessell.V'], system=s)

        start_phs, stop_phs, step = -0.2, 1.2, 0.1

        expected = load_light_curve("single.clear.v.json")
        expected_phases = expected[0]
        expected_flux = normalize_lc_for_unittests(expected[1]["Generic.Bessell.V"])

        obtained = o.lc(from_phase=start_phs, to_phase=stop_phs, phase_step=step)
        obtained_phases = obtained[0]
        obtained_flux = normalize_lc_for_unittests(obtained[1]["Generic.Bessell.V"])

        self.assertTrue(np.all(up.abs(np.round(obtained_phases, 3) - np.round(expected_phases, 3)) < TOL))
        self.assertTrue(np.all(up.abs(np.round(obtained_flux, 3) - np.round(expected_flux, 3)) < TOL))

    def test_spotty_single_system(self):
        config.LIMB_DARKENING_LAW = "linear"
        reload(lc)

        s = prepare_single_system(self.PARAMS['solar'], spots=self.SPOTS_META["standard"])
        o = Observer(passband=['Generic.Bessell.V'], system=s)

        start_phs, stop_phs, step = -0.2, 1.2, 0.1

        expected = load_light_curve("single.clear.v.json")
        expected_phases = expected[0]
        expected_flux = normalize_lc_for_unittests(expected[1]["Generic.Bessell.V"])

        obtained = o.lc(from_phase=start_phs, to_phase=stop_phs, phase_step=step)
        obtained_phases = obtained[0]
        obtained_flux = normalize_lc_for_unittests(obtained[1]["Generic.Bessell.V"])

        self.assertTrue(np.all(up.abs(np.round(obtained_phases, 3) - np.round(expected_phases, 3)) < TOL))
        self.assertTrue(np.all(up.abs(np.round(obtained_flux, 3) - np.round(expected_flux, 3)) < TOL))
