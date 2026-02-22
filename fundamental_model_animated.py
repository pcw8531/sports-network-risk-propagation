#!/usr/bin/env python
# coding: utf-8

# In[6]:


"""
================================================================================
FUNDAMENTAL NETWORK-AGENT DYNAMICS MODEL WITH ANIMATION
Core Mechanics of Risk Propagation in Networked Systems
================================================================================

Title: Animated Basic Network Simulation - Core Model Validation
Author: Chulwook Park
Date: October 2025
Version: 1.1
License: MIT

Purpose:
--------
This code demonstrates the fundamental network-agent dynamics through real-time
animation, showing how failures propagate through networks without recovery.
The visualization focuses on essential dynamics: failure spread, protection
attempts, and capital loss over 20 time steps.

Core Model (Simplified):
------------------------
1. Capital (c): c(t+1) = 1 + (1-fm-fp)*c(t)
2. Protection (fp): fp = fp0 + fp1*C
3. Protection Probability (pp): pp = pmax/(1 + cp/(fp*c))
4. Failure Propagation: pn (origin) + pl (transmission)
5. Social Learning: pr (imitation) + pe (exploration)

Key Feature:
------------
NO RECOVERY - demonstrates worst-case scenario requiring intervention

Animation Shows:
----------------
- Left: Network state evolution (failures spreading over time)
- Right: Cumulative failure matrix building up

Repository: github.com/chulwookpark/sports-network-vulnerability
================================================================================
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Patch
from matplotlib.gridspec import GridSpec
import warnings

warnings.filterwarnings('ignore')
np.random.seed(42)


# ============================================================================
# NETWORK GENERATION
# ============================================================================

def create_random_network(n=20, p=0.9):
    """Create Erdős-Rényi random network"""
    G = nx.erdos_renyi_graph(n, p, seed=42)
    try:
        C = nx.eigenvector_centrality(G, max_iter=1000)
    except:
        C = nx.degree_centrality(G)
    return G, C


# ============================================================================
# SIMULATION CLASS
# ============================================================================

class FundamentalNetworkSimulation:
    """
    Network-agent dynamics simulation without recovery mechanisms
    """
    
    def __init__(self, n=20, p=0.9):
        """Initialize simulation"""
        self.n = n
        self.p = p
        
        # Create network
        self.G, C = create_random_network(n, p)
        self.Centrality = np.array(list(C.values()))
        
        # State variables
        self.Capital = np.ones(n)
        self.Strategy_0 = np.zeros(n)
        self.Strategy_1 = np.zeros(n)
        self.Failure = np.zeros(n)
        self.failure_potential = np.zeros(n)
        self.protection_probability = np.zeros(n)
        
        # Parameters
        self.fm = 0.1      # Maintenance
        self.pmax = 1.0    # Max protection
        self.cp = 0.5      # Half-saturation
        self.pn = 0.1      # Failure origin
        self.pl = 0.3      # Propagation
        self.pr = 0.1      # Imitation
        self.pe = 0.1      # Exploration
        self.s = 1.0       # Selection intensity
        self.mu = 0.0      # Exploration mean
        self.sigma = 0.1   # Exploration SD
        
        # History tracking
        self.failure_history = []
        self.capital_history = []
        self.protection_history = []
        self.failure_matrix = []
        
    def step(self):
        """Execute one simulation time step"""
        
        # Social learning: Imitation
        for i in range(self.n):
            if np.random.random() <= self.pr:
                ff = i
                while True:
                    rr = np.random.choice(self.n)
                    if ff != rr:
                        break
                pi = 1.0 / (1.0 + np.exp(-self.s * (self.Capital[rr] - self.Capital[ff])))
                if np.random.random() <= pi:
                    self.Strategy_0[ff] = self.Strategy_0[rr]
                    self.Strategy_1[ff] = self.Strategy_1[rr]
        
        # Social learning: Exploration
        for i in range(self.n):
            if np.random.random() <= self.pe:
                self.Strategy_0[i] += np.random.normal(self.mu, self.sigma)
            if np.random.random() <= self.pe:
                self.Strategy_1[i] += np.random.normal(self.mu, self.sigma)
        
        # Protection level
        fp = self.Strategy_0 + self.Strategy_1 * self.Centrality
        fp = np.clip(fp, 0, 1 - self.fm)
        
        # Capital update
        self.Capital = 1.0 + (1.0 - self.fm - fp) * self.Capital
        self.Capital = np.clip(self.Capital, 0, 100)
        
        # Failure origination
        new_origins = np.random.random(self.n) <= self.pn
        self.failure_potential[new_origins] = 1
        
        # Failure propagation
        for i in range(self.n):
            if self.Failure[i] > 0:
                for j in self.G.neighbors(i):
                    if np.random.random() <= self.pl:
                        self.failure_potential[j] = 1
        
        # Protection probability
        self.protection_probability = np.zeros(self.n)
        at_risk = self.failure_potential > 0
        
        if at_risk.any():
            with np.errstate(divide='ignore', invalid='ignore'):
                denom = fp[at_risk] * self.Capital[at_risk] + 1e-10
                self.protection_probability[at_risk] = self.pmax / (1.0 + self.cp / denom)
        
        # Determine failures (NO RECOVERY)
        fail_check = (np.random.random(self.n) > self.protection_probability) & at_risk
        self.Failure[fail_check] = 1
        self.Capital[fail_check] = 0
        
        # Record history
        self.failure_history.append(np.mean(self.Failure))
        self.capital_history.append(np.mean(self.Capital))
        self.protection_history.append(np.mean(self.protection_probability))
        self.failure_matrix.append(self.Failure.copy())


# ============================================================================
# RUN FULL SIMULATION (for data collection)
# ============================================================================

def run_full_simulation(timePeriod=20):
    """
    Run complete simulation to collect all data
    
    This runs first to populate history before creating animation
    """
    print("Running simulation to collect data...")
    sim = FundamentalNetworkSimulation(n=20, p=0.9)
    
    for t in range(timePeriod):
        sim.step()
    
    print(f"Simulation complete: {len(sim.failure_history)} time steps recorded")
    return sim


# ============================================================================
# ANIMATION FUNCTION
# ============================================================================

def create_animated_visualization(sim_data, timePeriod=20):
    """
    Create animated visualization using pre-computed simulation data
    
    Parameters:
    -----------
    sim_data : FundamentalNetworkSimulation
        Simulation with complete history
    timePeriod : int
        Number of time steps
        
    Returns:
    --------
    matplotlib.animation.FuncAnimation
    """
    
    print(f"Creating animation from simulation data...")
    
    # Create figure with two panels
    fig = plt.figure(figsize=(14, 6), dpi=120)
    gs = GridSpec(1, 2, width_ratios=[1, 1], hspace=0.3, wspace=0.3)
    
    ax1 = fig.add_subplot(gs[0, 0])  # Network
    ax2 = fig.add_subplot(gs[0, 1])  # Matrix
    
    # Set up network layout (fixed for all frames)
    pos = nx.circular_layout(sim_data.G)
    
    # Reference to colorbar (create once)
    cbar_created = [False]
    
    def init():
        """Initialize animation"""
        ax1.clear()
        ax2.clear()
        ax1.set_aspect('equal')
        ax1.axis('off')
        return []
    
    def animate(frame):
        """Update animation frame"""
        
        # Clear axes
        ax1.clear()
        ax2.clear()
        
        # Get state at this frame
        current_failure = sim_data.failure_matrix[frame]
        current_protection = sim_data.protection_history[frame]
        
        # ====================================================================
        # PANEL 1: NETWORK VISUALIZATION
        # ====================================================================
        
        ax1.set_aspect('equal')
        ax1.axis('off')
        
        # Get current states
        failed = np.where(current_failure > 0)[0].tolist()
        healthy = np.where(current_failure == 0)[0].tolist()
        
        # Estimate which nodes are protected (using threshold)
        # Since we don't store individual protection, show nodes with low failure history
        protected = []
        if frame > 0:
            for i in range(sim_data.n):
                if current_failure[i] == 0 and current_protection > 0.3:
                    protected.append(i)
        
        # Draw network layers
        # Layer 1: Edges (light background)
        nx.draw_networkx_edges(sim_data.G, pos, ax=ax1, edge_color='lightgray', 
                              width=1.5, alpha=0.3)
        
        # Layer 2: Protected nodes (green halo)
        if protected:
            nx.draw_networkx_nodes(sim_data.G, pos, nodelist=protected, ax=ax1,
                                  node_color='green', node_size=800, 
                                  alpha=0.4, edgecolors='none')
        
        # Layer 3: Healthy nodes (blue)
        if healthy:
            nx.draw_networkx_nodes(sim_data.G, pos, nodelist=healthy, ax=ax1,
                                  node_color='blue', node_size=500,
                                  alpha=0.8, edgecolors='white', linewidths=1.5)
            nx.draw_networkx_labels(sim_data.G, pos, ax=ax1,
                                   labels={i: str(i) for i in healthy},
                                   font_color='white', font_size=9)
        
        # Layer 4: Failed nodes (red - on top)
        if failed:
            nx.draw_networkx_nodes(sim_data.G, pos, nodelist=failed, ax=ax1,
                                  node_color='red', node_size=500,
                                  alpha=0.9, edgecolors='white', linewidths=2)
            nx.draw_networkx_labels(sim_data.G, pos, ax=ax1,
                                   labels={i: str(i) for i in failed},
                                   font_color='white', font_size=9, font_weight='bold')
        
        # Title with current statistics
        fail_count = len(failed)
        ax1.set_title(
            f'Network State (t = {frame+1}/{timePeriod})\n' +
            f'Failed: {fail_count}/{sim_data.n} ({100*fail_count/sim_data.n:.1f}%)',
            fontsize=13, fontweight='bold'
        )
        
        # Simplified legend (3 items only)
        legend_elements = [
            Patch(facecolor='red', alpha=0.9, edgecolor='white', 
                  linewidth=2, label='Failed Nodes'),
            Patch(facecolor='blue', alpha=0.8, edgecolor='white', 
                  linewidth=1.5, label='Healthy Nodes'),
            Patch(facecolor='green', alpha=0.4, label='High Protection')
        ]
        ax1.legend(handles=legend_elements, loc='upper left',
                  fontsize=10, frameon=True, fancybox=True, shadow=True)
        
        # ====================================================================
        # PANEL 2: FAILURE MATRIX
        # ====================================================================
        
        # Build matrix up to current frame
        matrix = np.array(sim_data.failure_matrix[:frame+1]).T
        
        im = ax2.imshow(matrix, origin='upper', interpolation='nearest',
                      cmap=plt.cm.RdYlBu_r, aspect='auto', vmin=0, vmax=1)
        
        ax2.set_ylabel('Individual Agents', fontsize=11)
        ax2.set_xlabel('Time Steps', fontsize=11)
        ax2.set_title('Cumulative Failure Propagation', 
                     fontsize=13, fontweight='bold')
        
        ax2.set_xlim(-0.5, timePeriod - 0.5)
        ax2.set_ylim(-0.5, sim_data.n - 0.5)
        
        ax2.set_xticks(np.arange(0, timePeriod, 5))
        ax2.set_yticks(np.arange(0, sim_data.n, 5))
        ax2.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.3)
        
        # Add colorbar only once
        if not cbar_created[0]:
            cbar = plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
            cbar.set_label('State', fontsize=10)
            cbar.set_ticks([0, 1])
            cbar.set_ticklabels(['Healthy', 'Failed'])
            cbar_created[0] = True
        
        # Overall title
        fig.suptitle(
            'Fundamental Network Dynamics: Failure Propagation Without Recovery',
            fontsize=14, fontweight='bold', y=0.98
        )
        
        return []
    
    # Create animation
    ani = animation.FuncAnimation(fig, animate, init_func=init,
                                 frames=timePeriod, interval=500,
                                 blit=False, repeat=True)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    return ani


# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

def print_final_summary(sim, timePeriod):
    """Print simulation summary"""
    
    print("\n" + "="*80)
    print("FUNDAMENTAL MODEL SIMULATION SUMMARY")
    print("="*80)
    print(f"Network: {sim.n} nodes (Random, p={sim.p})")
    print(f"Time steps: {timePeriod}")
    print(f"Recovery: DISABLED (worst-case scenario)")
    print("-"*80)
    
    print(f"\nFinal State (t = {timePeriod}):")
    print("-"*80)
    final_failures = int(np.sum(sim.failure_matrix[-1]))
    print(f"  Failed nodes:              {final_failures}/{sim.n} ({100*final_failures/sim.n:.1f}%)")
    print(f"  Mean capital:              {sim.capital_history[-1]:.4f}")
    print(f"  Mean protection prob:      {sim.protection_history[-1]:.4f}")
    
    print(f"\nDynamics:")
    print("-"*80)
    print(f"  Peak failure rate:         {max(sim.failure_history):.2%} (t={sim.failure_history.index(max(sim.failure_history))+1})")
    print(f"  Average capital:           {np.mean(sim.capital_history):.4f}")
    print(f"  Average protection:        {np.mean(sim.protection_history):.4f}")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS:")
    print("="*80)
    print("  • Failures accumulate without recovery mechanisms")
    print("  • Network structure enables cascading propagation")
    print("  • Protection reduces but cannot eliminate risk")
    print("  • Validates need for immediate interventions")
    print("="*80 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    
    print("="*80)
    print("FUNDAMENTAL NETWORK-AGENT DYNAMICS - ANIMATED")
    print("Core Mechanics Validation")
    print("="*80)
    
    # Run simulation first to collect data
    timePeriod = 20
    sim = run_full_simulation(timePeriod)
    
    # Print summary (now data exists)
    print_final_summary(sim, timePeriod)
    
    # Create animation from collected data
    ani = create_animated_visualization(sim, timePeriod)
    
    # Try to display
    try:
        from IPython.display import HTML
        display(HTML(ani.to_jshtml()))
    except:
        print("\nAnimation created. Displaying in window...")
        plt.show()
    
    # Optional: Save animation
    # print("Saving animation...")
    # ani.save('fundamental_dynamics.mp4', writer='ffmpeg', fps=2, dpi=150)
    # print("Animation saved as: fundamental_dynamics.mp4")
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    print("This animation demonstrates fundamental propagation mechanics")
    print("without recovery, validating the critical need for interventions.")
    print("="*80)


# In[ ]:




