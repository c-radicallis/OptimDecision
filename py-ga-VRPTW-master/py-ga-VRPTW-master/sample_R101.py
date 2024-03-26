# -*- coding: utf-8 -*-

'''sample_R101.py'''

import random
from gavrptw.core import run_gavrptw
import matplotlib.pyplot as plt
import json

random.seed(64)

instance_name = 'R101'

unit_cost = 8.0
init_cost = 60.0
wait_cost = 0.5
delay_cost = 1.5

ind_size = 25
pop_size = 80
cx_pb = 0.85
mut_pb = 0.01
n_gen = 100

export_csv = True

list_1 = run_gavrptw(instance_name=instance_name, unit_cost=unit_cost, init_cost=init_cost, \
    wait_cost=wait_cost, delay_cost=delay_cost, ind_size=ind_size, pop_size=pop_size, \
    cx_pb=cx_pb, mut_pb=mut_pb, n_gen=n_gen, export_csv=export_csv)


# Load the data from the json file 
json_folder = '.\data\json'
file_path = json_folder + '\\' + instance_name + '.json'

with open(file_path, 'r') as file:
    data = json.load(file)

customer = 'customer_'


# part where it plots the routes

cmap = plt.cm.get_cmap('tab10')

# Generate list of 50 distinct and saturated colors in hexadecimal format
color_vector = [cmap(i)[:3] for i in range(50)]


plt.figure(figsize=[6, 6])

for i in range(len(list_1)):
    list_1[i] = [0] + list_1[i] + [0]

for j in range(len(list_1)):
    for i in range(1, len(list_1[j])):



        number_i = list_1[j][i]
        number_i_1 = list_1[j][i - 1]

        customer_i = customer + str(number_i)
        customer_i_1 = customer + str(number_i_1)


        if customer_i == 'customer_0':
            customer_i = "depart"
        else:
            pass
            
        if customer_i_1 == 'customer_0':
            customer_i_1 = "depart"
        else:
            pass

        # Draw the path based on the indices in the path
        x_point_1 = data[customer_i_1]['coordinates']['x']
        x_point_2 = data[customer_i]['coordinates']['x']
        y_point_1 = data[customer_i_1]['coordinates']['y']
        y_point_2 = data[customer_i]['coordinates']['y']
        plt.arrow(x_point_1 , y_point_1, x_point_2 - x_point_1, y_point_2-y_point_1, head_width=1, head_length=1, color=color_vector[j], length_includes_head=True)

plt.grid(True)
plt.xlabel('X coordinate')
plt.ylabel('Y coordinate')
plt.show()
