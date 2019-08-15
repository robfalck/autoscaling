import openmdao.api as om
import dymos as dm
import numpy as np


class BrachODE(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn = self.options['num_nodes']

        # Add inputs, outputs
        self.add_input('v', val=np.zeros(nn), units='m/s')
        self.add_input('g', val=np.zeros(nn), units='m/s**2')
        self.add_input('th', val=np.zeros(nn), units='rad')

        self.add_output('xdot', val=np.zeros(nn), units='m/s')
        self.add_output('ydot', val=np.zeros(nn), units='m/s')
        self.add_output('vdot', val=np.zeros(nn), units='m/s**2')

        # Declare partials
        arange = np.arange(nn)

        self.declare_partials('xdot', 'v', rows=arange, cols=arange)
        self.declare_partials('xdot', 'th', rows=arange, cols=arange)

        self.declare_partials('ydot', 'v', rows=arange, cols=arange)
        self.declare_partials('ydot', 'th', rows=arange, cols=arange)

        self.declare_partials('vdot', 'g', rows=arange, cols=arange)
        self.declare_partials('vdot', 'th', rows=arange, cols=arange)

    def compute(self, ins, outs):
        v, th, g = ins['v'], ins['th'], ins['g']
        sin_th, cos_th = np.sin(th), np.cos(th)

        outs['xdot'] = v * sin_th
        outs['ydot'] = v * cos_th
        outs['vdot'] = g * cos_th

    def compute_partials(self, ins, J):
        v, th, g = ins['v'], ins['th'], ins['g']
        sin_th, cos_th = np.sin(th), np.cos(th)

        J['xdot', 'v'] = sin_th
        J['xdot', 'th'] = v * cos_th

        J['ydot', 'v'] = cos_th
        J['ydot', 'th'] = -v * sin_th

        J['vdot', 'g'] = cos_th
        J['vdot', 'th'] = -g * sin_th

if __name__ == '__main__':
    prob = om.Problem()
    model = prob.model

    traj = dm.Trajectory()
    model.add_subsystem('traj', traj)

    phase = dm.Phase(ode_class=BrachODE, transcription=dm.GaussLobatto(num_segments=10))
    traj.add_phase('phase0', phase)

    phase.set_time_options(fix_initial=True)
    phase.set_state_options('x', fix_initial=True, fix_final=True)
    phase.set_state_options('y', fix_initial=True, fix_final=True)
    phase.set_state_options('v', fix_initial=True)
    phase.add_control('th', units='deg', lower=0.01, upper=179.9)
    phase.add_design_parameter('g', units='m/s**2', opt=False, val=9.80665)

    phase.add_objective('time', loc='final')

    prob.driver = om.ScipyOptimizeDriver()
    model.linear_solver = om.DirectSolver()     # isn't the linear solver DirectSolver by default?

    prob.setup()

    prob['traj.phase0.t_initial'] = 0.0
    prob['traj.phase0.t_duration'] = 1.0
    prob['traj.phase0.states:x'] = phase.interpolate(ys=[0,100], nodes='state_input')
    prob['traj.phase0.states:y'] = phase.interpolate(ys=[0,1], nodes='state_input')
    prob['traj.phase0.states:v'] = phase.interpolate(ys=[0,5], nodes='state_input')
    prob['traj.phase0.controls:th'] = phase.interpolate(ys=[5,100.5], nodes='control_input')

    prob.run_driver()

    import matplotlib.pyplot as plt
    X = prob['traj.phase0.timeseries.states:x']
    Y = prob['traj.phase0.timeseries.states:y']
    plt.plot(X,Y,'b-')
    plt.savefig('brach.png')
