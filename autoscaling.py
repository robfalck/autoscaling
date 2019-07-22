import dymos as dm
import openmdao.api as om


class PJRNScaler(object):
    def __init__(self, jac, lbs, ubs):
        # Get full names of vars, defect cons, path cons
        full_vnames = self._parse_full_vnames_from(jac)
        full_fnames = self._parse_full_fnames_from(jac)
        full_gnames = self._parse_full_gnames_from(jac)

        # Compute components of inverses of diagonal matrices Kv, Kf, Kg
        Kv_inv = self._compute_Kv_inv(lbs, ubs)
        Kf_inv = self._compute_Kf_inv(full_fnames, jac, full_vnames, Kv_inv)
        Kg_inv = self._compute_Kg_inv(full_gnames, jac, full_vnames, Kv_inv)

        # Get refs, defect_refs from Kv, Kf, Kg inverses.
        self.refs = {}
        self.ref0s = {}
        for name in Kv_inv:
            self.refs[name] = ubs[name]
            self.ref0s[name] = lbs[name]
        for name in Kg_inv:
            self.refs[name] = Kg_inv[name]

        self.defect_refs = {}
        for name in Kf_inv:
            self.defect_refs[name] = Kf_inv[name]

    @staticmethod
    def _compute_Kv_inv(lbs, ubs):
        Kv_inv = {}

        # pre: keys for lbs and ubs are the same and correspond with
        # relevant states, ctrls
        for vname in lbs:
            Kv_inv[vname] = ubs[vname] - lbs[vname]

        return Kv_inv

    @staticmethod
    def _compute_Kf_inv(F_names, jac, V_names, Kv_inv):
        Kf_inv = {}

        for fw in F_names:
            short_fw = fw.split(':')[-1]
            Kf_inv[short_fw] = []
            nn = len(jac[fw, V_names[0]])
            for nd in range(nn):
                norm = 0
                for v in V_names:
                    short_v = v.split(':')[-1].split('.')[-1]
                    subrow = jac[fw, v][nd]
                    sum = 0
                    for el in subrow:
                        sum += el * el
                    norm += sum * Kv_inv[short_v] ** 2
                norm = norm ** 0.5
                Kf_inv[short_fw].append(norm)

        return Kf_inv

    @staticmethod
    def _compute_Kg_inv(G_names, jac, V_names, Kv_inv):
        Kg_inv = {}

        for g in G_names:
            short_g = g.split(':')[-1]
            Kg_inv[short_g] = []
            nn = len(jac[g, V_names[0]])
            for nd in range(nn):
                norm = 0
                for v in V_names:
                    short_v = v.split(':')[-1].split('.')[-1]
                    subrow = jac[g, v][nd]
                    sum = 0
                    for el in subrow:
                        sum += el * el
                    norm += sum * Kv_inv[short_v] ** 2
                norm = norm ** 0.5
                Kg_inv[short_g].append(norm)

        return Kg_inv

    @staticmethod
    def _parse_full_fnames_from(jac):
        full_fnames = []

        fnrawdict = {}
        for of, _ in jac:
            fnrawdict[of] = None

        fnrawlist = list(fnrawdict.keys())
        for fnraw in fnrawlist:
            if '.defects:' in fnraw:
                full_fnames.append(fnraw)

        return full_fnames

    @staticmethod
    def _parse_full_gnames_from(jac):
        full_gnames = []

        gnrawdict = {}
        for of, _ in jac:
            gnrawdict[of] = None

        gnrawlist = list(gnrawdict.keys())
        for gnraw in gnrawlist:
            if '.path:' in gnraw:
                full_gnames.append(gnraw)

        return full_gnames

    @staticmethod
    def _parse_full_vnames_from(jac):
        vnrawdict = {}
        for _, wrt in jac:
            vnrawdict[wrt] = None

        return list(vnrawdict)


def autoscale(prob, jac, lbs, ubs):
    pjrn = PJRNScaler(jac, lbs, ubs)
    set_refs(prob.model, pjrn)
    prob.setup()


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
    refs = pjrn.refs
    ref0s = pjrn.ref0s
    defect_refs = pjrn.defect_refs

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
