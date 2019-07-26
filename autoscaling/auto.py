
class AutoScaler(object):
    def __init__(self):
        self.refs = {}
        self.ref0s = {}
        self.defect_refs = {}

    def list_ref_keys(self):
        print('=======')
        print('REFs')
        print('=======')
        for key in self.refs:
            print(key)

    def list_ref0_keys(self):
        print('=======')
        print('REF0s')
        print('=======')
        for key in self.ref0s:
            print(key)

    def list_defect_ref_keys(self):
        print('=======')
        print('DEFECT_REFs')
        print('=======')
        for key in self.defect_refs:
            print(key)

    @staticmethod
    def is_control_name(name):
        return '.controls:' in name

    @staticmethod
    def is_defect_name(name):
        return '.defects:' in name

    @staticmethod
    def is_path_constraint_name(name):
        return '.path:' in name

    @staticmethod
    def is_state_name(name):
        return '.states:' in name

    @staticmethod
    def local_defect_name(global_name):
        return global_name.split(':')[-1]

    @staticmethod
    def local_var_name(global_name):
        return global_name.split(':')[-1].split('.')[-1]
