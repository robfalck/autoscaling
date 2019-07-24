import openmdao.api as om


def print_subsystems(sys):
    if isinstance(sys, om.Group):
        for subsys in sys._loc_subsys_map:
            print_subsystems(getattr(sys, subsys))
    else:
        print(sys.name)


def save_tji_keys(prob, filename):
    prob.run_model()
    tji = prob.compute_totals()
    keys = {(of, wrt) for of, wrt in tji}
    import pickle
    with open(filename, 'wb') as file:
        pickle.dump(keys, file, protocol=pickle.HIGHEST_PROTOCOL)
