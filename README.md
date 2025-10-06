# Network-Agent Dynamics in Sports Systems

**Code for Manuscript Review**: Impact of Immediate Interventions in Risk Propagation: Network Topology Effects on Sports System Vulnerability

## Repository Contents

This repository contains three simulation models supporting the manuscript:

### 1. Fundamental Model (`fundamental_model_animated.py`)
- Demonstrates basic failure propagation without recovery
- Shows network state evolution over 20 time steps
- Animated visualization of cascade dynamics

### 2. Recovery Delay Analysis (`recovery_delay_simulation.py`)
- Compares immediate (r_t=1) vs delayed (r_t=2) interventions
- Calculates Network Vulnerability Index (NVI)
- Reproduces manuscript Figure 3

### 3. Network Topology Effects (`network_topology_ternary.py`)
- Ternary phase space analysis
- Compares Regular, Random, Small-world, and Scale-free networks
- Reproduces manuscript Figure 5 and Table 6

## Installation
```bash
pip install -r requirements.txt
