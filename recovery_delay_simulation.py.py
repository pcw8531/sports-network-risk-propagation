#!/usr/bin/env python
# coding: utf-8

# In[11]:


"""
================================================================================
RECOVERY DELAY IMPACT ON NETWORK FAILURE PROPAGATION
Computational Model for Sports System Vulnerability Analysis
================================================================================

Title: Network Recovery Simulation with Delayed Intervention Effects
Author: Chulwook Park
Date: October 2025
Version: 1.1
License: MIT

Purpose:
--------
This simulation demonstrates the critical impact of recovery delay (r_t) on 
failure propagation in scale-free networks, supporting the findings presented in:
"Impact of Immediate Interventions in Risk Propagation: Network Topology Effects 
on Sports System Vulnerability"

Description:
------------
The code compares immediate recovery (r_t=1) versus delayed recovery (r_t=2) in
scale-free networks characteristic of sports teams with star players. It visualizes
how delayed interventions lead to cascading failures, while immediate interventions
maintain system stability. The Network Vulnerability Index (NVI) is calculated to
quantify the difference in system resilience.

Key Features:
- Side-by-side comparison of recovery scenarios
- Real-time NVI calculation and visualization
- Explicit failure cascade dynamics
- Parameter calibration based on empirical sports data
- Sensitivity analysis for recovery delay effects

Theory:
-------
Recovery delay (r_t) represents the time gap between problem identification and
intervention implementation in sports systems. When r_t=1, interventions are
immediate (ideal scenario). When r_t≥2, there is a delay allowing failures to
propagate through network connections before recovery begins.

Network Vulnerability Index (NVI):
NVI = mean(failure_rate) / mean(protection_level)
Higher NVI indicates greater system vulnerability to cascading failures.

Repository: github.com/chulwookpark/sports-network-vulnerability
================================================================================
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec

# Set random seed for reproducibility
np.random.seed(42)

class NetworkRecoverySimulation:
    """
    Network-based simulation of failure propagation with recovery mechanisms.
    
    This class models how failures spread through interconnected systems and how
    recovery delay affects the cascading dynamics. Each node represents an agent
    (e.g., athlete, team member) with capital, protection strategies, and failure
    states that evolve based on network interactions.
    """
    
    def __init__(self, network_type='scale-free', n=100, r_t=1):
        """
        Initialize simulation with specified network and recovery time
        
        Parameters:
        -----------
        network_type : str
            Network topology ('scale-free', 'regular', 'random', 'small-world')
            Scale-free networks model sports teams with star players (hubs)
        n : int
            Number of nodes (team size)
        r_t : int
            Recovery time delay (1=immediate intervention, ≥2=delayed intervention)
            This is the CRITICAL parameter affecting system vulnerability
        """
        self.n = n
        self.r_t = r_t
        self.network_type = network_type
        
        # Validate parameters
        if r_t < 1:
            raise ValueError("Recovery time (r_t) must be ≥ 1")
        if n < 10:
            raise ValueError("Network size (n) must be ≥ 10")
        
        # Create network based on type
        if network_type == 'regular':
            dim = int(np.sqrt(n))
            self.G = nx.grid_2d_graph(dim, dim)
            self.G = nx.convert_node_labels_to_integers(self.G)
        elif network_type == 'random':
            self.G = nx.erdos_renyi_graph(n, 0.1)
        elif network_type == 'small-world':
            k = min(10, n // 10)  # Ensure k < n
            self.G = nx.watts_strogatz_graph(n, k, 0.3)
        else:  # scale-free (default)
            m = min(3, n // 10)  # Preferential attachment parameter
            self.G = nx.barabasi_albert_graph(n, m)
        
        # Calculate centrality (importance measure for each node)
        try:
            C_dict = nx.eigenvector_centrality(self.G, max_iter=1000)
        except:
            # Fallback to degree centrality if eigenvector fails
            C_dict = nx.degree_centrality(self.G)
        
        self.Centrality = np.array([C_dict.get(i, 0) for i in range(n)])
        if self.Centrality.max() > 0:
            self.Centrality = self.Centrality / self.Centrality.max()
        
        # Initialize state variables
        self.reset_simulation()
        
    def reset_simulation(self):
        """Reset all simulation variables to initial state"""
        # State matrix B: [capital, strategy0, strategy1, failure]
        self.B = np.zeros((self.n, 4))
        self.B[:, 0] = 1.0  # Initial capital (resource/ability level)
        self.B[:, 1] = 0.3  # Initial strategy parameter fp0
        self.B[:, 2] = 0.3  # Initial strategy parameter fp1
        self.B[:, 3] = 0    # No initial failures
        
        # Failure dynamics tracking
        self.failure_potential = np.zeros(self.n)  # Latent risk at each node
        self.recovery_counter = np.zeros(self.n)    # Time since failure began
        
        # Model Parameters (calibrated from empirical sports data)
        # See manuscript Tables 1-4 for parameter justification
        self.fm = 0.1   # Maintenance cost (fraction of capital)
        self.pr = 0.9   # Imitation probability (social learning rate)
        self.pe = 0.1   # Exploration probability (innovation rate)
        self.pn = 0.1   # Failure origination probability per node
        self.pl = 0.3   # Propagation probability along network links
        self.pmax = 1.0 # Maximum protection probability
        self.cp = 0.5   # Reference point for protection saturation
        
        # Metrics tracking
        self.failure_history = []
        self.protection_history = []
        self.capital_history = []
        
    def step(self):
        """
        Execute one time step of the simulation
        
        Process flow:
        1. Calculate protection levels based on strategies and centrality
        2. Update capital based on investments
        3. Originate new failure potentials
        4. Propagate failures through network
        5. Apply protection and determine new failures
        6. Execute recovery mechanism (CRITICAL: depends on r_t)
        7. Update strategies through imitation
        """
        
        # === 1. PROTECTION LEVEL CALCULATION ===
        # fp = fp0 + fp1*C (heuristic protection investment)
        fp = self.B[:, 1] + self.B[:, 2] * self.Centrality
        fp = np.clip(fp, 0, 1 - self.fm)  # Constrain to valid range
        
        # === 2. CAPITAL UPDATE ===
        # Capital grows with payoff, diminishes with maintenance and protection costs
        self.B[:, 0] = 1 + (1 - self.fm - fp) * self.B[:, 0]
        self.B[:, 0] = np.clip(self.B[:, 0], 0, 100)  # Prevent overflow
        
        # === 3. FAILURE ORIGINATION ===
        # New failure potentials can arise spontaneously at any node
        new_failures = np.random.random(self.n) < self.pn
        self.failure_potential[new_failures] = 1
        
        # === 4. FAILURE PROPAGATION THROUGH NETWORK ===
        # Failed nodes spread failure potential to neighbors
        for i in range(self.n):
            if self.B[i, 3] > 0:  # If node i has failed
                neighbors = list(self.G.neighbors(i))
                for j in neighbors:
                    if np.random.random() < self.pl:
                        self.failure_potential[j] = 1
        
        # === 5. PROTECTION AND FAILURE DETERMINATION ===
        # Protection probability based on investment and capital
        # pp = pmax / (1 + cp/(fp*c))
        protection_prob = np.zeros(self.n)
        idx = self.failure_potential > 0
        if idx.any():
            denominator = fp[idx] * self.B[idx, 0] + 1e-10
            protection_prob[idx] = self.pmax / (1 + self.cp / denominator)
        
        # Determine which nodes fail (failure potential + insufficient protection)
        fail_mask = (np.random.random(self.n) <= (1 - protection_prob)) & idx
        self.B[fail_mask, 3] = 1
        self.B[fail_mask, 0] = 0  # Failure causes capital loss
        
        # === 6. RECOVERY MECHANISM (KEY PARAMETER: r_t) ===
        """
        CRITICAL DISTINCTION BETWEEN IMMEDIATE AND DELAYED RECOVERY:
        
        r_t = 1 (Immediate Recovery):
        - Failure potentials cleared immediately each step
        - Failed nodes recover in the same time step
        - Prevents cascading effects
        - Models ideal intervention scenario
        
        r_t ≥ 2 (Delayed Recovery):
        - Failure potentials persist for multiple steps
        - Failed nodes remain failed for r_t time steps
        - Allows cascading propagation during delay
        - Models realistic intervention delays in sports systems
        """
        
        if self.r_t == 1:
            # IMMEDIATE RECOVERY: Reset all failures and potentials instantly
            self.failure_potential[:] = 0
            self.B[:, 3] = 0
            self.recovery_counter[:] = 0
            
        else:
            # DELAYED RECOVERY: Failures persist for r_t time steps
            # Increment recovery counter for currently failed nodes
            self.recovery_counter[self.B[:, 3] == 1] += 1
            
            # Nodes recover only after r_t time steps have passed
            recover_mask = self.recovery_counter >= self.r_t
            self.B[recover_mask, 3] = 0
            self.recovery_counter[recover_mask] = 0
            
            # Failure potentials decay gradually (not immediately)
            # This allows propagation to continue during recovery delay
            decay_mask = np.random.random(self.n) < (0.3 / self.r_t)
            self.failure_potential[decay_mask] = 0
        
        # === 7. STRATEGY EVOLUTION (IMITATION) ===
        # Agents copy strategies from more successful neighbors
        for i in range(self.n):
            if np.random.random() < self.pr:
                neighbors = list(self.G.neighbors(i))
                if neighbors:
                    # Choose neighbor with higher capital as role model
                    neighbor_capitals = [self.B[j, 0] for j in neighbors]
                    if max(neighbor_capitals) > self.B[i, 0]:
                        j = neighbors[np.argmax(neighbor_capitals)]
                        # Imitate role model's strategies
                        self.B[i, 1:3] = self.B[j, 1:3]
        
        # === 8. TRACK METRICS ===
        self.failure_history.append(np.mean(self.B[:, 3]))
        self.protection_history.append(np.mean(fp))
        self.capital_history.append(np.mean(self.B[:, 0]))
    
    def calculate_nvi(self, window=20):
        """
        Calculate Network Vulnerability Index (NVI)
        
        NVI = mean(failure_rate) / mean(protection_level)
        
        Higher values indicate greater system vulnerability.
        Typical ranges:
        - NVI < 0.5: Resilient system
        - 0.5 ≤ NVI < 1.0: Moderate vulnerability
        - NVI ≥ 1.0: High vulnerability
        
        Parameters:
        -----------
        window : int, number of recent time steps to average
        
        Returns:
        --------
        float : NVI value
        """
        if len(self.failure_history) < window:
            return 0.0
        
        recent_failures = np.mean(self.failure_history[-window:])
        recent_protection = np.mean(self.protection_history[-window:])
        
        # Prevent division by zero
        nvi = recent_failures / (recent_protection + 0.01)
        return nvi


def create_comparison_animation():
    """
    Create side-by-side animation comparing immediate vs delayed recovery
    
    This visualization demonstrates the paper's key finding: recovery delay
    dramatically increases system vulnerability even with identical network
    structure and protection mechanisms.
    
    Returns:
    --------
    matplotlib.animation.FuncAnimation object
    """
    
    # Create figure with sophisticated layout
    fig = plt.figure(figsize=(16, 7))
    gs = GridSpec(2, 2, height_ratios=[3, 1], width_ratios=[1, 1],
                  hspace=0.3, wspace=0.25)
    
    # Network visualizations (top row)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    
    # Time series comparison (bottom row)
    ax3 = fig.add_subplot(gs[1, :])
    
    # Initialize simulations with identical networks
    print("Initializing simulations...")
    sim1 = NetworkRecoverySimulation('scale-free', n=100, r_t=1)
    sim2 = NetworkRecoverySimulation('scale-free', n=100, r_t=2)
    
    # Use same network structure for fair comparison
    sim2.G = sim1.G.copy()
    sim2.Centrality = sim1.Centrality.copy()
    
    # Set up network visualization layout
    pos = nx.spring_layout(sim1.G, k=0.5, iterations=20, seed=42)
    
    def init():
        """Initialize animation"""
        ax1.clear()
        ax2.clear()
        ax3.clear()
        
        ax1.set_title('Immediate Recovery (r_t=1)\nIdeal Intervention Scenario', 
                     fontsize=12, fontweight='bold', color='blue')
        ax2.set_title('Delayed Recovery (r_t=2)\nRealistic Intervention Scenario', 
                     fontsize=12, fontweight='bold', color='red')
        
        ax3.set_xlabel('Time Steps', fontsize=11)
        ax3.set_ylabel('Failure Rate', fontsize=11)
        ax3.set_ylim(0, 1)
        ax3.grid(True, alpha=0.3)
        
        return []
    
    def animate(frame):
        """Animation update function"""
        # Execute one time step in both simulations
        sim1.step()
        sim2.step()
        
        # Clear axes for redrawing
        ax1.clear()
        ax2.clear()
        
        # === NETWORK VISUALIZATIONS ===
        # Color nodes: red = failed, blue = healthy, size by centrality
        colors1 = ['darkred' if sim1.B[i, 3] > 0 else 'lightblue' 
                  for i in range(sim1.n)]
        colors2 = ['darkred' if sim2.B[i, 3] > 0 else 'lightblue' 
                  for i in range(sim2.n)]
        
        # Node size proportional to centrality (star players are larger)
        sizes1 = [50 + 200 * sim1.Centrality[i] for i in range(sim1.n)]
        sizes2 = [50 + 200 * sim2.Centrality[i] for i in range(sim2.n)]
        
        # Draw networks
        nx.draw(sim1.G, pos, ax=ax1, node_color=colors1, node_size=sizes1,
                edge_color='gray', width=0.5, with_labels=False, alpha=0.8)
        nx.draw(sim2.G, pos, ax=ax2, node_color=colors2, node_size=sizes2,
                edge_color='gray', width=0.5, with_labels=False, alpha=0.8)
        
        # Update titles with current failure counts
        fail_count1 = np.sum(sim1.B[:, 3])
        fail_count2 = np.sum(sim2.B[:, 3])
        
        ax1.set_title(f'r_t=1 | Failures: {fail_count1:.0f}/{sim1.n} ({100*fail_count1/sim1.n:.1f}%)', 
                     fontsize=11, fontweight='bold', color='blue')
        ax2.set_title(f'r_t=2 | Failures: {fail_count2:.0f}/{sim2.n} ({100*fail_count2/sim2.n:.1f}%)', 
                     fontsize=11, fontweight='bold', 
                     color='red' if fail_count2 > fail_count1 else 'black')
        
        # === TIME SERIES PLOT ===
        ax3.clear()
        time_steps = range(len(sim1.failure_history))
        
        # Plot failure rates over time
        ax3.plot(time_steps, sim1.failure_history, 'b-', 
                label=f'Immediate Recovery (r_t=1)', linewidth=2.5, alpha=0.8)
        ax3.plot(time_steps, sim2.failure_history, 'r-', 
                label=f'Delayed Recovery (r_t=2)', linewidth=2.5, alpha=0.8)
        
        ax3.set_xlabel('Time Steps', fontsize=11)
        ax3.set_ylabel('Failure Rate', fontsize=11)
        ax3.set_ylim(0, 1)
        ax3.legend(loc='upper left', fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # === NVI CALCULATION AND DISPLAY ===
        if len(sim1.failure_history) > 20:
            nvi1 = sim1.calculate_nvi(window=20)
            nvi2 = sim2.calculate_nvi(window=20)
            
            # Calculate percentage difference
            nvi_diff = ((nvi2 - nvi1) / (nvi1 + 0.01)) * 100
            
            # Display NVI comparison
            nvi_text = f'Network Vulnerability Index (NVI):\n'
            nvi_text += f'r_t=1: {nvi1:.3f} | r_t=2: {nvi2:.3f}\n'
            nvi_text += f'Increase: {nvi_diff:.1f}%'
            
            ax3.text(0.98, 0.97, nvi_text, 
                    transform=ax3.transAxes, ha='right', va='top',
                    fontsize=9, fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', 
                             alpha=0.9, edgecolor='black'))
        
        # Add step counter
        ax3.text(0.02, 0.97, f'Step: {frame+1}', 
                transform=ax3.transAxes, ha='left', va='top',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.7))
        
        return []
    
    # Create animation
    print("Creating animation...")
    ani = animation.FuncAnimation(fig, animate, init_func=init, 
                                 frames=200, interval=100, blit=False,
                                 repeat=True)
    
    # Overall title
    plt.suptitle('Recovery Delay Impact on Failure Propagation in Scale-Free Networks\n' +
                'Network Vulnerability Analysis for Sports Systems', 
                fontsize=14, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    return ani


def run_comparative_analysis(network_type='scale-free', n=100, time_steps=500):
    """
    Run quantitative comparison of different recovery delay values
    
    Parameters:
    -----------
    network_type : str, network topology to test
    n : int, network size
    time_steps : int, number of simulation steps
    
    Returns:
    --------
    dict : Results including NVI values for each r_t
    """
    print(f"\nRunning comparative analysis on {network_type} network...")
    print(f"Network size: {n} nodes, Time steps: {time_steps}\n")
    
    results = {}
    
    for r_t in [1, 2, 3, 5]:
        print(f"Testing r_t = {r_t}...", end=' ')
        sim = NetworkRecoverySimulation(network_type, n=n, r_t=r_t)
        
        # Run simulation
        for _ in range(time_steps):
            sim.step()
        
        # Calculate metrics
        nvi = sim.calculate_nvi(window=50)
        mean_failures = np.mean(sim.failure_history[-100:])
        mean_capital = np.mean(sim.capital_history[-100:])
        
        results[f'r_t_{r_t}'] = {
            'NVI': nvi,
            'mean_failure_rate': mean_failures,
            'mean_capital': mean_capital,
            'failure_history': sim.failure_history
        }
        
        print(f"NVI = {nvi:.3f}, Failure Rate = {mean_failures:.3f}")
    
    return results


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("="*80)
    print("RECOVERY DELAY IMPACT SIMULATION")
    print("Network-Agent Dynamics in Sports Systems")
    print("="*80)
    
    # Option 1: Run animation (for visualization)
    print("\n[1] Generating recovery effect comparison animation...")
    ani = create_comparison_animation()
    
    try:
        # Try to display in Jupyter notebook
        from IPython.display import HTML
        display(HTML(ani.to_jshtml()))
    except:
        # Show in standard matplotlib window
        plt.show()
    
    # Option 2: Run quantitative analysis (for data)
    print("\n[2] Running quantitative comparative analysis...")
    results = run_comparative_analysis(network_type='scale-free', n=100, time_steps=500)
    
    print("\n" + "="*80)
    print("SUMMARY OF RESULTS")
    print("="*80)
    for key, value in results.items():
        print(f"\n{key}:")
        print(f"  Network Vulnerability Index (NVI): {value['NVI']:.4f}")
        print(f"  Mean Failure Rate: {value['mean_failure_rate']:.4f}")
        print(f"  Mean Capital: {value['mean_capital']:.4f}")
    
    print("\n" + "="*80)
    print("Key Finding: Recovery delay substantially increases system vulnerability")
    nvi_increase = ((results['r_t_2']['NVI'] - results['r_t_1']['NVI']) / 
                    results['r_t_1']['NVI']) * 100
    print(f"NVI increases by {nvi_increase:.1f}% when r_t changes from 1 to 2")
    print("="*80)


# In[ ]:




