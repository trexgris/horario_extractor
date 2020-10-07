
import os
from collections import deque

class bfs:
    def __init__(self, nodes_data_path):
        self.__build_graph(nodes_data_path)
    def __build_graph(self, nodes_data_path):
        self.__graph = {}
        nodes = [ f.path for f in os.scandir(nodes_data_path) if f.is_dir() ]
        for node in nodes:
            direct_connections = [ f.name for f in os.scandir(node) if f.is_dir() ]
            node_name = node.rsplit('\\', 1)[-1]
            self.__graph[node_name] = set(direct_connections)
    def run(self, start, goal):
        if start == goal:
            return [start]
        visited = {start}
        queue = deque([(start, [])])
        while queue:
            current, path = queue.popleft()
            visited.add(current)
            for neighbor in self.__graph[current]:
                if neighbor == goal:
                    return path + [current, neighbor]
                if neighbor in visited:
                    continue
                queue.append((neighbor, path + [current]))
                visited.add(neighbor)
        return None
            
       

                            



if __name__ == "__main__":
    bfs = bfs('./costa_rica')
    res = bfs.run('Puerto Jiménez', 'Cañas')
    print(res)
    pass