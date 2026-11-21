import networkx as nx
from lambda_sa_extractor import compute_topological_sieve_stats


def build_synthetic_expertise_network() -> nx.DiGraph:
    """
    Constructs a directed interaction network with:
      - A tightly knit 5-maintainer elite core (lambda = 3)
      - A secondary 5-contributor architectural ring (lambda = 2)
      - 40 peripheral question-askers connected via fragile single-link cycles (lambda = 1)
    """
    G = nx.DiGraph()

    # Layer 3: 5 core maintainers (complete digraph -> 4-edge-strongly-connected)
    elite = list(range(0, 5))
    for u in elite:
        for v in elite:
            if u != v:
                G.add_edge(u, v)

    # Layer 2: 5 senior contributors with 2 edge-disjoint paths to/from elite core
    seniors = list(range(5, 10))
    for idx, s in enumerate(seniors):
        e1 = elite[idx % len(elite)]
        e2 = elite[(idx + 1) % len(elite)]
        G.add_edge(s, e1)
        G.add_edge(s, e2)
        G.add_edge(e1, s)
        G.add_edge(e2, s)

    # Layer 1: 40 peripheral users (fragile single-path attachment)
    for p in range(10, 50):
        target = p % 10
        G.add_edge(p, target)
        G.add_edge(target, p)

    return G


if __name__ == "__main__":
    G = build_synthetic_expertise_network()
    print(f"Synthetic Directed Network: |V| = {G.number_of_nodes()}, |E| = {G.number_of_edges()}\n")

    results = compute_topological_sieve_stats(G, max_lambda=3)
    header = f"{'Lambda':<8} | {'|V(Core)|':<10} | {'V Share':<9} | {'E Share':<9} | {'Mean PR':<10} | {'Top-10 Recall':<13}"
    print(header)
    print("-" * len(header))

    for r in results:
        print(
            f"{r['lambda']:<8} | "
            f"{r['core_nodes']:<10} | "
            f"{r['vertex_share']:>8.1%} | "
            f"{r['edge_share']:>8.1%} | "
            f"{r['mean_pagerank']:>10.4f} | "
            f"{r['top10_recall']:>12.1%}"
        )
