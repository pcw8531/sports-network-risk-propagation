Here's the updated README keeping your simple style:

---

# Network-Agent Dynamics in Sports Systems

**Code for Manuscript Review:** Impact of Immediate Interventions in Risk Propagation: Network Topology Effects on Sports System Vulnerability

## Repository Contents

This repository contains three simulation models and empirical validation supporting the manuscript:

### Simulation Models

1. **Fundamental Model** (`fundamental_model_animated.py`)
   - Demonstrates basic failure propagation without recovery
   - Shows network state evolution over 20 time steps
   - Animated visualization of cascade dynamics

2. **Recovery Delay Analysis** (`recovery_delay_simulation.py`)
   - Compares immediate (r_t=1) vs delayed (r_t=2) interventions
   - Calculates Network Vulnerability Index (NVI)
   - Reproduces manuscript Figure 3

3. **Network Topology Effects** (`network_topology_ternary.py`)
   - Ternary phase space analysis
   - Compares Regular, Random, Small-world, and Scale-free networks
   - Reproduces manuscript Figure 5 and Table 8

### Empirical Validation

4. **Empirical Validation** (`Empirical_validation.py`)
   - Validates model predictions against real-world sports data
   - Generates Figure 6 (three-panel validation)
   - Statistical analysis: R² = 0.981, RMSE = 0.089
   - Reproduces manuscript Figure 6 and Table 7

## Data Sources

### NBA Injury Data
- **File:** `NBA Player Injury Stats(1951 - 2023).csv`
- **Source:** https://www.kaggle.com/datasets/ghopkins/nba-injuries-2010-2018
- **Coverage:** 2010-2018, n = 77,463 injury events across 30 teams
- **Purpose:** Micro-level cascade pattern validation

### COVID-19 Sports Disruption Data
- **File:** `covid19_sports_shutdowns.csv`
- **Source:** Compiled from Wikipedia + official league announcements (verified via WHO reports)
- **Coverage:** 12 major professional leagues (2020-2021): NBA, Premier League, La Liga, Serie A, Bundesliga, Ligue 1, MLB, NHL, KBO, K League 1, KBL, NPB
- **Purpose:** Macro-level disruption validation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Run simulations
python fundamental_model_animated.py
python recovery_delay_simulation.py
python network_topology_ternary.py

# Run empirical validation
python Empirical_validation.py
```

## License

MIT License

---

- Kept everything else simple and concise
