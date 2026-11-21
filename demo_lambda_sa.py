import networkx as nx
from lambda_sa_extractor import compute_topological_sieve_stats


def build_synthetic_expertise_network() -> nx.DiGraph:
    """
    Constructs a directed GitHub-like expertise network (N = 150):
      - Layer 2 (L2ECC, 5 nodes / 3.3%): Core maintainers linked via mutually
        redundant edge-disjoint feedback paths (lambda >= 2).
      - Layer 1 (LSCC, +20 nodes): Active contributors connected to the core
        via single-link reciprocal chains (lambda = 1).
      - Layer 0 (Global, +125 nodes): Peripheral question-askers with unilateral
        ties directed toward experts (lambda = 0).
    """
    G = nx.DiGraph()

    # Layer 2: 5 elite core maintainers (complete digraph)
    elite = list(range(0, 5))
    for u in elite:
        for v in elite:
            if u != v:
                G.add_edge(u, v)

    # Layer 1: 20 active contributors in single-link cycles with the elite core
    for idx, c in enumerate(range(5, 25)):
        hub = elite[idx % len(elite)]
        G.add_edge(c, hub)
        G.add_edge(hub, c)

    # Layer 0: 125 peripheral seekers asking questions (edges seeker -> expert)
    for p in range(25, 150):
        # Seekers primarily query elite core and occasionally active contributors
        G.add_edge(p, elite[p % len(elite)])
        G.add_edge(p, elite[(p + 2) % len(elite)])
        if p % 2 == 0:
            G.add_edge(p, 5 + (p % 20))

    return G


if __name__ == "__main__":
    G = build_synthetic_expertise_network()
    print(f"Directed Expertise Network: |V| = {G.number_of_nodes()}, |E| = {G.number_of_edges()}\n")

    results = compute_topological_sieve_stats(G)
    header = (
        f"{'Layer':<15} | {'|V| (%)':<13} | {'|E| (%)':<13} | "
        f"{'PageRank':<9} | {'Authority':<9} | {'Indegree':<8} | {'Top-10 Recall (PR/Auth/In)':<25}"
    )
    print(header)
    print("-" * len(header))

    for r in results:
        v_str = f"{r['core_nodes']} ({r['vertex_share']:.1%})"
        e_str = f"{r['core_edges']} ({r['edge_share']:.1%})"
        rec_str = f"{r['top10_pr_recall']:.0%} / {r['top10_auth_recall']:.0%} / {r['top10_indeg_recall']:.0%}"
        print(
            f"{r['label']:<15} | {v_str:<13} | {e_str:<13} | "
            f"{r['mean_pagerank']:>9.4f} | {r['mean_authority']:>9.4f} | {r['mean_indegree']:>8.1f} | {rec_str:<25}"
        )
