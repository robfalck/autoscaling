from autoscaling.autosc import AutoScaler


class IsoScaler(AutoScaler):
    def __init__(self, jac, lbs, ubs):
        fnames = self.parse_defect_names(jac)

        Kv_inv = self.compute_Kv_inv(lbs, ubs)
        Kf_inv = self.compute_Kf_inv(fnames, Kv_inv)

        self.refs = {}
        self.ref0s = {}
        self.defect_refs = {}

        for name in Kv_inv:
            self.refs[name] = ubs[name]
            self.ref0s[name] = lbs[name]
        for name in Kf_inv:
            self.defect_refs[name] = Kf_inv[name]

    def compute_Kv_inv(lbs, ubs):
        return {v: ubs[v] - lbs[v] for v in ubs}

    def compute_Kf_inv(fnames, Kv_inv):
        Kf_inv = {}
        for name in fnames:
            loc_name = name.split(':')[-1]
            for vname in Kv_inv:
                if loc_name == vname.split(':')[-1]:
                    Kf_inv[name] = Kv_inv[vname]
                    break
        return Kf_inv
