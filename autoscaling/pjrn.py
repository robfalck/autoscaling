class PJRNScaler(object):
    def __init__(self, jac, lbs, ubs):
        # Get full names of vars, defect cons, path cons
        vnames = self._parse_vnames(jac)
        fnames = self._parse_fnames(jac)
        gnames = self._parse_gnames(jac)

        # Compute components of inverses of diagonal matrices Kv, Kf, Kg
        Kv_inv = self._compute_Kv_inv(lbs, ubs)
        Kf_inv = self._compute_Kc_inv(jac, fnames, vnames, Kv_inv)
        Kg_inv = self._compute_Kc_inv(jac, gnames, vnames, Kv_inv)

        # Get refs, defect_refs from Kv, Kf, Kg inverses.
        self.refs = {}
        self.ref0s = {}
        self.defect_refs = {}
        for name in Kv_inv:
            self.refs[name] = ubs[name]
            self.ref0s[name] = lbs[name]
        for name in Kf_inv:
            self.defect_refs[name] = Kf_inv[name]
        for name in Kg_inv:
            self.refs[name] = Kg_inv[name]

    @staticmethod
    def _compute_Kc_inv(jac, cnames, vnames, Kv_inv):
        Kc_inv = {}
        for c in cnames:
            Kc_inv[c] = []
            nn = len(jac[c, list(vnames)[0]])
            for nd in range(nn):
                norm = 0
                for v in vnames:
                    subrow = jac[c, v][nd]
                    sum = 0
                    for el in subrow:
                        sum += el * el
                    norm += sum * Kv_inv[v] ** 2
                norm = norm ** 0.5
                Kc_inv[c].append(norm)
        return Kc_inv

    @staticmethod
    def _compute_Kv_inv(lbs, ubs):
        return {v: ubs[v] - lbs[v] for v in ubs}

    @staticmethod
    def _is_fname(name):
        return '.defects:' in name

    @staticmethod
    def _is_gname(name):
        return '.path:' in name

    @staticmethod
    def _is_state(name):
        return '.states:' in name

    @staticmethod
    def _is_ctrl(name):
        return '.controls:' in name

    @staticmethod
    def _parse_fnames(jac):
        return {of for of, _ in jac if PJRNScaler._is_fname(of)}

    @staticmethod
    def _parse_gnames(jac):
        return {of for of, _ in jac if PJRNScaler._is_gname(of)}

    @staticmethod
    def _parse_vnames(jac):
        return {wrt for _, wrt in jac}
