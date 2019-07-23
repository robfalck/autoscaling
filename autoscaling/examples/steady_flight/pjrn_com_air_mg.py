import openmdao.api as om
import dymos as dm

from aircraft_ode import AircraftODE
from dymos.utils.lgl import lgl


def main():
    import pickle
    with open('unsc_tji_sc.pickle', 'rb') as file:
        jac = pickle.load(file)
    with open('lower_bounds_info.pickle', 'rb') as file:
        lbs = pickle.load(file)
    with open('upper_bounds_info.pickle', 'rb') as file:
        ubs = pickle.load(file)

    p = om.Problem(model=om.Group())
    p.driver = om.pyOptSparseDriver()
    p.driver.options['optimizer'] = 'SNOPT'
    p.driver.options['dynamic_simul_derivs'] = True

    num_seg = 15
    seg_ends, _ = lgl(num_seg + 1)

    traj = p.model.add_subsystem('traj', dm.Trajectory())

    phase = traj.add_phase('phase0',
                           dm.Phase(ode_class=AircraftODE,
                                    transcription=dm.Radau(num_segments=num_seg,
                                                           segment_ends=seg_ends,
                                                           order=3, compressed=False)))

    # Pass Reference Area from an external source
    assumptions = p.model.add_subsystem('assumptions', om.IndepVarComp())
    assumptions.add_output('S', val=427.8, units='m**2')
    assumptions.add_output('mass_empty', val=1.0, units='kg')
    assumptions.add_output('mass_payload', val=1.0, units='kg')

    phase.set_time_options(initial_bounds=(0, 0), duration_bounds=(300, 10000))

    phase.set_state_options('range', units='NM', fix_initial=True,
                            fix_final=False, lower=0, upper=2000)
    phase.set_state_options('mass_fuel', units='lbm', fix_initial=True,
                            fix_final=True, upper=1.5E5, lower=0.0)
    phase.set_state_options('alt', units='kft', fix_initial=True,
                            fix_final=True, lower=0.0, upper=60)

    phase.add_control('climb_rate', units='ft/min', opt=True, lower=-3000,
                      upper=3000, rate_continuity=True, rate2_continuity=False)
    phase.add_control('mach', units=None, opt=False)

    phase.add_input_parameter('S', units='m**2')
    phase.add_input_parameter('mass_empty', units='kg')
    phase.add_input_parameter('mass_payload', units='kg')

    phase.add_path_constraint('propulsion.tau', lower=0.01, upper=2.0, shape=(1,))

    p.model.connect('assumptions.S', 'traj.phase0.input_parameters:S')
    p.model.connect('assumptions.mass_empty', 'traj.phase0.input_parameters:mass_empty')
    p.model.connect('assumptions.mass_payload', 'traj.phase0.input_parameters:mass_payload')

    phase.add_objective('range', loc='final')

    p.setup()

    p['traj.phase0.t_initial'] = 0.0
    p['traj.phase0.t_duration'] = 3600.0
    p['traj.phase0.states:range'][:] = phase.interpolate(ys=(0, 724.0), nodes='state_input')
    p['traj.phase0.states:mass_fuel'][:] = phase.interpolate(ys=(30000, 1e-3), nodes='state_input')
    p['traj.phase0.states:alt'][:] = 10.0

    p['traj.phase0.controls:mach'][:] = 0.8

    p['assumptions.S'] = 427.8
    p['assumptions.mass_empty'] = 0.15E6
    p['assumptions.mass_payload'] = 84.02869 * 400

    from autoscaling.autoscaling import autoscale
    autoscale(p, jac, lbs, ubs)

    p.run_driver()


if __name__ == '__main__':
    main()
