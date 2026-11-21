import networkx as nx
from typing import List, Dict, Set


def _has_lambda_edge_connectivity(G: nx.DiGraph, lam: int) -> bool:
    """
    Checks if a directed graph G is strongly lambda-edge-connected
    (i.e., every ordered pair u, v has at least `lam` edge-disjoint directed paths).
    """
    nodes = list(G.nodes())
    if len(nodes) <= 1:
        return False
    # Fast degree lower-bound check
    if any(G.in_degree(u) < lam or G.out_degree(u) < lam for u in nodes):
        return False
    return nx.edge_connectivity(G) >= lam


def _find_minimum_edge_cut_edges(G: nx.DiGraph, lam: int) -> Set[tuple]:
    """
    Finds a small directed edge cut of size < lam whose removal breaks
    strong lambda-edge-connectivity.
    """
    if lam == 2:
        # Exact strong-bridge detection for lambda = 2
        bridges = set()
        for u, v in list(G.edges()):
            G.remove_edge(u, v)
            if not nx.is_strongly_connected(G):
                bridges.add((u, v))
            G.add_edge(u, v)
        return bridges

    # General case for lambda >= 3 via minimum edge cut
    cut = nx.minimum_edge_cut(G)
    return set(cut) if len(cut) < lam else set()


def extract_lambda_sa_cores(G: nx.DiGraph, lam: int = 2) -> List[nx.DiGraph]:
    """
    Extracts all maximal induced subgraphs possessing Strong Directed
    Structural Adhesion of order `lam` (lambda-SA).

    Parameters
    ----------
    G : nx.DiGraph
        Input directed interaction network.
    lam : int, default=2
        Order of directed edge-disjoint path redundancy (lambda >= 1).

    Returns
    -------
    List[nx.DiGraph]
        List of maximal induced lambda-SA subgraphs sorted by size descending.
    """
    if lam <= 1:
        sccs = [G.subgraph(c).copy() for c in nx.strongly_connected_components(G) if len(c) > 1]
        return sorted(sccs, key=lambda g: g.number_of_nodes(), reverse=True)

    cores = []
    # Prune vertices that cannot possibly belong to a lambda-SA core
    queue = [G.subgraph(c).copy() for c in nx.strongly_connected_components(G) if len(c) > lam]

    while queue:
        sub = queue.pop(0)
        # Iterative (lam, lam)-core degree pruning
        changed = True
        while changed and sub.number_of_nodes() > 0:
            to_remove = [u for u in sub.nodes() if sub.in_degree(u) < lam or sub.out_degree(u) < lam]
            if to_remove:
                sub.remove_nodes_from(to_remove)
            else:
                changed = False

        if sub.number_of_nodes() <= lam:
            continue

        # Re-split into strongly connected components after degree pruning
        sccs = [sub.subgraph(c).copy() for c in nx.strongly_connected_components(sub) if len(c) > lam]
        if len(sccs) > 1 or (len(sccs) == 1 and sccs[0].number_of_nodes() < sub.number_of_nodes()):
            queue.extend(sccs)
            continue

        if _has_lambda_edge_connectivity(sub, lam):
            cores.append(sub)
        else:
            cut_edges = _find_minimum_edge_cut_edges(sub, lam)
            if cut_edges:
                sub.remove_edges_from(cut_edges)
                for comp in nx.strongly_connected_components(sub):
                    if len(comp) > lam:
                        queue.append(sub.subgraph(comp).copy())

    return sorted(cores, key=lambda g: g.number_of_nodes(), reverse=True)


def compute_topological_sieve_stats(G: nx.DiGraph, max_lambda: int = 3) -> List[Dict]:
    """
    Computes core compression ratios and elite prestige concentration
    (PageRank, HITS Authority, In-degree) across hierarchical lambda-SA layers.
    """
    n_total = G.number_of_nodes()
    e_total = G.number_of_edges()
    if n_total == 0:
        return []

    pagerank = nx.pagerank(G)
    _, authorities = nx.hits(G, max_iter=200, normalized=True)
    in_deg = dict(G.in_degree())

    # Top-10 experts ranked by PageRank
    top_10_experts = set(sorted(pagerank, key=pagerank.get, reverse=True)[:min(10, n_total)])

    stats = []
    for lam in range(1, max_lambda + 1):
        cores = extract_lambda_sa_cores(G, lam=lam)
        if not cores:
            stats.append({
                "lambda": lam,
                "num_cores": 0,
                "core_nodes": 0,
                "core_edges": 0,
                "vertex_share": 0.0,
                "edge_share": 0.0,
                "mean_pagerank": 0.0,
                "mean_authority": 0.0,
                "mean_indegree": 0.0,
                "top10_recall": 0.0,
            })
            continue

        largest = cores[0]
        c_nodes = set(largest.nodes())
        stats.append({
            "lambda": lam,
            "num_cores": len(cores),
            "core_nodes": len(c_nodes),
            "core_edges": largest.number_of_edges(),
            "vertex_share": len(c_nodes) / n_total,
            "edge_share": largest.number_of_edges() / e_total if e_total > 0 else 0.0,
            "mean_pagerank": sum(pagerank[u] for u in c_nodes) / len(c_nodes),
            "mean_authority": sum(authorities[u] for u in c_nodes) / len(c_nodes),
            "mean_indegree": sum(in_deg[u] for u in c_nodes) / len(c_nodes),
            "top10_recall": len(c_nodes & top_10_experts) / len(top_10_experts),
        })
    return stats
