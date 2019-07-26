from .auto import AutoScaler


class IsoScaler(AutoScaler):
    def __init__(self, jac, lbs, ubs):
        super(IsoScaler, self).__init__()

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

        Kv_inv = {v: ubs[v] - lbs[v] for v in vnames}

        Kf_inv = {}
        for f in fnames:
            key = None
            loc_f = f.split(':')[-1]
            for v in vnames:
                if v.split(':')[-1] == loc_f:
                    key = v
                    break
            assert(key is not None)
            Kf_inv[f] = Kv_inv[key]  # note that this is NOT an array!

        for nm in vnames:
            self.refs[nm] = ubs[nm]
            self.ref0s[nm] = lbs[nm]
        for nm in fnames:
            self.defect_refs[nm] = Kf_inv[nm]
