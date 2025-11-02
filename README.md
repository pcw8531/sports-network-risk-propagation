# Network-Agent Dynamics in Sports Systems

**Code for Manuscript Review:** Impact of Immediate Interventions in Risk Propagation: Network Topology Effects on Sports System Vulnerability

## Repository Contents

This repository contains four simulation models, empirical validation, and supplementary videos supporting the manuscript:

### Simulation Models

1. **Fundamental Model** (`fundamental_model_animated.py`)
   - Demonstrates basic failure propagation without recovery
   - Shows network state evolution over 20 time steps
   - Animated visualization of cascade dynamics
   - Generates Supplementary Video S1

2. **Recovery Delay Analysis** (`recovery_delay_simulation.py`)
   - Compares immediate (r_t=1) vs delayed (r_t=2) interventions
   - Calculates Network Vulnerability Index (NVI)
   - Reproduces manuscript Figure 3
   - Generates Supplementary Video S2

3. **Network Topology Effects** (`network_topology_ternary.py`)
   - Ternary phase space analysis
   - Compares Regular, Random, Small-world, and Scale-free networks
   - Reproduces manuscript Figure 5 and Table 8
   - Generates Supplementary Video S3

4. **Integrated Network-Phase Space Visualization** (`network_phase_space_integrated.py`)
   - Unified visualization of network failure synchronized with phase space evolution
   - Scale-free network (n=35, m=2) embedded in ternary diagram
   - Parametric recovery delay sweep (r_t = 1.0→5.0) over 150 frames
   - Node colors transition blue→red while attractor migrates through phase space
   - Demonstrates hub vulnerability under delayed intervention
   - Generates Supplementary Video S4 (22.5 seconds, **video file included in repository**)
   - Supports manuscript Figure 6 bottom panel interpretation

### Empirical Validation

5. **Empirical Validation** (`Empirical_validation.py`)
   - Validates model predictions against real-world sports data
   - Generates Figure 6 (three-panel validation)
   - Statistical analysis: R² = 0.981, RMSE = 0.089
   - Reproduces manuscript Figure 6 and Table 7

### Supplementary Videos

- **Video S1** (`supplementary_video_S1.mp4`): Fundamental dynamics without recovery (10s)
- **Video S2** (`supplementary_video_S2.mp4`): Recovery delay comparison (10s)
- **Video S3** (`supplementary_video_S3.mp4`): Network topology effects (10s)
- **Video S4** (`supplementary_video_S4.mp4`): Integrated network-phase space dynamics (22.5s) ✨ **NEW**

All video files are included in the repository for peer review and can be regenerated using the corresponding Python scripts.

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
python network_phase_space_integrated.py  # NEW: Integrated visualization

# Run empirical validation
python Empirical_validation.py
```
