from copy import deepcopy

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

INITIAL_NUMBER = -1


class State:

    def __init__(self, graph):
        self.graph = graph
        self.trajectory = np.full(len(graph), INITIAL_NUMBER, dtype=np.int)

        G = nx.Graph()
        for index in range(len(graph)):
            G.add_node(index)
        self.G = G

    def update(self, node):
        init_list = np.where(self.trajectory == INITIAL_NUMBER)[0]
        if len(init_list) != 0:
            self.trajectory[init_list[0]] = node
        return self.check_last_action(init_list)

    def total_cost(self):
        total_cost = 0
        for index, node in enumerate(self.trajectory):
            if index == 0:
                continue
            distance = self.graph[self.trajectory[index]
                                  ] - self.graph[self.trajectory[index-1]]
            total_cost += np.linalg.norm(distance, 2)
        distance = self.graph[self.trajectory[-1]
                              ] - self.graph[self.trajectory[0]]
        total_cost += np.linalg.norm(distance, 2)
        return total_cost

    def check_last_action(self, init_list):
        if len(init_list) <= 1:
            return True
        return False

    def render(self):
        nx.add_path(self.G, list(
            filter(lambda x: x != -1, self.trajectory)))
        pos = {}
        for index, node in enumerate(self.graph):
            pos[index] = node
        nx.draw(self.G, pos)
        plt.show()

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result
