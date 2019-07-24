
class AutoScaler(object):
    def __init__(self, jac, lbs, ubs):
        pass

    @staticmethod
    def is_defect_constraint(name):
        return '.defects:' in name

    @staticmethod
    def is_path_constraint(name):
        return '.path:' in name

    @staticmethod
    def is_state(name):
        return '.states:' in name

    @staticmethod
    def is_control(name):
        return '.controls:' in name

    @staticmethod
    def parse_defect_names(jac):
        return {of for of, _ in jac if AutoScaler.is_defect_constraint(of)}

    @staticmethod
    def parse_constraint_names(jac):
        return {of for of, _ in jac if AutoScaler.is_path_constraint(of)}

    @staticmethod
    def parse_var_names(jac):
        return {wrt for _, wrt in jac}
