from brach_ode import BrachODE
import dymos as dm
import openmdao.api as om
from autoscaling.api import autoscale, PJRNScaler, IsoScaler


def main():
    prob = om.Problem()
    model = prob.model

    traj = model.add_subsystem('traj', dm.Trajectory())
    phase = dm.Phase(ode_class=BrachODE, transcription=dm.GaussLobatto(num_segments=10))
    traj.add_phase('phase0', phase)

    prob.driver = om.pyOptSparseDriver()
    prob.driver.options['optimizer'] = 'SNOPT'
    prob.driver.opt_settings['iSumm'] = 6

    phase.set_time_options(fix_initial=True, duration_bounds=(0.1, 100), units='s')
    phase.add_state('x', fix_initial=True, fix_final=True, units='m', rate_source='xdot')
    phase.add_state('y', fix_initial=True, fix_final=True, units='m', rate_source='ydot')
    phase.add_state('v', fix_initial=True, units='m/s', rate_source='vdot', targets=['v'])
    phase.add_control('th', lower=0.01, upper=179.9, units='deg', targets=['th'])
    phase.add_design_parameter('g', opt=False, val=9.80665, units='m/s**2', targets=['g'])

    phase.add_objective('time', loc='final')

    prob.setup()

    # Specify the initial guess
    prob['traj.phase0.t_initial'] = 0.0
    prob['traj.phase0.t_duration'] = 30.0
    prob['traj.phase0.states:x'] = phase.interpolate(ys=[0, 1000], nodes='state_input')
    prob['traj.phase0.states:y'] = phase.interpolate(ys=[0, 1], nodes='state_input')
    prob['traj.phase0.states:v'] = phase.interpolate(ys=[0, 10], nodes='state_input')
    prob['traj.phase0.controls:th'] = phase.interpolate(ys=[5, 100.5], nodes='control_input')

    # Scale the problem
    # sc = None
    # sc = IsoScaler(jac, lbs, ubs)

    autoscale(prob, autoscaler=PJRNScaler(prob))

    prob.run_driver()

    return prob


if __name__ == '__main__':
    main()
