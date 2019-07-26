from .auto import AutoScaler


class PJRNScaler(AutoScaler):
    """
    Autoscaling helper class that, upon instantiation, utilizes
    given total jacobian and bounds information to compute
    reference values according to the Projected Jacobian Rows
    Normalization (PJRN) autoscaling scheme.

    Attributes
    ----------
    refs : dict
        Variable and path constraint refs.
    ref0s : dict
        Variable and path constraint ref0s.
    defect_refs : dict
        Refs for collocation defect constraints.
    """

    def __init__(self, jac, lbs, ubs):
        """
        Computes reference values according to Projected
        Jacobian Rows Normalization (PJRN) scaling.

        Parameters
        ----------
        jac : dict
            Total jacobian information compatible with the
            problem to be scaled.
        lbs : dict
            Lower bounds information.
        ubs : dict
            Upper bounds information.
        """
        super(PJRNScaler, self).__init__()

        # Parse global names of states, (dynamic) controls,
        # collocation defect constraints, and path constraints
        # from total jacobian dict keys...
        vnames = self._parse_vnames_from(jac)
        fnames = self._parse_fnames_from(jac)
        gnames = self._parse_gnames_from(jac)

        # Calculate diagonals of scaling matrix inverses for
        # variables, defect constraints, and path constraints,
        # according to the PJRN defining formulae...
        Kv_inv = {v: ubs[v] - lbs[v] for v in vnames}

        Kf_inv = {}
        for f in fnames:
            Kf_inv[f] = []
            nn = len(jac[f, list(vnames)[0]])
            for nd in range(nn):
                norm = 0
                for v in vnames:
                    subrow = jac[f, v][nd]
                    sum = 0
                    for el in subrow:
                        sum += el * el
                    norm += sum * Kv_inv[v]**2
                norm = norm ** 0.5
                Kf_inv[f].append(norm)

        Kg_inv = {}
        for g in gnames:
            Kg_inv[g] = []
            nn = len(jac[g, list(vnames)[0]])
            for nd in range(nn):
                norm = 0
                for v in vnames:
                    subrow = jac[g, v][nd]
                    sum = 0
                    for el in subrow:
                        sum += el * el
                    norm += sum * Kv_inv[v]**2
                norm = norm ** 0.5
                Kg_inv[g].append(norm)

        # Set refs, ref0s, defect_refs...
        for nm in vnames:
            self.refs[nm] = ubs[nm]
            self.ref0s[nm] = lbs[nm]
        for nm in fnames:
            self.defect_refs[nm] = Kf_inv[nm]
        for nm in gnames:
            self.refs[nm] = Kg_inv[nm]
            self.ref0s[nm] = 0

    def _parse_vnames_from(self, jac):
        vnames = set()
        for of, wrt in jac:
            if self.is_state_name(wrt):
                vnames.add(wrt)
            elif self.is_control_name(wrt):
                vnames.add(wrt)
        return vnames

    def _parse_fnames_from(self, jac):
        fnames = set()
        for of, wrt in jac:
            if self.is_defect_name(of):
                fnames.add(of)
        return fnames

    def _parse_gnames_from(self, jac):
        gnames = set()
        for of, wrt in jac:
            if self.is_path_constraint_name(of):
                gnames.add(of)
        return gnames
