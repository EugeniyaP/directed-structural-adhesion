# Strong Directed Structural Adhesion ($\lambda$-SA) & Elite Closure

Reference implementation for extracting maximal induced **$\lambda$-Edge-Strongly-Connected Subgraphs ($\lambda$-SA)** in asymmetric interaction networks and quantifying the **Topological Sieve Effect**.

## Overview
Unlike vertex-connectivity models (e.g., Moody & White's structural cohesion) or non-induced 2-edge-connected blocks, $\lambda$-SA isolates **maximal induced subgraphs** where every ordered pair of actors $(u, v)$ is mutually reachable via at least $\lambda$ completely edge-disjoint directed pathways. At the critical threshold $\lambda = 2$, this core filters out peripheral noise and traps the network's structural elite.

## Features
- **Recursive Induced 2-ESCC Extraction:** Refines 2-edge-connected blocks into strict maximal induced subgraphs via iterative strong-bridge removal.
- **Topological Sieve Diagnostics:** Measures vertex/edge compression ratios and prestige concentration (PageRank, HITS Authority, Indegree) across adhesive layers.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the standalone $\lambda$-SA & Topological Sieve demo:**
   ```bash
   python demo_lambda_sa.py
   ```




## Citation
```bibtex
@article{perekhodko2026architecture,
  title={The Architecture of Asymmetry: Directed Structural Adhesion and Elite Closure in Interaction Networks},
  author={Perekhodko, Eugenia},
  journal={SocArXiv Preprints},
  year={2026},
  doi={10.31235/osf.io/zft8x}
}
```
