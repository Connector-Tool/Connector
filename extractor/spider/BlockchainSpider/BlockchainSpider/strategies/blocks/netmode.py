import asyncio
import os
import platform

import networkx as nx

from BlockchainSpider.settings import BASE_DIR
from supports.pymotifcounter import PyMotifCounterNetMODE


class NetMODEBlockMotifCounter:
    single_counters = {}

    def __init__(self, **kwargs):
        self.counter = NetMODEMotifCounter(**kwargs)

    async def count(self, edges: [dict]):
        hash_txs = dict()
        for edge in edges:
            txs = hash_txs.get(edge.get('transaction_hash'))
            if txs is None:
                txs = hash_txs[edge.get('transaction_hash')] = list()
            txs.append(edge)

        txhashs = list(hash_txs.keys())
        tasks = [self.counter.count(hash_txs[txhash]) for txhash in txhashs]
        txhashs_frequency = await asyncio.gather(*[asyncio.create_task(task) for task in tasks])
        for i, txhash in enumerate(txhashs):
            yield {
                'transaction_hash': txhash,
                'frequency': txhashs_frequency[i],
            }


class NetMODEMotifCounter:
    def __init__(
            self,
            motif_size: int = 3,
            n_threads: int = 1,
            burnin: int = 0,
            n_random: int = 0,
            edge_select_method: int = 3,
    ):
        """
        A motif counter using NetMODE algorithm
        :param motif_size: k-node subgraphs (=3,4,5 or 6)
        :param n_threads: Number of threads to use
        :param burnin: Number of random graphs to be discarded
        :param n_random: Number of comparison graphs (An integer in [0, 2^31))
        :param edge_select_method: Bidirectional edge random_method (0:fixed, 1:no regard, 2: global constant, 3:local constant (default), 4:uniform
        """
        assert motif_size in {3, 4, 5, 6}, \
            "The motif size of NetMODEMotifCounter must be equal to 3, 4, 5 or 6"
        assert edge_select_method in {0, 1, 2, 3, 4}, \
            "The method for edge selecting must be equal to 0, 1, 2, 3 or 4"

        self.motif_size = motif_size
        self.n_threads = n_threads
        self.burnin = burnin
        self.n_random = n_random
        self.edge_select_method = edge_select_method
        self.bin_path = os.path.join(
            BASE_DIR,
            os.sep.join([
                'supports',
                'pymotifcounter',
                'binaries',
                'NetMODE',
                'NetMODE',
                'NetMODE' if platform.system().lower() != 'windows' else 'NetMODE.exe'
            ])
        )

    async def count(self, edges: [dict]) -> dict:
        """
        Count motif from given an list of edges with the same transaction hash
        :param edges: the edges of a graph
        :return: a dict with (motif id -> frequency)
        """

        # init input graph
        g = nx.MultiDiGraph()
        _edges = [(e.get('address_from', ''), e.get('address_to', '')) for e in edges]
        g.add_edges_from(_edges)
        if g.number_of_nodes() < 3 or g.number_of_edges() < 2:
            return {}

        # init motif counters
        motif_counter = PyMotifCounterNetMODE(
            binary_location=self.bin_path
        )
        motif_counter.get_parameter('motif_size').value = self.motif_size
        motif_counter.get_parameter('n_threads').value = self.n_threads
        motif_counter.get_parameter('burnin').value = self.burnin
        motif_counter.get_parameter('n_random').value = self.n_random
        motif_counter.get_parameter('edge_select_method').value = self.edge_select_method

        # Enumerate motifs using the selected counter
        rlt = {}
        try:
            _rlt = await motif_counter(g)
            _rlt = _rlt.iloc[:, :2]
            rlt = {_rlt.iloc[i, 0]: _rlt.iloc[i, 1] for i in range(_rlt.shape[0])}
        except:
            pass
        return rlt
