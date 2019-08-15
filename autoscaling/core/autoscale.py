"""Define the autoscale() method."""

import dymos as dm
import openmdao.api as om

from autoscaling.core.autoscaler import AutoScaler


def autoscale(prob, autoscaler):
    """
    Scale the given problem using the scaling data encapsulated by the given autoscaler helper object.

    Parameters
    ----------
    prob : Problem
        Dymos problem to be scaled. Should be single-phase and dynamically-constrained.
    autoscaler : AutoScaler
        Autoscaling helper object.
    """
    if autoscaler is None:
        return
    assert(isinstance(autoscaler, AutoScaler))
    inputs, outputs = _get_vals(prob)
    _set_refs(prob.model, autoscaler)
    prob.setup()
    _set_vals(prob, inputs, outputs)


def _get_vals(prob):
    """
    Save the value of all inputs and outputs so they can be restored after the additional setup.

    Parameters
    ----------
    prob : Problem
        The OpenMDAO problem instance whose values are to be returned.

    Returns
    -------
    inputs : dict
        A dictionary keyed by absolute path mapping to the values of all inputs in the problem.
    outputs : dict
        A dictionary keyed by absolute path mapping to the values of all outputs in the problem.
    """
    inputs = prob.model.list_inputs(prom_name=True, out_stream=None)
    outputs = prob.model.list_outputs(prom_name=True, out_stream=None)
    return inputs, outputs


def _set_vals(prob, inputs, outputs):
    """
    Set the values of all inputs and outputs in the model

    Parameters
    ----------
    prob : dict
        The probem instance to which the values are to be set.
    inputs : dict
        A dictionary keyed by absolute path mapping to the values of all inputs in the problem.
    outputs : dict
        A dictionary keyed by absolute path mapping to the values of all outputs in the problem.
    """
    for input_name, options in inputs:
        prob.set_val(input_name, options['value'])
    for output_name, options in outputs:
        prob.set_val(output_name, options['value'])


def _set_refs(sys, autoscaler):
    """
    Set the scaling reference values for the given system using the given autoscaler

    Parameters
    ----------
    sys : om.System
        The system whose reference scaling values are to be set.
    autoscaler : AutoScaler
        The Autoscaler used to computed the reference scaling values.

    """
    if isinstance(sys, dm.Phase):
        _set_phase_refs(sys, autoscaler)
    elif isinstance(sys, om.Group):
        for subsys in sys._loc_subsys_map:
            _set_refs(getattr(sys, subsys), autoscaler)


def _set_phase_refs(phase, sc):
    # Get relevant times, states, controls
    loc_times = phase_times(phase, sc)
    loc_states = _phase_states(phase, sc)
    loc_controls = _phase_controls(phase, sc)

    # Get refs, ref0s, defect_refs
    loc_refs = _get_phase_refs(phase, sc)
    loc_ref0s = _get_phase_ref0s(phase, sc)
    loc_defect_refs = _get_phase_defect_refs(phase, sc)

    # Set refs, ref0s, defect_refs
    if 't_initial' in loc_times:
        phase.user_time_options['initial_ref'] = loc_refs['t_initial']
        phase.user_time_options['initial_ref0'] = loc_ref0s['t_initial']
    if 't_duration' in loc_times:
        phase.user_time_options['duration_ref'] = loc_refs['t_duration']
        phase.user_time_options['duration_ref0'] = loc_ref0s['t_duration']
    phase.time_options.update(phase.user_time_options)

    for st in loc_states:
        phase.user_state_options[st]['ref'] = loc_refs[st]
        phase.user_state_options[st]['ref0'] = loc_ref0s[st]
        phase.user_state_options[st]['defect_ref'] = loc_defect_refs[st]
        phase.state_options[st].update(phase.user_state_options[st])

    for ct in loc_controls:
        phase.user_control_options[ct]['ref'] = loc_refs[ct]
        phase.user_control_options[ct]['ref0'] = loc_ref0s[ct]
        phase.control_options[ct].update(phase.user_control_options[ct])


def phase_times(phase, sc):
    """
    Gets set of local names corresponding to time information relative to phase.
    Resulting set contains 't_initial', 't_duration', both, or neither.
    """
    times = set()
    for nm in sc.refs:
        if phase.pathname in nm:
            if 't_initial' in nm:
                assert('t_initial' not in times)
                times.add('t_initial')
            elif 't_duration' in nm:
                assert('t_duration' not in times)
                times.add('t_duration')
    return times


def _phase_states(phase, sc):
    """
    Gets set of local names corresponding to phase states.
    """
    states = set()
    for nm in sc.refs:
        if phase.pathname in nm:
            if sc.is_state_name(nm):
                loc_nm = sc.local_var_name(nm)
                assert(loc_nm not in states)
                states.add(loc_nm)
    return states


def _phase_controls(phase, sc):
    """
    Gets set of local names corresponding to phase controls.
    """
    controls = set()
    for nm in sc.refs:
        if phase.pathname in nm:
            if sc.is_control_name(nm):
                loc_nm = sc.local_var_name(nm)
                assert(loc_nm not in controls)
                controls.add(loc_nm)
    return controls


def _get_phase_refs(phase, sc):
    refs = {}
    for nm in sc.refs:
        if phase.pathname in nm:
            loc_nm = sc.local_var_name(nm)
            assert(loc_nm not in refs)
            refs[loc_nm] = sc.refs[nm]
    return refs


def _get_phase_ref0s(phase, sc):
    ref0s = {}
    for nm in sc.ref0s:
        if phase.pathname in nm:
            loc_nm = sc.local_var_name(nm)
            assert(loc_nm not in ref0s)
            ref0s[loc_nm] = sc.ref0s[nm]
    return ref0s


def _get_phase_defect_refs(phase, sc):
    defect_refs = {}
    for nm in sc.defect_refs:
        if phase.pathname in nm:
            loc_nm = sc.local_var_name(nm)
            assert(loc_nm not in defect_refs)
            defect_refs[loc_nm] = sc.defect_refs[nm]
    return defect_refs
