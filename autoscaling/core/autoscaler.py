"""Define the AutoScaler abstract base class, which defines a fundamental interface sufficient for an autoscaling helper class to work with autoscale()."""

from __future__ import print_function

from abc import ABC


class AutoScaler(ABC):
    """
    Abstract base class defining the fundamental interface common to autoscaling helper classes such as IsoScaler and PJRNScaler.

    Attributes
    ----------
    refs : dict
        Maps a variable's global name to its ref value.
    ref0s : dict
        Maps a variable's global name to its ref0 value.
    defect_refs : dict
        Maps a variable's defect's global name to its defect_ref value.
    """

    def __init__(self, *argv, **kwargs):
        """
        Instantiate attributes to defaults; initialize.

        Parameters
        ----------
        *argv : tuple
            Additional non-keyword arguments to be passed for initialization (see initialize() method).
        **kwargs : dict
            Additional keyword arguments to be passed for initialization (see initialize() method).
        """
        self.refs = {}
        self.ref0s = {}
        self.defect_refs = {}

        self.initialize(*argv, **kwargs)

    def list_all_refs(self):
        """
        Print the refs, ref0s, and defect_refs reference value dictionaries in a more readable format.
        """
        self.list_refs()
        self.list_ref0s()
        self.list_defect_refs()

    def list_refs(self):
        """
        Print the refs reference value dictionary in a more readable format.

        Each dict entry is printed as two rows of the form
            [key]
            => [value]
        where [key] is the key and [value] is the value at that key.
        """
        print('----\nREFs\n----')
        self._print_dict(self.refs)

    def list_ref0s(self):
        """
        Print the ref0s reference value dictionary in a more readable format.

        Each dict entry is printed as two rows of the form
            [key]
            => [value]
        where [key] is the key and [value] is the value at that key.
        """
        print('-----\nREF0s\n-----')
        self._print_dict(self.ref0s)

    def list_defect_refs(self):
        """
        Print the defect_refs reference value dictionary in a more readable format.

        Each dict entry is printed as two rows of the form
            [key]
            => [value]
        where [key] is the key and [value] is the value at that key.
        """
        print('-----------\nDEFECT_REFs\n-----------')
        self._print_dict(self.defect_refs)

    @staticmethod
    def _print_dict(dict_to_print):
        for key in dict_to_print:
            print('{0}\n=>\t{1}'.format(key, dict_to_print[key]))
        print()

    def list_ref_keys(self):
        """
        Print the keys of the refs dict attribute, one per line.
        """
        print('=======')
        print('REFs')
        print('=======')
        for key in self.refs:
            print(key)

    def list_ref0_keys(self):
        """
        Print the keys of the ref0s dict attribute, one per line.
        """
        print('=======')
        print('REF0s')
        print('=======')
        for key in self.ref0s:
            print(key)

    def list_defect_ref_keys(self):
        """
        Print the keys of the defect_refs dict attribute, one per line.
        """
        print('=======')
        print('DEFECT_REFs')
        print('=======')
        for key in self.defect_refs:
            print(key)

    @staticmethod
    def is_control_name(global_name):
        """
        Return True if the named global variable is a (dynamic) control.

        Parameters
        ----------
        global_name : str
            Global variable name.

        Returns
        -------
        bool
            True if the named global variable is a (dynamic) control.
        """
        return '.controls:' in global_name

    @staticmethod
    def is_defect_name(global_name):
        """
        Return True if the named global variable is a collocation defect constraint.

        Parameters
        ----------
        global_name : str
            Global variable name.

        Returns
        -------
        bool
            True if the named global variable is a collocation defect constraint.
        """
        return '.defects:' in global_name

    @staticmethod
    def is_path_constraint_name(global_name):
        """
        Return True if the named global variable is a path constraint.

        Parameters
        ----------
        global_name : str
            Global variable name.

        Returns
        -------
        bool
            True if the named global variable is a path constraint.
        """
        return '.path:' in global_name

    @staticmethod
    def is_state_name(global_name):
        """
        Return True if the named global variable is a state.

        Parameters
        ----------
        global_name : str
            Global variable name.

        Returns
        -------
        bool
            True if the named global variable is a state.
        """
        return '.states:' in global_name

    @staticmethod
    def local_defect_name(global_name):
        """
        Parse the local name of a collocation defect constraint from its global name.

        Parameters
        ----------
        global_name : str
            Global name of collocation defect constraint.

        Returns
        -------
        str
            Local name of the named defect.
        """
        return global_name.split(':')[-1]

    @staticmethod
    def local_var_name(global_name):
        """
        Parse the local name of a non-defect variable from its global name.

        Parameters
        ----------
        global_name : str
            Global name of non-defect variable.

        Returns
        -------
        str
            Local name of the named non-defect variable.
        """
        return global_name.split(':')[-1].split('.')[-1]
