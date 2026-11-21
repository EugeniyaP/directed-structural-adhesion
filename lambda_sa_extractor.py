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
    if any(G.in_degree(u) < lam or G.out_degree(u) < lam for u in nodes):
        return False
    return nx.edge_connectivity(G) >= lam


def _find_minimum_edge_cut_edges(G: nx.DiGraph, lam: int) -> Set[tuple]:
    """
    Finds a small directed edge cut of size < lam whose removal breaks
    strong lambda-edge-connectivity.
    """
    if lam == 2:
        bridges = set()
        for u, v in list(G.edges()):
            G.remove_edge(u, v)
            if not nx.is_strongly_connected(G):
                bridges.add((u, v))
            G.add_edge(u, v)
        return bridges

    cut = nx.minimum_edge_cut(G)
    return set(cut) if len(cut) < lam else set()


def extract_lambda_sa_cores(G: nx.DiGraph, lam: int = 2) -> List[nx.DiGraph]:
    """
    Extracts all maximal induced subgraphs possessing Strong Directed
    Structural Adhesion of order `lam` (lambda-SA), per Definition 2.
    """
    if lam <= 0:
        return [G.copy()] if G.number_of_nodes() > 0 else []

    if lam == 1:
        sccs = [G.subgraph(c).copy() for c in nx.strongly_connected_components(G) if len(c) > 1]
        return sorted(sccs, key=lambda g: g.number_of_nodes(), reverse=True)

    cores = []
    queue = [G.subgraph(c).copy() for c in nx.strongly_connected_components(G) if len(c) > lam]

    while queue:
        sub = queue.pop(0)
        changed = True
        while changed and sub.number_of_nodes() > 0:
            to_remove = [u for u in sub.nodes() if sub.in_degree(u) < lam or sub.out_degree(u) < lam]
            if to_remove:
                sub.remove_nodes_from(to_remove)
            else:
                changed = False

        if sub.number_of_nodes() <= lam:
            continue

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


def compute_topological_sieve_stats(G: nx.DiGraph) -> List[Dict]:
    """
    Evaluates boundary contraction and monotonic expertise concentration across
    the three nested structural adhesion layers studied in Perekhodko (2026):
      - Layer 0: Global Graph (G)
      - Layer 1: Largest Strongly Connected Component (LSCC, lambda = 1)
      - Layer 2: Largest 2-Edge-Connected Component (L2ECC, lambda = 2)
    """
    n_total = G.number_of_nodes()
    e_total = G.number_of_edges()
    if n_total == 0:
        return []

    pagerank = nx.pagerank(G)
    _, authorities = nx.hits(G, max_iter=200, normalized=True)
    in_deg = dict(G.in_degree())

    k_top = min(10, n_total)
    top10_pr = set(sorted(pagerank, key=pagerank.get, reverse=True)[:k_top])
    top10_auth = set(sorted(authorities, key=authorities.get, reverse=True)[:k_top])
    top10_indeg = set(sorted(in_deg, key=in_deg.get, reverse=True)[:k_top])

    layers = [
        (0, "Global (G)", [G]),
        (1, "LSCC (lam=1)", extract_lambda_sa_cores(G, lam=1)),
        (2, "L2ECC (lam=2)", extract_lambda_sa_cores(G, lam=2)),
    ]

    stats = []
    for level, label, cores in layers:
        if not cores:
            stats.append({
                "level": level,
                "label": label,
                "core_nodes": 0,
                "core_edges": 0,
                "vertex_share": 0.0,
                "edge_share": 0.0,
                "mean_pagerank": 0.0,
                "mean_authority": 0.0,
                "mean_indegree": 0.0,
                "top10_pr_recall": 0.0,
                "top10_auth_recall": 0.0,
                "top10_indeg_recall": 0.0,
            })
            continue

        largest = cores[0]
        c_nodes = set(largest.nodes())
        stats.append({
            "level": level,
            "label": label,
            "core_nodes": len(c_nodes),
            "core_edges": largest.number_of_edges(),
            "vertex_share": len(c_nodes) / n_total,
            "edge_share": largest.number_of_edges() / e_total if e_total > 0 else 0.0,
            "mean_pagerank": sum(pagerank[u] for u in c_nodes) / len(c_nodes),
            "mean_authority": sum(authorities[u] for u in c_nodes) / len(c_nodes),
            "mean_indegree": sum(in_deg[u] for u in c_nodes) / len(c_nodes),
            "top10_pr_recall": len(c_nodes & top10_pr) / k_top,
            "top10_auth_recall": len(c_nodes & top10_auth) / k_top,
            "top10_indeg_recall": len(c_nodes & top10_indeg) / k_top,
        })
    return stats
