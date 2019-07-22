from brach import BrachODE
import dymos as dm
import openmdao.api as om
import pickle

x_f = 100      # value for x_f; assumed to equal x_f from previous solve


def main():
    # ============================
    # Load in jac, lbs, ubs for testing
    # ============================
    with open('total_jac_info.pickle', 'rb') as file:
        jac = pickle.load(file)
    with open('lower_bounds_info.pickle', 'rb') as file:
        lbs = pickle.load(file)
    with open('upper_bounds_info.pickle', 'rb') as file:
        ubs = pickle.load(file)

    # =======================
    # Scale problem and solve
    # =======================
    prob = om.Problem()
    model = prob.model

    traj = model.add_subsystem('traj', dm.Trajectory())
    phase = dm.Phase(ode_class=BrachODE, transcription=dm.GaussLobatto(num_segments=10))
    traj.add_phase('phase0', phase)

    prob.driver = om.pyOptSparseDriver()
    prob.driver.options['optimizer'] = 'SNOPT'

    configure_phase_for_optimization_unscaled(phase)

    prob.setup()

    prob['traj.phase0.t_initial'] = 0.0
    prob['traj.phase0.t_duration'] = 1.0
    prob['traj.phase0.states:x'] = phase.interpolate(ys=[0, x_f], nodes='state_input')
    prob['traj.phase0.states:y'] = phase.interpolate(ys=[0, 1], nodes='state_input')
    prob['traj.phase0.states:v'] = phase.interpolate(ys=[0, 10], nodes='state_input')
    prob['traj.phase0.controls:th'] = phase.interpolate(ys=[5, 100.5], nodes='control_input')

    from autoscaling import autoscale
    autoscale(prob, jac, lbs, ubs)

    prob.run_driver()


def print_subsystems(sys):
    if isinstance(sys, om.Group):
        for subsys in sys._loc_subsys_map:
            print_subsystems(getattr(sys, subsys))
    else:
        print(sys.name)


def configure_phase_for_optimization(phase, pjrn):
    phase.set_time_options(
        fix_initial=True, duration_ref0=pjrn.ref0s['t_duration'], duration_ref=pjrn.refs['t_duration'])
    phase.set_state_options('x', fix_initial=True, fix_final=True, ref0=pjrn.ref0s['x'],
                            ref=pjrn.refs['x'], defect_ref=pjrn.defect_refs['x'])
    phase.set_state_options('y', fix_initial=True, fix_final=True, ref0=pjrn.ref0s['y'],
                            ref=pjrn.refs['y'], defect_ref=pjrn.defect_refs['y'])
    phase.set_state_options('v', fix_initial=True, ref0=pjrn.ref0s['v'],
                            ref=pjrn.refs['v'], defect_ref=pjrn.defect_refs['v'])
    phase.add_control('th', lower=0.01, upper=179.9, units='deg',
                      ref0=pjrn.ref0s['th'], ref=pjrn.refs['th'])
    phase.add_design_parameter('g', opt=False, val=9.80665, units='m/s**2')

    phase.add_objective('time', loc='final')


def configure_phase_for_optimization_unscaled(phase):
    phase.set_time_options(fix_initial=True)
    phase.set_state_options('x', fix_initial=True, fix_final=True)
    phase.set_state_options('y', fix_initial=True, fix_final=True)
    phase.set_state_options('v', fix_initial=True)
    phase.add_control('th', lower=0.01, upper=179.9, units='deg')
    phase.add_design_parameter('g', opt=False, val=9.80665, units='m/s**2')

    phase.add_objective('time', loc='final')


def set_refs(phase, pjrn):
    # Time
    phase.user_time_options['duration_ref'] = pjrn.refs['t_duration']
    # States
    phase.user_state_options['x']['ref'] = pjrn.refs['x']
    phase.user_state_options['y']['ref'] = pjrn.refs['y']
    phase.user_state_options['v']['ref'] = pjrn.refs['v']
    phase.user_state_options['x']['ref0'] = pjrn.ref0s['x']
    phase.user_state_options['y']['ref0'] = pjrn.ref0s['y']
    phase.user_state_options['v']['ref0'] = pjrn.ref0s['v']
    # Defects
    phase.user_state_options['x']['defect_ref'] = pjrn.defect_refs['x']
    phase.user_state_options['y']['defect_ref'] = pjrn.defect_refs['y']
    phase.user_state_options['v']['defect_ref'] = pjrn.defect_refs['v']
    # Controls
    phase.user_control_options['th']['ref'] = pjrn.refs['th']
    phase.user_control_options['th']['ref0'] = pjrn.ref0s['th']

    # Update
    phase.time_options.update(phase.user_time_options)
    phase.state_options['x'].update(phase.user_state_options['x'])
    phase.state_options['y'].update(phase.user_state_options['y'])
    phase.state_options['v'].update(phase.user_state_options['v'])
    phase.control_options['th'].update(phase.user_control_options['th'])


if __name__ == '__main__':
    main()
