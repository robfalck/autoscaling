import openmdao.api as om


def print_subsystems(sys):
    if isinstance(sys, om.Group):
        for subsys in sys._loc_subsys_map:
            print_subsystems(getattr(sys, subsys))
    else:
        print(sys.name)
