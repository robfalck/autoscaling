from .auto import AutoScaler


class PJRNScaler(AutoScaler):
    def __init__(self, jac, lbs, ubs):
        super(PJRNScaler, self).__init__()

        vnames = set()
        for of, wrt in jac:
            if '.states:' in wrt:
                vnames.add(wrt)
            elif '.controls:' in wrt:
                vnames.add(wrt)

        fnames = set()
        for of, wrt in jac:
            if '.defects:' in of:
                fnames.add(of)

        gnames = set()
        for of, wrt in jac:
            if '.path:' in of:
                gnames.add(of)

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

        for nm in vnames:
            self.refs[nm] = ubs[nm]
            self.ref0s[nm] = lbs[nm]
        for nm in fnames:
            self.defect_refs[nm] = Kf_inv[nm]
        for nm in gnames:
            self.refs[nm] = Kg_inv[nm]
            self.ref0s[nm] = 0
