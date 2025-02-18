Change Log
==========
|


v0.1_
-----
.. v0.1_: https://github.com/mikecokina/elisa/commits/release/0.1

**Release date:** 2019-11-06

**Features**


* **binary system modeling**

    - points surface generation from generalized surface potential
    - triangulation (faces creation) of component`s surface points
    - physical quantities (gravity, temperatures) distribution over component surface (faces)
    - surface spots
    - temperature pulsations effect
    - light curves modeling for circular synchronous/asynchronous orbits with spotty/no-spotty components
    - radial velocity curves based on movement of center of mass

* **binary system visualization**

    - surface points plot
    - surface wire mesh plot
    - surface faces plot with visualization of distribution of physical quantities
    - orbit plot
    - animations of orbital motions


v0.2_
-----
.. v0.2_: https://github.com/mikecokina/elisa/commits/release/0.2

**Release date:** 2019-12-29

**Features**

* **binary system radial velocities curves modeling**

    - radial velocity curves based on movement of center of mass computed upon astro-community quantities (:math:`q`, :math:`asini`)

* **capability to compute lightcurves on several processor's cores (multiprocessing)**

    - split supplied phases to `N` smaller batches (N is equal to desired processes but up to number of available cores) and computed all at once

* **fitting parameters of binary system**

    - light curve fitting using ``Markov Chain Monte Carlo`` (capability to fit using standard physical parameters :math:`M_1`, :math:`M_2` or parameters used by community :math:`q` (mass ratio) and :math:`a` (semi major axis))
    - light curve fitting using ``non-linear least squares`` method (capability to fit using standard physica; parameters :math:`M_1`, :math:`M_2` or parameters used by community :math:`q` (mass ratio) and :math:`a` (semi major axis))
    - radial velocity fitting based on ``Markov Chain Monte Carlo`` method (standard physical parameters, :math:`M_1`, :math:`M_2`, :math:`e`, :math:`i`, :math:`{\omega}`, :math:`{\gamma}`
    - radial velocity fitting based on ``non-linear least squares`` method (standard physical parameters, :math:`M_1`, :math:`M_2`, :math:`e`, :math:`i`, :math:`{\omega}`, :math:`{\gamma}`

* **more specific errors raised**

    - created several different type of errors (see ``elisa.base.errors`` for more information)

**Fixes**

- `elisa.observer.Observer.observe.lc` and `elisa.observer.Observer.observe.rv` will not raise an error in case
  when parameter `phases` is `numpy.array` type
- adaptive discretization of binaries do not allow to change distretization factor out of prescribed boundaries
  (it used to lead to small amount of surface points and then triangulation crashed)
- app does not crash on `phase_interval_reduce` in observer during light curve computation
  if BinarySystem is not used from direct import of `BinarySystem`
- const PI multiplicator removed from output flux (still require investigation)
- app does not crash if `bolometric` passband is used
- np.int32/64 and np.float32/64 are considered as valid values on binary system initialization


v0.2.1_
-------
.. v0.2.1_: https://github.com/mikecokina/elisa/commits/release/0.2.1

**Release date:** 2020 2020-01-17

**Fixes**

- spots discretization managed by parent object if not specified otherwise
- valid detection of spots on over-contact neck

v0.2.2_
-------
.. v0.2.2_: https://github.com/mikecokina/elisa/commits/release/0.2.2

**Release date:** 2020-01-29

**Fixes**

- radial velocity curves orientation
- fixed requirements in setupy.py
- fixed requirements in docs

v0.2.3_
-------
.. v0.2.3_: https://github.com/mikecokina/elisa/commits/release/0.2.3

**Release date:** 2020-05-27

**Fixes**

- fitting light curves of over-contact binaries won't crash with missing `param` error due to invalid constraint setting on backend
- normalize lightcurves (during fitting procedure) each on its max values instead of normalization on global maximum
- MCMC penalisation in case of invalid binary system return big negative number instead of value near to 0.0
- raise `elisa.base.error.AtmosphereError` when atmosphere file not founf instead `FileNotFoundError`

v0.3_
-----

.. v0.3_: https://github.com/mikecokina/elisa/commits/release/0.3

**Release date:** 2020-06-17

**Features**

* **single system**
    - light curve calculation of single stars with spots and pulsations

* **analytics api** *
    - more user frendly analytics api
    - summary outputs of fitting
    - extended i/o of fitting

* **computaional** *
    - TESS passband (limb darkening tables included)

**Fixes**

    - fitting light curves of over-contact binaries won't crash with missing `param` error due to invalid constraint setting on backend
    - normalize lightcurves (during fitting procedure) each on its max values instead of normalization on global maximum
    - MCMC penalisation in case of invalid binary system return big negative number instead of value near to 0.0
    - raise `elisa.base.error.AtmosphereError` when atmosphere file not founf instead `FileNotFoundError`
    - lc observation atmosphere is not hardcode to `ck04` anymore
    - small spots do not cause crashes
    - mcmc chain evaluator often crashed when fitting system with component filling its roche lobe, fixed by snapping
      surface potential to critical potentials if they are within errors from fitted potential

v0.3.1_
-------

.. v0.3.1_: https://github.com/mikecokina/elisa/commits/release/0.3.1

**Release date:** 2020-08-19

**Enhancements**

    - fit_summary (result_summary) function now enables full propagation of errors using `propagate_errors` argument

**Fixes**

    - on-demand normalization of light curves
    - mcmc chain evaluator often crashed when fitting system with component filling its roche lobe, fixed by snapping
      surface potential to critical potentials if they are within errors from fitted potential
    - wrong intervals used in corner and trace plot, now fitting confidence intervals instead of fit intervals
    - more suitable form of cost function for least squares fitting method
    - correcting secondary potential derivative component
    - libration motion accounted for in spot position in case of eccetric orbits
    - fix: volume conserved in eccentric spotty systems

v0.4_
-----

.. v0.4_: https://github.com/mikecokina/elisa/commits/release/0.4

**Release date:** 2020-10-01


**Features**

    - radial velocity curves modelled based on radiometric quantities capable of modelling
      Rossitter effect and effect of spots

**Enhancements**

    - dependencies updates
    - support Python 3.6|3.7|3.8
    - configuration module uses singleton instead of global variables
      >>> from elisa import settings
    - ability to display observation stored in DataSet class using DataSet.plot.display_observation()

**Fixes**

    - removed faulty curve points produced by multiprocessing curve integration methods
    - component's volume conserved for eccentric spotty orbits
    - surface areas produced by numeric noise when total eclipse is occuring are mitigated
    - renormalization of temperature (temperatures powered to exponent of 4)

v0.5_
-----

.. v0.5_: https://github.com/mikecokina/elisa/commits/release/0.5

**Release date:** 2021-10-20

**Features**

    - added `black_body` as one of possibilities for atmospheres
    - support different atmospheres for celestial objects
    - `velocity` and `radial_velocity` option for `colormap` argument added to BinarySystem.plot.surface() and
      SingleSystem.plot.surface()
    - ability to select priors from uniform or normal distribution, standard deviation of the normal distribution is
      defined with the `sigma` fit parameter attribute

**Enhancements**
    - solar constant conserved with different levels of surface discretization
    - improvements to trapezoidal discretization
    - additional constraints for approximations used during integration of eccentric light curves,
      relative change in irradiation is checked when similar orbital positions are evaluated, improves precision
    - pre-build logging schemas added, that are accessible via LOG_CONFIG parameter with options 'default' or 'fit' or
      path to custom configuration file. 'fit' schema will suppress all logging messages except for messages from
      analytics class.
    - utilizing numba for computationally heavy tasks such as reflection effect (preparation for GPU ready version of
      ELISa)
    - function elisa.analytics.tasks.load_results() returns results in form of dict
    - command set_up_logging() not needed anymore while changing logging schemas
    - adaptive and custom sampling during fitting accessed by 'samples' argument
    - ability for surface plot to return figure instance with boolean argument `return_figure_instance`
    - correction of surface underestimation is separately tuned for each discretization method (single star, detached,
      over-contact)
    - ablility to filter flat chain to be within specific interval of parameters using AnalyticsTask.filter_chain
      function. This method is suitable for examining multiple solutions.
    - ability to evaluate R^2 for set of model parameters using function AnalyticsTask.coefficient_of_determination.
    - adding ability to load from json in "radius"-based format that describes the size of the star with
      `equivalent_radius` instead of polar gravity `polar_log_g` in "standard" format
    - BinarySystem and SingleSystem now contain a function build_container that builds a complete model of a system at
      given photometric `phase` or observational `time`.
    - in the default mode (when user did not specified the discretization factor), sizes of surface elements of both
      components are scaled in a way, that the surface elements of both components roughly output the same amount of
      flux, if the (min, max) range of discretization factors can be maintained. This prevents from unnecessary surface
      oversampling of smaller and dimmer binary components.


**Fixes**

    - <binary_system>.init() reinitialize parameters corretly (require fix for pulsations)
    - inclination rotation is provided in positive direction instead of negative
    - line-of-sight vector is switched from [1, 0, 0] to [-1, 0, 0] to make model consistent with radial velocity
      observations where negative value describes velocity of body moving towards the observer. Azimuth of the body is
      now measured with respect to y-axis. Observer is now located at [-inf, 0, 0]
    - atmosphere models are interpolated using flux-based weights instead of temperature based weights
    - calculation of surface element visibility was fixed in cases of eclipses caused by stars smaller than surface
      elements on eclipsed components
    - starting value for implicit solver adjusted in case of near-side parts of overcontact stars generated in
      cylindrical symmetry from polar_radius to 0.25 * polar radius. This prevents a crash of solver for points near
      the neck.

v0.5.1_
-------

.. v0.5.1_: https://github.com/mikecokina/elisa/commits/release/0.5.1

**Release date:** 2021-11-04

**Fixes**

    - fixed requirements to avoid installation error::

        ERROR: packaging 21.2 has requirement pyparsing<3,>=2.0.2, but you'll have pyparsing 3.0.4 which is incompatible.

v0.6
----

**Release date:** ****-**-**

**Features**

    - first run configuration manager - minimal required configuration wizzard on first start when not configured
    - download manager - download limb darkening and atmospheres via download manager instead of manual copying it
    - support python 3.9

**Enhancements**

    - ability to set default_discretization_factor that governs fidelity of the surface mesh
    - ability to automatically fill the semi-major axis (SMA) in fit parameters while fitting the LC data.
      In such cases, the SMA cannot be derived and it has to be fixed at some sensible value which will put component
      surface gravity accelerations within the the range supported by atmospheric models.
      The `LCBinaryAnalyticsTask.set_result()` and `load_result()` functions have default argument
      `autofill_sma`=True that will try to generate a sensible value of SMA if `semi_major_axis` fitting parameter is
      missing in initial fitting parameters JSON/dictionary.
    - setting custom atmosphere models and limb-darkening coefficients for components of modelled system. In case of
      `SingleSystem` and `Binary system`, custom atmosphere model is set with `atmosphere` argument of the `Star`
      instance and custom limb-darkening coefficients can be passed in `limb_darkening_coefficients` for each
      passband filter. Custom limb-darkening coefficients are, however, set constant across the whole surface. In case
      of fitting tasks, custom atmospheres and limb-darkening coefficients are passed as arguments of `AnalyticsTask'
      instance.
    - `BinarySystem` and `SingleSystem` have a new parameter `distance` which defines a distance between observer on
      the system's centre of mass. If not supplied, default value of 10 pc is used.
    - Observer module is now capable of producing light curves ni magnitudes by setting `Observer.flux_unit = u.mag`
      or by keyword argument `flux_unit` in Observer.observe.lc() function.
    - New configuration parameter `MAGNITUDE_SYSTEM` was introduced to define sets of zero points used to
      calculate magnitudes. Available magnitude system are `vega`(default), `ab`, `st`.

**Fixes**

    - configuration parser will not crash when `general.home` is set in config file
    - prior probability in case of normal distribution now clips the edges of the
      distributions correctly according to `min` and `max` fit parameter configuration arguments.

Future plans
============

v1.0
----
    - web GUI and API
