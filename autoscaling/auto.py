
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
