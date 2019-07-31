import dymos as dm
import openmdao.api as om
import pickle
from aircraft_ode import AircraftODE
from dymos.utils.lgl import lgl
from autoscaling.api import autoscale, IsoScaler, PJRNScaler


def main():
    prob = om.Problem()
    model = prob.model

    num_seg = 15
    seg_ends, _ = lgl(num_seg + 1)
    traj = model.add_subsystem('traj', dm.Trajectory())
    phase = traj.add_phase('phase0',
                           dm.Phase(ode_class=AircraftODE,
                                    transcription=dm.Radau(num_segments=num_seg,
                                                           segment_ends=seg_ends,
                                                           order=3, compressed=False)))

    assumptions = model.add_subsystem('assumptions', om.IndepVarComp())
    assumptions.add_output('S', val=427.8, units='m**2')
    assumptions.add_output('mass_empty', val=1.0, units='kg')
    assumptions.add_output('mass_payload', val=1.0, units='kg')

    prob.driver = om.pyOptSparseDriver()
    prob.driver.options['optimizer'] = 'SNOPT'

    phase.set_time_options(initial_bounds=(0, 0), duration_bounds=(300, 10000))

    phase.set_state_options('range', units='NM', fix_initial=True,
                            fix_final=False, lower=0, upper=2000)
    phase.set_state_options('mass_fuel', units='lbm', fix_initial=True, fix_final=True,
                            upper=1.5E5, lower=0.0)
    phase.set_state_options('alt', units='kft', fix_initial=True, fix_final=True,
                            lower=0.0, upper=60)

    phase.add_control('climb_rate', units='ft/min', opt=True, lower=-3000, upper=3000,
                      rate_continuity=True, rate2_continuity=False)

    phase.add_control('mach', units=None, opt=False)

    phase.add_input_parameter('S', units='m**2')
    phase.add_input_parameter('mass_empty', units='kg')
    phase.add_input_parameter('mass_payload', units='kg')

    phase.add_path_constraint('propulsion.tau', lower=0.01, upper=2.0, shape=(1,))

    model.connect('assumptions.S', 'traj.phase0.input_parameters:S')
    model.connect('assumptions.mass_empty', 'traj.phase0.input_parameters:mass_empty')
    model.connect('assumptions.mass_payload', 'traj.phase0.input_parameters:mass_payload')

    phase.add_objective('range', loc='final')

    prob.setup()

    prob['traj.phase0.t_initial'] = 0.0
    prob['traj.phase0.t_duration'] = 3600.0
    prob['traj.phase0.states:range'][:] = phase.interpolate(ys=(0, 724.0), nodes='state_input')
    prob['traj.phase0.states:mass_fuel'][:] = phase.interpolate(
        ys=(30000, 1e-3), nodes='state_input')
    prob['traj.phase0.states:alt'][:] = 10.0

    prob['traj.phase0.controls:mach'][:] = 0.8

    prob['assumptions.S'] = 427.8
    prob['assumptions.mass_empty'] = 0.15E6
    prob['assumptions.mass_payload'] = 84.02869 * 400

    with open('total_jac_info.pickle', 'rb') as file:
        jac = pickle.load(file)
    with open('lower_bounds_info.pickle', 'rb') as file:
        lbs = pickle.load(file)
    with open('upper_bounds_info.pickle', 'rb') as file:
        ubs = pickle.load(file)

    # sc = None
    # sc = IsoScaler(jac, lbs, ubs)
    sc = PJRNScaler(jac, lbs, ubs)

    autoscale(prob, autoscaler=sc)

    prob.run_driver()

    # with open('total_jac_info.pickle', 'wb') as file:
    #     pickle.dump(prob.compute_totals(), file, protocol=pickle.HIGHEST_PROTOCOL)

    return prob


if __name__ == '__main__':
    main()
