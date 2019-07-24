import dymos as dm
import openmdao.api as om
from autoscaling.autosc import AutoScaler


def autoscale(prob, autosc_class, jac, lbs=None, ubs=None):
    import inspect
    assert(inspect.isclass(autosc_class))
    assert(issubclass(autosc_class, AutoScaler))
    sc = autosc_class(jac, lbs, ubs)
    set_refs(prob.model, sc)
    prob.setup()


def get_refs(phase, sc):
    refs = {}
    for glob_name in sc.refs:
        assert(not is_fname(glob_name))
        if name_is_in_phase(glob_name, phase):
            loc_name = get_loc_name(glob_name, phase)
            assert(loc_name not in refs)
            refs[loc_name] = sc.refs[glob_name]
    return refs


def get_ref0s(phase, sc):
    ref0s = {}
    for glob_name in sc.ref0s:
        assert(is_vname(glob_name) or is_gname(glob_name))
        if name_is_in_phase(glob_name, phase):
            loc_name = get_loc_name(glob_name, phase)
            assert(loc_name not in ref0s)
            ref0s[loc_name] = sc.ref0s[glob_name]
    return ref0s


def get_defect_refs(phase, sc):
    defect_refs = {}
    for glob_name in sc.defect_refs:
        assert(is_fname(glob_name))
        if name_is_in_phase(glob_name, phase):
            loc_name = get_loc_name(glob_name, phase)
            assert(loc_name not in defect_refs)
            defect_refs[loc_name] = sc.defect_refs[glob_name]
    return defect_refs


def name_is_in_phase(name, phase):
    return phase.pathname in name


def get_loc_name(name, phase):
    return name.split(':')[-1].split('.')[-1]


def is_fname(name):
    return AutoScaler.is_defect_constraint(name)


def is_gname(name):
    return AutoScaler.is_path_constraint(name)


def is_vname(name):
    return not is_fname(name) and not is_gname(name)


def set_refs(sys, sc):
    if isinstance(sys, dm.Phase):
        set_phase_refs(sys, sc)
    elif isinstance(sys, om.Group):
        for subsys in sys._loc_subsys_map:
            set_refs(getattr(sys, subsys), sc)


def set_phase_refs(phase, sc):
    # Get states, ctrls for state
    states = phase_states(phase, sc)
    ctrls = phase_ctrls(phase, sc)

    # Get refs, ref0s, defect_refs for phase
    refs = get_refs(phase, sc)
    ref0s = get_ref0s(phase, sc)
    defect_refs = get_defect_refs(phase, sc)

    # Set refs for...
    # Time
    if 't_initial' in refs:
        phase.user_time_options['initial_ref'] = refs['t_initial']
        phase.user_time_options['initial_ref0'] = ref0s['t_initial']
    if 't_duration' in refs:
        phase.user_time_options['duration_ref'] = refs['t_duration']
        phase.user_time_options['duration_ref0'] = ref0s['t_duration']
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


def phase_states(phase, sc):
    return {get_loc_name(key, phase) for key in sc.refs if phase.pathname in key and AutoScaler.is_state(key)}


def phase_ctrls(phase, sc):
    return {get_loc_name(key, phase) for key in sc.refs if phase.pathname in key and AutoScaler.is_control(key)}
