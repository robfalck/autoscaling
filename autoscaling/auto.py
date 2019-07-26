
class AutoScaler(object):
    def __init__(self):
        self.refs = {}
        self.ref0s = {}
        self.defect_refs = {}

    def is_control_name(self, name):
        return '.controls:' in name

    def is_defect_name(self, name):
        return '.defects:' in name

    def is_path_constraint_name(self, name):
        return '.path:' in name

    def is_state_name(self, name):
        return '.states:' in name

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

    def local_defect_name(self, global_name):
        return global_name.split(':')[-1]

    def local_var_name(self, global_name):
        return global_name.split(':')[-1].split('.')[-1]
