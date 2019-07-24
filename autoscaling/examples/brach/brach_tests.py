from brach import BrachODE
import dymos as dm
import openmdao.api as om
import pickle
from autoscaling.autoscaling import autoscale


def main():
    # Run unscaled problem
    print('\n\n\n\n\n==========')
    print('UNSCALED PROBLEM')
    print('==========\n\n\n\n\n')
    run_unscaled()

    # Run manually-scaled problem
    print('\n\n\n\n\n==========')
    print('MANUALLY-SCALED PROBLEM')
    print('==========\n\n\n\n\n')
    run_man_scaled()

    # Run variable-scaled problem
    print('\n\n\n\n\n==========')
    print('VARS-ONLY SCALED PROBLEM')
    print('==========\n\n\n\n\n')
    run_PJRN_scaled(vars_only=True)

    # Run PJRN-scaled problem using run-once jac, with driver scaling
    print('\n\n\n\n\n==========')
    print('PJRN-SCALED PROBLEM, USING RUN-ONCE JAC, WITH DRIVER SCALING')
    print('==========\n\n\n\n\n')
    run_PJRN_scaled(model_jac=True, driver_scaling=True)

    # Run PJRN-scaled problem using run-once jac, without driver scaling
    print('\n\n\n\n\n==========')
    print('PJRN-SCALED PROBLEM, USING RUN-ONCE JAC, WITHOUT DRIVER SCALING')
    print('==========\n\n\n\n\n')
    run_PJRN_scaled(model_jac=True, driver_scaling=False)

    # Run PJRN-scaled problem using unscaled problem jac, with driver scaling
    print('\n\n\n\n\n==========')
    print('PJRN-SCALED PROBLEM, USING UNSCALED PROBLEM JAC, WITH DRIVER SCALING')
    print('==========\n\n\n\n\n')
    run_PJRN_scaled(model_jac=False, driver_scaling=True)

    # Run PJRN-scaled problem using unscaled problem jac, without driver scaling
    print('\n\n\n\n\n==========')
    print('PJRN-SCALED PROBLEM, USING UNSCALED PROBLEM JAC, WITHOUT DRIVER SCALING')
    print('==========\n\n\n\n\n')
    run_PJRN_scaled(model_jac=False, driver_scaling=False)


def run_unscaled():
    prob = om.Problem()
    model = prob.model

    traj = model.add_subsystem('traj', dm.Trajectory())
    phase = dm.Phase(ode_class=BrachODE, transcription=dm.GaussLobatto(num_segments=10))
    traj.add_phase('phase0', phase)

    prob.driver = om.pyOptSparseDriver()
    prob.driver.options['optimizer'] = 'SNOPT'

    phase.set_time_options(fix_initial=True)
    phase.set_state_options('x', fix_initial=True, fix_final=True)
    phase.set_state_options('y', fix_initial=True, fix_final=True)
    phase.set_state_options('v', fix_initial=True)
    phase.add_control('th', lower=0.01, upper=179.9, units='deg')
    phase.add_design_parameter('g', opt=False, val=9.80665, units='m/s**2')

    phase.add_objective('time', loc='final')

    prob.setup()

    prob['traj.phase0.t_initial'] = 0.0
    prob['traj.phase0.t_duration'] = 1.0
    prob['traj.phase0.states:x'] = phase.interpolate(ys=[0, 100], nodes='state_input')
    prob['traj.phase0.states:y'] = phase.interpolate(ys=[0, 1], nodes='state_input')
    prob['traj.phase0.states:v'] = phase.interpolate(ys=[0, 10], nodes='state_input')
    prob['traj.phase0.controls:th'] = phase.interpolate(ys=[5, 100.5], nodes='control_input')

    prob.run_driver()

    save_tji(prob, 'tji_unsc_no_driver_scaling.pickle', driver_scaling=False)
    save_tji(prob, 'tji_unsc_w_driver_scaling.pickle', driver_scaling=True)


def run_man_scaled():
    prob = om.Problem()
    model = prob.model

    traj = model.add_subsystem('traj', dm.Trajectory())
    phase = dm.Phase(ode_class=BrachODE, transcription=dm.GaussLobatto(num_segments=10))
    traj.add_phase('phase0', phase)

    prob.driver = om.pyOptSparseDriver()
    prob.driver.options['optimizer'] = 'SNOPT'

    phase.set_time_options(fix_initial=True)
    phase.set_state_options('x', fix_initial=True, fix_final=True, ref=100)
    phase.set_state_options('y', fix_initial=True, fix_final=True)
    phase.set_state_options('v', fix_initial=True, ref=10)
    phase.add_control('th', lower=0.01, upper=179.9, ref=179.9, ref0=0.01, units='deg')
    phase.add_design_parameter('g', opt=False, val=9.80665, units='m/s**2')

    phase.add_objective('time', loc='final')

    prob.setup()

    prob['traj.phase0.t_initial'] = 0.0
    prob['traj.phase0.t_duration'] = 1.0
    prob['traj.phase0.states:x'] = phase.interpolate(ys=[0, 100], nodes='state_input')
    prob['traj.phase0.states:y'] = phase.interpolate(ys=[0, 1], nodes='state_input')
    prob['traj.phase0.states:v'] = phase.interpolate(ys=[0, 10], nodes='state_input')
    prob['traj.phase0.controls:th'] = phase.interpolate(ys=[5, 100.5], nodes='control_input')

    prob.run_driver()


def run_PJRN_scaled(model_jac=False, driver_scaling=False, vars_only=False):
    if vars_only:
        return run_man_scaled()

    prob = om.Problem()
    model = prob.model

    traj = model.add_subsystem('traj', dm.Trajectory())
    phase = dm.Phase(ode_class=BrachODE, transcription=dm.GaussLobatto(num_segments=10))
    traj.add_phase('phase0', phase)

    prob.driver = om.pyOptSparseDriver()
    prob.driver.options['optimizer'] = 'SNOPT'

    phase.set_time_options(fix_initial=True)
    phase.set_state_options('x', fix_initial=True, fix_final=True)
    phase.set_state_options('y', fix_initial=True, fix_final=True)
    phase.set_state_options('v', fix_initial=True)
    phase.add_control('th', lower=0.01, upper=179.9, units='deg')
    phase.add_design_parameter('g', opt=False, val=9.80665, units='m/s**2')

    phase.add_objective('time', loc='final')

    prob.setup()

    prob['traj.phase0.t_initial'] = 0.0
    prob['traj.phase0.t_duration'] = 1.0
    prob['traj.phase0.states:x'] = phase.interpolate(ys=[0, 100], nodes='state_input')
    prob['traj.phase0.states:y'] = phase.interpolate(ys=[0, 1], nodes='state_input')
    prob['traj.phase0.states:v'] = phase.interpolate(ys=[0, 10], nodes='state_input')
    prob['traj.phase0.controls:th'] = phase.interpolate(ys=[5, 100.5], nodes='control_input')

    if (model_jac):
        prob.run_model()
        jac = prob.compute_totals(driver_scaling=driver_scaling)
    else:
        filename = 'tji_unsc_w_driver_scaling.pickle' if driver_scaling else 'tji_unsc_no_driver_scaling.pickle'
        with open(filename, 'rb') as file:
            jac = pickle.load(file)

    with open('lower_bounds_info.pickle', 'rb') as file:
        lbs = pickle.load(file)
    with open('upper_bounds_info.pickle', 'rb') as file:
        ubs = pickle.load(file)

    autoscale(prob, jac, lbs, ubs)

    prob.run_driver()


def save_tji(prob, filename, driver_scaling=False):
    with open(filename, 'wb') as file:
        pickle.dump(prob.compute_totals(driver_scaling=driver_scaling),
                    file, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
