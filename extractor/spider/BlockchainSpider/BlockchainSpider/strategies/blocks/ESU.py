import time

import networkx as nx


class ESUMotifCounter:
    def __init__(self, motif_size: int = 3):
        self.motif_size = motif_size

    def count(self, edges: list):
        # init input graph
        g = nx.MultiDiGraph()
        _edges = [(e.get('address_from', ''), e.get('address_to', '')) for e in edges]
        g.add_edges_from(_edges)
        if g.number_of_nodes() < 3 or g.number_of_edges() < 2:
            return {}

        # convert multidigraph to digraph
        nodes_num = {node: i for i, node in enumerate(g.nodes())}
        edges = dict()
        for u, v, k in g.edges(keys=True):
            edges[(nodes_num[u], nodes_num[v])] = max(edges.get((u, v), 0), k)
        gg = nx.DiGraph()
        gg.add_weighted_edges_from([(edge[0], edge[1], weight) for edge, weight in edges.items()])

    @staticmethod
    def ESU(g: nx.Graph, motif_size: int):
        # pre-compute some useful data
        node_num = {node: i for i, node in enumerate(g.nodes())}
        node_neighbors = {node: set(g.neighbors(node)) for node in g.nodes()}

        def _extend_subgraph(subgraph_nodes: set, extension_nodes: set, v):
            if len(subgraph_nodes) == motif_size:
                yield g.subgraph(subgraph_nodes)

            # pre-compute neighbors of subgraph nodes
            subgraph_nodes_neighbors = set()
            for subgraph_node in subgraph_nodes:
                subgraph_nodes_neighbors = subgraph_nodes_neighbors.union(node_neighbors[subgraph_node])
            # subgraph_nodes_and_neighbors = subgraph_nodes.union(subgraph_nodes_neighbors)

            while len(extension_nodes) != 0:
                node = extension_nodes.pop()
                excl = node_neighbors[node].difference(subgraph_nodes_neighbors)
                _extension_nodes = extension_nodes.union({_node for _node in excl if node_num[_node] > node_num[v]})
                yield from _extend_subgraph(subgraph_nodes.union({node}), _extension_nodes, v)

        for v in g.nodes():
            extension = {u for u in node_neighbors[v] if node_num[u] > node_num[v]}
            yield from _extend_subgraph({v}, extension, v)


if __name__ == '__main__':
    # g = nx.DiGraph()
    # g.add_edges_from([(1, 2), (2, 3), (1, 3), (2, 4)])
    g = nx.watts_strogatz_graph(10, 8, 0.2)
    gg = nx.DiGraph()
    gg.add_edges_from([(u, v) for u, v in g.edges()])
    print(g.number_of_nodes(), g.number_of_edges())

    start = time.time()
    for subgraph in ESUMotifCounter.ESU(g, 3):
        print(subgraph.edges)
    print('using:', time.time() - start)
