

import random
from gavrptw.core import run_gavrptw


def main():
    '''main()'''
    random.seed(64)

    instance_name = 'R3'
    ind_size = 3

    pop_size = 25
    cx_pb = 0.85
    mut_pb = 0.02
    n_gen = 100

    export_csv = True

    run_gavrptw(instance_name=instance_name, ind_size=ind_size, pop_size=pop_size, \
        cx_pb=cx_pb, mut_pb=mut_pb, n_gen=n_gen, export_csv=export_csv)


if __name__ == '__main__':
    main()
