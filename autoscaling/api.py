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
    # Get relevant times, states, ctrls
    loc_times = phase_times(phase, sc)
    loc_states = phase_states(phase, sc)
    loc_ctrls = phase_ctrls(phase, sc)

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

    for ct in loc_ctrls:
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
            if '.states:' in nm:
                loc_nm = nm.split(':')[-1]
                assert(loc_nm not in states)
                states.add(loc_nm)
    return states


def phase_ctrls(phase, sc):
    """
    Gets set of local names corresponding to phase controls.
    """
    ctrls = set()
    for nm in sc.refs:
        if phase.pathname in nm:
            if '.controls:' in nm:
                loc_nm = nm.split(':')[-1]
                assert(loc_nm not in ctrls)
                ctrls.add(loc_nm)
    return ctrls


def get_phase_refs(phase, sc):
    refs = {}
    for nm in sc.refs:
        if phase.pathname in nm:
            loc_nm = nm.split(':')[-1].split('.')[-1]
            assert(loc_nm not in refs)
            refs[loc_nm] = sc.refs[nm]
    return refs


def get_phase_ref0s(phase, sc):
    ref0s = {}
    for nm in sc.ref0s:
        if phase.pathname in nm:
            loc_nm = nm.split(':')[-1].split('.')[-1]
            assert(loc_nm not in ref0s)
            ref0s[loc_nm] = sc.ref0s[nm]
    return ref0s


def get_phase_defect_refs(phase, sc):
    defect_refs = {}
    for nm in sc.defect_refs:
        if phase.pathname in nm:
            loc_nm = nm.split(':')[-1]
            assert(loc_nm not in defect_refs)
            defect_refs[loc_nm] = sc.defect_refs[nm]
    return defect_refs
