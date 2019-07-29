
import pickle
lbs = {}

lbs['traj.phases.ascent.indep_states.states:r'] = 0.0
lbs['traj.phases.ascent.time_extents.t_duration'] = 1.0
lbs['traj.phases.descent.time_extents.t_initial'] = 0.5
lbs['traj.phases.ascent.indep_states.states:gam'] = 0.0
lbs['traj.phases.descent.indep_states.states:gam'] = -45
lbs['traj.phases.descent.indep_states.states:v'] = 150.0
lbs['traj.phases.descent.indep_states.states:r'] = 100.0
lbs['traj.phases.descent.time_extents.t_duration'] = 0.5
lbs['traj.phases.ascent.indep_states.states:h'] = 0.0
lbs['traj.phases.descent.indep_states.states:h'] = 0.0
lbs['traj.phases.ascent.indep_states.states:v'] = 150.0


ubs = {}

ubs['traj.phases.ascent.indep_states.states:r'] = 100.0
ubs['traj.phases.ascent.time_extents.t_duration'] = 100.0
ubs['traj.phases.descent.time_extents.t_initial'] = 100.0
ubs['traj.phases.ascent.indep_states.states:gam'] = 25.0
ubs['traj.phases.descent.indep_states.states:gam'] = 0
ubs['traj.phases.descent.indep_states.states:v'] = 200.0
ubs['traj.phases.descent.indep_states.states:r'] = 200.0
ubs['traj.phases.descent.time_extents.t_duration'] = 100.0
ubs['traj.phases.ascent.indep_states.states:h'] = 100.0
ubs['traj.phases.descent.indep_states.states:h'] = 100.0
ubs['traj.phases.ascent.indep_states.states:v'] = 200.0

with open('lower_bounds_info.pickle', 'wb') as file:
    pickle.dump(lbs, file, protocol=pickle.HIGHEST_PROTOCOL)
with open('upper_bounds_info.pickle', 'wb') as file:
    pickle.dump(ubs, file, protocol=pickle.HIGHEST_PROTOCOL)
