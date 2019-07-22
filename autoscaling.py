import dymos as dm
import openmdao.api as om
from new_pjrn import PJRNScaler


def autoscale(prob, jac, lbs, ubs):
    pjrn = PJRNScaler(jac, lbs, ubs)
    set_refs(prob.model, pjrn)
    prob.setup()


def get_refs(phase, pjrn):
    refs = {}
    for key in pjrn.refs:
        if is_vname(key):
            short_key = key.split(':')[-1].split('.')[-1]
            refs[short_key] = pjrn.refs[key]
        elif is_gname(key):
            short_key = key.split(':')[-1]
            refs[short_key] = pjrn.refs[key]
    return refs


def get_ref0s(phase, pjrn):
    ref0s = {}
    for key in pjrn.ref0s:
        if is_vname(key):
            short_key = key.split(':')[-1].split('.')[-1]
            ref0s[short_key] = pjrn.ref0s[key]
        elif is_gname(key):
            short_key = key.split(':')[-1]
            ref0s[short_key] = pjrn.ref0s[key]
    return ref0s


def get_defect_refs(phase, pjrn):
    defect_refs = {}
    for key in pjrn.defect_refs:
        if is_fname(key):
            short_key = key.split(':')[-1]
            defect_refs[short_key] = pjrn.defect_refs[key]
    return defect_refs


def is_fname(key):
    return PJRNScaler._is_fname(key)


def is_gname(key):
    return PJRNScaler._is_gname(key)


def is_vname(key):
    return not is_fname(key) and not is_gname(key)


def set_refs(sys, pjrn):
    if isinstance(sys, dm.Phase):
        set_phase_refs(sys, pjrn)
    elif isinstance(sys, om.Group):
        for subsys in sys._loc_subsys_map:
            set_refs(getattr(sys, subsys), pjrn)


def set_phase_refs(phase, pjrn):
    # Get states, ctrls for state
    states = phase.state_options.keys()
    ctrls = phase.control_options.keys()

    # Get refs, ref0s, defect_refs for phase
    refs = get_refs(phase, pjrn)
    ref0s = get_ref0s(phase, pjrn)
    defect_refs = get_defect_refs(phase, pjrn)

    # Set refs for...
    # Time
    if 't_initial' in refs:
        phase.user_time_options['initial_ref'] = refs['t_initial']
    if 't_duration' in refs:
        phase.user_time_options['duration_ref'] = refs['t_duration']
    # States, defects
    for state in states:
        phase.user_state_options[state]['ref'] = refs[state]
        phase.user_state_options[state]['ref0'] = ref0s[state]
        phase.user_state_options[state]['defect_ref'] = defect_refs[state]
    # Controls
    for ctrl in ctrls:
        phase.user_control_options[ctrl]['ref'] = refs[ctrl]
        phase.user_control_options[ctrl]['ref0'] = ref0s[ctrl]

    # Update refs
    phase.time_options.update(phase.user_time_options)
    for state in states:
        phase.state_options[state].update(phase.user_state_options[state])
    for ctrl in ctrls:
        phase.control_options[ctrl].update(phase.user_control_options[ctrl])
