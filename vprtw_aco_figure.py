import matplotlib.pyplot as plt
from multiprocessing import Queue as MPQueue

class VrptwAcoFigure:
    def __init__(self, nodes: list, path_queue: MPQueue , alpha  , beta):
        """
        Matplotlib drawing calculations need to be in the main thread, 
        it's recommended to open another thread for finding paths. 
        When the thread finds a new path, it puts the path in the path_queue, 
        and the drawing thread will automatically draw it. 
        Each element in the queue is a path represented as a PathMessage (class).
        The nodes are represented as instances of the Node (class) in the nodes list. 
        We mainly use Node.x and Node.y to obtain the coordinates of the nodes.

        :param nodes: A list of nodes, including the depot
        :param path_queue: A queue used to store paths calculated by the working thread. 
        Each element in the queue is a path, where each path contains IDs of various nodes.
        """

        self.alpha = alpha
        self.beta = beta        
        self.nodes = nodes
        self.figure = plt.figure(figsize=(10, 10))
        self.figure_ax = self.figure.add_subplot(1, 1, 1)
        self.path_queue = path_queue
        self._depot_color = 'k'
        self._customer_color = 'steelblue'
        self._line_color = 'darksalmon'

    def _draw_point(self):
        # Draw the depot
        self.figure_ax.scatter([self.nodes[0].x], [self.nodes[0].y], c=self._depot_color, label='depot', s=40)

        # Draw customers
        self.figure_ax.scatter([node.x for node in self.nodes[1:]],
                               [node.y for node in self.nodes[1:]], c=self._customer_color, label='customer', s=20)
        plt.pause(0.5)

    def run(self):
        # Draw all nodes first
        self._draw_point()
        self.figure.show()

        # Read new paths from the queue and draw them
        while True:
            if not self.path_queue.empty():
                # Get the newest path from the queue, discard other paths
                info = self.path_queue.get()
                while not self.path_queue.empty():
                    info = self.path_queue.get()

                path, distance, used_vehicle_num = info.get_path_info()
                if path is None:
                    print('[draw figure]: exit')
                    break

                # Record lines to be removed first, don't remove directly in the first loop,
                # Otherwise, self.figure_ax.lines will change during the loop, 
                # causing some lines to fail to be successfully removed
                remove_obj = []
                for line in self.figure_ax.lines:
                    if line._label == 'line':
                        remove_obj.append(line)

                for line in remove_obj:
                    self.figure_ax.lines.remove(line)
                remove_obj.clear()

                # Redraw the lines
                self.figure_ax.set_title('Distance: %0.2f, Vehicles: %d, α: %0.1f, β: %0.1f  ' % (distance, used_vehicle_num , self.alpha , self.beta))
                self._draw_line(path)
            plt.pause(1)

    def _draw_line(self, path):
        # Draw the path based on the indices in the path
        for i in range(1, len(path)):
            x_list = [self.nodes[path[i - 1]].x, self.nodes[path[i]].x]
            y_list = [self.nodes[path[i - 1]].y, self.nodes[path[i]].y]
            self.figure_ax.plot(x_list, y_list, color=self._line_color, linewidth=1.5, label='line')
            plt.pause(0.2)
