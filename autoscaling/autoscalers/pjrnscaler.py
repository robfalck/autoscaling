"""Define PJRNScaler class."""

from autoscaling.core.autoscaler import AutoScaler


class PJRNScaler(AutoScaler):
    """
    Helper class for automatic scaling of dynamically-constrained optimization problems via the projected jacobian rows normalization (PJRN) method.

    Attributes
    ----------
    refs : dict
        Maps a variable's global name to its ref value.
    ref0s : dict
        Maps a variable's global name to its ref0 value.
    defect_refs : dict
        Maps a variable's defect's global name to its defect_ref value.
    """

    def initialize(self, jac, lbs, ubs):
        """
        Initialize, using the given variable bounds and jacobian information.

        Parameters
        ----------
        jac : dict
            Jacobian information from which global variable, constraint names are parsed. Must be compatible with the Dymos problem at hand.
        lbs : dict
            Maps a global variable (not a constraint) name to its lower bound.
        ubs : dict
            Maps a global variable (not a constraint) name to its upper bound.
        """
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

    @staticmethod
    def _parse_vnames_from(jac):
        """
        Parse global variable names from given jacobian information.

        Parameters
        ----------
        jac : dict
            Jacobian information.
        """
        vnames = set()
        for of, wrt in jac:
            if PJRNScaler.is_state_name(wrt):
                vnames.add(wrt)
            elif PJRNScaler.is_control_name(wrt):
                vnames.add(wrt)
        return vnames

    @staticmethod
    def _parse_fnames_from(jac):
        """
        Parse global collocation defect constraint names from given jacobian information.

        Parameters
        ----------
        jac : dict
            Jacobian information.
        """
        fnames = set()
        for of, wrt in jac:
            if PJRNScaler.is_defect_name(of):
                fnames.add(of)
        return fnames

    @staticmethod
    def _parse_gnames_from(jac):
        """
        Parse global path defect constraint names from given jacobian information.

        Parameters
        ----------
        jac : dict
            Jacobian information.
        """
        gnames = set()
        for of, wrt in jac:
            if PJRNScaler.is_path_constraint_name(of):
                gnames.add(of)
        return gnames
