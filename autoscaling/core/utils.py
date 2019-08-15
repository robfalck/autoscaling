import numpy as np
import openmdao.api as om


def get_jac_and_bounds(prob):
    """
    Retrieve the jacobian and bounds infromation from the given problem.

    Parameters
    ----------
    prob : om.Problem
        The OpenMDAO problem instance.

    Returns
    -------
    jac : dict
        The problem jacobian.
    lbs : dict
        The design variable lower bounds
    ubs : dict
        The design variable upper bounds
    """
    prob.run_model()

    jac = prob.compute_totals()

    desvars = prob.model.get_design_vars(recurse=True)

    lbs = {}
    ubs = {}

    abs2prom = prob.model._var_abs2prom
    for abs_name, options in desvars.items():
        prom_name = abs2prom['output'][abs_name]

        # The lower bound is given by option 'lower' if defined.
        # Otherwise, use the minimum value encountered in the initial guess.
        lb = np.min(options['lower'])
        min_val = np.min(prob.get_val(prom_name))
        lbs[abs_name] = lb if lb > -1.0E16 else min_val

        # The upper bound is given by option 'upper' if defined.
        # Otherwise, use the maximum value encountered in the initial guess.
        ub = np.max(options['upper'])
        max_val = np.max(prob.get_val(prom_name))
        ubs[abs_name] = ub if ub < 1.0E16 else max_val

        # If the lower/upper bounds are equal, set either lower or upper to 0, depending on the
        # current sign.
        if lbs[abs_name] == ubs[abs_name]:
            if lbs[abs_name] > 0:
                lbs[abs_name] = 0.0
            else:
                ubs[abs_name] = 0.0

    return jac, lbs, ubs
