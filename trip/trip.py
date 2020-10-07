import os
from ..search.graph import Graph

class Trip:
    def __init__(self):
        pass
    def __build_graph(self, country_path):
        g = Graph()
        
        nodes = [ f.path for f in os.scandir('./costa_rica') if f.is_dir() ]
        for node in nodes:
            direct_connections = [ f.name for f in os.scandir(node) if f.is_dir() ]
            node_name = node.rsplit('\\', 1)[-1]
        pass