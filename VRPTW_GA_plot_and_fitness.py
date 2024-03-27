# -*- coding: utf-8 -*-

'''sample_R101.py'''

import random
from gavrptw.core import run_gavrptw
import matplotlib.pyplot as plt
import json
import os
import pandas as pd
import time

# Set the random seed for reproducibility
random.seed(64)

# Set the instance name
instance_name = 'R25'



def main(unit_cost, init_cost, wait_cost, delay_cost, ind_size, pop_size, cx_pb, mut_pb, n_gen):
        
    # Set the parameters for the genetic algorithm
    '''unit_cost = 8.0
    init_cost = 60.0
    wait_cost = 0.5
    delay_cost = 1.5

    ind_size = 25
    pop_size = 80
    cx_pb = 10.0
    mut_pb = 10.0
    n_gen = 300'''

    export_csv = True

    # Run the genetic algorithm
    start_time = time.time()

    list_1 = run_gavrptw(instance_name=instance_name, unit_cost=unit_cost, init_cost=init_cost, \
        wait_cost=wait_cost, delay_cost=delay_cost, ind_size=ind_size, pop_size=pop_size, \
        cx_pb=cx_pb, mut_pb=mut_pb, n_gen=n_gen, export_csv=export_csv)
    
    elapsed_time = time.time() - start_time



    # Load the data from the json file 
    json_folder = '.\\data\\json'
    file_path = json_folder + '\\' + instance_name + '.json'

    with open(file_path, 'r') as file:
        data = json.load(file)

    customer = 'customer_'


    # Get a list of 50 distinct and saturated colors
    cmap = plt.colormaps.get_cmap('tab10')

    # Generate list of 50 distinct and saturated colors in hexadecimal format
    color_vector = [cmap(i)[:3] for i in range(50)]

    # Plot the solution
    plt.figure(figsize=[6, 6])
    plt.axis([0,70,0,70])
    plt.gca().set_aspect('equal')

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
            plt.arrow(x_point_1 , y_point_1, x_point_2 - x_point_1, y_point_2-y_point_1, head_width=1.5, head_length=1.5, color=color_vector[j], length_includes_head=True)
            plt.plot(x_point_1, y_point_1, ".", color=color_vector[j], markersize=10)

    plt.plot(data["depart"]['coordinates']['x'], data["depart"]['coordinates']['y'], "o", color="red", markersize=10)

    plt.grid(True)
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.title('VRPTW Solution for ' + instance_name)

    # Get the directory of the current Python script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a folder named 'plots' inside the script directory
    plots_dir = os.path.join(script_dir, 'images')
    os.makedirs(plots_dir, exist_ok=True)

    file_path = f'{instance_name}_uC{unit_cost}_iC{init_cost}_wC{wait_cost}' \
                f'_dC{delay_cost}_iS{ind_size}_pS{pop_size}_cP{cx_pb}_mP{mut_pb}_nG{n_gen}.png'

    # Save the plot to the 'plots' folder
    plt.savefig(os.path.join(plots_dir, file_path))


    ## part where it plots the fitness

    # Check if the file exists
    file_path = file_path.replace('.png','.csv')
    csv_file_path = '.\\results\\' + file_path

    if os.path.exists(csv_file_path):
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        # Specify columns to plot
        columns_to_plot = ['min_fitness','max_fitness','avg_fitness','std_fitness']  # Add more columns as needed
    else:
        print(f"File {file_path} does not exist. Please check the file path and name.")


    plt.figure(figsize=[6, 6])
    df[columns_to_plot].plot()
    plt.title('VRPTW Solution Fitness for ' + instance_name)
    plt.xlabel('Generation')
    #plt.legend(['Minimum Fitness', 'Maximum Fitness', 'Average Fitness', 'Standard Deviation Fitness'], loc='right')
    plt.grid(True)
    plt.xlim(0,max(df['generation']))
    plt.ylim(0)


    file_path = file_path.replace('.csv','.jpeg')
    image_file_path = '.\\results\\' + file_path

    plt.savefig(image_file_path)




import itertools

# Example vectors
unit_cost = [2.0, 4.0]
init_cost = [20.0, 40.0]
wait_cost = [0.5]
delay_cost = [1.0]

ind_size = [25]
pop_size = [80]
cx_pb = [0.1, 10.0]
mut_pb = [0.1, 10.0]
n_gen = [300]

# Create a list to store combinations
combinations = []


for unit_cost, init_cost, wait_cost, delay_cost, ind_size, pop_size, cx_pb, mut_pb, n_gen in itertools.product(unit_cost, init_cost, wait_cost, delay_cost, ind_size, pop_size, cx_pb, mut_pb, n_gen):
    combinations.append([unit_cost, init_cost, wait_cost, delay_cost, ind_size, pop_size, cx_pb, mut_pb, n_gen])

print(combinations)

# Run the main function for each combination
for combination in combinations:
    main(*combination)
    print(f"Finished running for combination: {combination}")