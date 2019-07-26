import dymos as dm
import openmdao.api as om
from autoscaling.auto import AutoScaler
from autoscaling.pjrn import PJRNScaler
from autoscaling.iso import IsoScaler


def autoscale(prob, autoscaler):
    if autoscaler is None:
        return
    assert(isinstance(autoscaler, AutoScaler))
    set_refs(prob.model, autoscaler)
    prob.setup()


def set_refs(sys, sc):
    if isinstance(sys, dm.Phase):
        set_phase_refs(sys, sc)
    elif isinstance(sys, om.Group):
        for subsys in sys._loc_subsys_map:
            set_refs(getattr(sys, subsys), sc)


def set_phase_refs(phase, sc):
    # Get relevant times, states, controls
    loc_times = phase_times(phase, sc)
    loc_states = phase_states(phase, sc)
    loc_controls = phase_controls(phase, sc)

    # Get refs, ref0s, defect_refs
    loc_refs = get_phase_refs(phase, sc)
    loc_ref0s = get_phase_ref0s(phase, sc)
    loc_defect_refs = get_phase_defect_refs(phase, sc)

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


def phase_states(phase, sc):
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


def phase_controls(phase, sc):
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


def get_phase_refs(phase, sc):
    refs = {}
    for nm in sc.refs:
        if phase.pathname in nm:
            loc_nm = sc.local_var_name(nm)
            assert(loc_nm not in refs)
            refs[loc_nm] = sc.refs[nm]
    return refs


def get_phase_ref0s(phase, sc):
    ref0s = {}
    for nm in sc.ref0s:
        if phase.pathname in nm:
            loc_nm = sc.local_var_name(nm)
            assert(loc_nm not in ref0s)
            ref0s[loc_nm] = sc.ref0s[nm]
    return ref0s


def get_phase_defect_refs(phase, sc):
    defect_refs = {}
    for nm in sc.defect_refs:
        if phase.pathname in nm:
            loc_nm = sc.local_var_name(nm)
            assert(loc_nm not in defect_refs)
            defect_refs[loc_nm] = sc.defect_refs[nm]
    return defect_refs
