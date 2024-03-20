import numpy as np
import copy
from vrptw_base import VrptwGraph
from threading import Event

class Ant:
    def __init__(self, graph: VrptwGraph, start_index=0):
        super()
        self.graph = graph
        self.current_index = start_index
        self.vehicle_load = 0
        self.vehicle_travel_time = 0
        self.travel_path = [start_index]
        self.arrival_time = [0]

        self.index_to_visit = list(range(graph.node_num))
        self.index_to_visit.remove(start_index)

        self.total_travel_distance = 0

    def clear(self):
        self.travel_path.clear()
        self.index_to_visit.clear()

    def move_to_next_index(self, next_index):
        # Update the ant's path
        self.travel_path.append(next_index)
        self.total_travel_distance += self.graph.node_dist_mat[self.current_index][next_index]

        dist = self.graph.node_dist_mat[self.current_index][next_index]
        self.arrival_time.append(self.vehicle_travel_time + dist)

        if self.graph.nodes[next_index].is_depot:
            # If the next position is a depot, reset the vehicle load and travel time
            self.vehicle_load = 0
            self.vehicle_travel_time = 0
        else:
            # Update vehicle load, travel distance, and time
            self.vehicle_load += self.graph.nodes[next_index].demand
            # If it's earlier than the customer's required time window (ready_time), then waiting is needed
            self.vehicle_travel_time += dist + max(self.graph.nodes[next_index].ready_time - self.vehicle_travel_time - dist, 0) + self.graph.nodes[next_index].service_time
            self.index_to_visit.remove(next_index)

        self.current_index = next_index

    def index_to_visit_empty(self):
        return len(self.index_to_visit) == 0

    def get_active_vehicles_num(self):
        return self.travel_path.count(0)-1

    def check_condition(self, next_index) -> bool:
        """
        Check if moving to the next point meets the constraints
        """
        if self.vehicle_load + self.graph.nodes[next_index].demand > self.graph.vehicle_capacity:
            return False

        dist = self.graph.node_dist_mat[self.current_index][next_index]
        wait_time = max(self.graph.nodes[next_index].ready_time - self.vehicle_travel_time - dist, 0)
        service_time = self.graph.nodes[next_index].service_time

        # Check if after visiting a customer, it's possible to return to the depot
        if self.vehicle_travel_time + dist + wait_time + service_time + self.graph.node_dist_mat[next_index][0] > self.graph.nodes[0].due_time:
            return False

        # Can't serve customers outside their due time
        if self.vehicle_travel_time + dist > self.graph.nodes[next_index].due_time:
            return False

        return True

    def cal_next_index_meet_constrains(self):
        """
        Find all customers reachable from the current position (ant.current_index)
        """
        next_index_meet_constrains = []
        for next_ind in self.index_to_visit:
            if self.check_condition(next_ind):
                next_index_meet_constrains.append(next_ind)
        return next_index_meet_constrains

    def cal_nearest_next_index(self, next_index_list):
        """
        Select the nearest customer from the candidate customers to the current position (ant.current_index)
        """
        current_ind = self.current_index

        nearest_ind = next_index_list[0]
        min_dist = self.graph.node_dist_mat[current_ind][next_index_list[0]]

        for next_ind in next_index_list[1:]:
            dist = self.graph.node_dist_mat[current_ind][next_ind]
            if dist < min_dist:
                min_dist = dist
                nearest_ind = next_ind

        return nearest_ind

    @staticmethod
    def cal_total_travel_distance(graph: VrptwGraph, travel_path):
        distance = 0
        current_ind = travel_path[0]
        for next_ind in travel_path[1:]:
            distance += graph.node_dist_mat[current_ind][next_ind]
            current_ind = next_ind
        return distance

    def try_insert_on_path(self, node_id, stop_event: Event):
        """
        Try to insert the node_id into the current travel_path
        Insertion should not violate load, time, and distance constraints
        If there are multiple positions, find the optimal one
        """
        best_insert_index = None
        best_distance = None

        for insert_index in range(len(self.travel_path)):

            if stop_event.is_set():
                return

            if self.graph.nodes[self.travel_path[insert_index]].is_depot:
                continue

            # Find the nearest depot before insert_index
            front_depot_index = insert_index
            while front_depot_index >= 0 and not self.graph.nodes[self.travel_path[front_depot_index]].is_depot:
                front_depot_index -= 1
            front_depot_index = max(front_depot_index, 0)

            # Check_ant starts from front_depot_index
            check_ant = Ant(self.graph, self.travel_path[front_depot_index])

            # Let check_ant traverse points in path from front_depot_index + 1 to insert_index - 1
            for i in range(front_depot_index+1, insert_index):
                check_ant.move_to_next_index(self.travel_path[i])

            # Start trying to visit nodes from the sorted index_to_visit
            if check_ant.check_condition(node_id):
                check_ant.move_to_next_index(node_id)
            else:
                continue

            # If it can reach node_id, ensure that the vehicle can return to the depot
            for next_ind in self.travel_path[insert_index:]:

                if stop_event.is_set():
                    return

                if check_ant.check_condition(next_ind):
                    check_ant.move_to_next_index(next_ind)

                    # If it returns to the depot
                    if self.graph.nodes[next_ind].is_depot:
                        temp_front_index = self.travel_path[insert_index-1]
                        temp_back_index = self.travel_path[insert_index]

                        check_ant_distance = self.total_travel_distance - self.graph.node_dist_mat[temp_front_index][temp_back_index] + \
                                             self.graph.node_dist_mat[temp_front_index][node_id] + self.graph.node_dist_mat[node_id][temp_back_index]

                        if best_distance is None or check_ant_distance < best_distance:
                            best_distance = check_ant_distance
                            best_insert_index = insert_index
                        break

                # If it can't return to the depot, return to the previous level
                else:
                    break

        return best_insert_index

    def insertion_procedure(self, stop_even: Event):
        """
        Try to find a suitable position to insert each unvisited node into the current travel_path
        Insertion should not violate load, time, and distance constraints
        """
        if self.index_to_visit_empty():
            return

        success_to_insert = True
        # Repeat until no node from unvisited can be successfully inserted
        while success_to_insert:

            success_to_insert = False
            # Get the unvisited nodes
            ind_to_visit = np.array(copy.deepcopy(self.index_to_visit))

            # Sort unvisited customers' demands
