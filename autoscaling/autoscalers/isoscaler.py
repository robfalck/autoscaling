"""Define IsoScaler class."""

from autoscaling.core.autoscaler import AutoScaler


class IsoScaler(AutoScaler):
    """
    Helper class for automatic scaling of dynamically-constrained optimization problems via the isoscaling (IS) method.

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
            Jacobian information from which global variable, constraint names are parsed. Assumed to be compatible with the Dymos problem at hand.
        lbs : dict
            Maps a global variable (not a constraint) name to its lower bound.
        ubs : dict
            Maps a global variable (not a constraint) name to its upper bound.
        """
        # Parse global names of states, (dynamic) controls,
        # and collocation defect constraints from total
        # jacobian dict keys...
        vnames = self._parse_vnames_from(jac)
        fnames = self._parse_fnames_from(jac)

        # Calculate diagonals of scaling matrix inverses for
        # variables and defect constraints, according to PJRN
        # defining formulae...
        Kv_inv = {v: ubs[v] - lbs[v] for v in vnames}

        Kf_inv = {}
        for f in fnames:
            key = None
            loc_f = self.local_defect_name(f)
            for v in vnames:
                loc_v = self.local_var_name(v)
                if loc_v == loc_f:
                    key = v
                    break
            assert(key is not None)
            Kf_inv[f] = Kv_inv[key]

        # Set refs, ref0s, defect_refs...
        for nm in vnames:
            self.refs[nm] = ubs[nm]
            self.ref0s[nm] = lbs[nm]
        for nm in fnames:
            self.defect_refs[nm] = Kf_inv[nm]

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
            if IsoScaler.is_state_name(wrt):
                vnames.add(wrt)
            elif IsoScaler.is_control_name(wrt):
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
            if IsoScaler.is_defect_name(of):
                fnames.add(of)
        return fnames
