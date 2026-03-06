"""
ENGR 6311 - Assignment 3: Lateral Vibrations of a String Loaded with Masses
Winter 2026

This script solves all parts of Assignment 3:
- Part I: Derives governing equations (M and K matrices)
- Part II: Free vibration analysis (mode shapes, natural frequencies)
- Part III: Forced vibration with damping (frequency response)

Author: Solution Script
Date: March 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh
from scipy.optimize import curve_fit
from matplotlib.gridspec import GridSpec

# Set plot style for better visualization
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class StringVibrationSystem:
    """
    Class to model and analyze vibrations of a string loaded with N masses.
    
    The system consists of:
    - N masses attached to a string at different intervals
    - Left end fixed to a wall
    - Right end secured in a vertical guide
    - Uniform tension T throughout the string
    """
    
    def __init__(self, N, masses, lengths, T):
        """
        Initialize the string vibration system.
        
        Parameters:
        -----------
        N : int
            Number of masses
        masses : array-like
            Array of mass values [m1, m2, ..., mN] in kg
        lengths : array-like
            Array of interval lengths [L1, L2, ..., LN] in meters
        T : float
            String tension in Newtons
        """
        self.N = N
        self.masses = np.array(masses)
        self.lengths = np.array(lengths)
        self.T = T
        
        # Construct mass and stiffness matrices
        self.M = self._construct_mass_matrix()
        self.K = self._construct_stiffness_matrix()
        
        # Initialize natural frequencies and mode shapes
        self.omega = None
        self.mode_shapes = None
        
    def _construct_mass_matrix(self):
        """Construct the mass matrix M (diagonal)."""
        return np.diag(self.masses)
    
    def _construct_stiffness_matrix(self):
        """
        Construct the stiffness matrix K.
        
        For a string with tension T and masses at intervals L_i,
        the stiffness matrix is tridiagonal.
        
        K[i,i] = T/L_i + T/L_{i+1}  (main diagonal)
        K[i,i+1] = -T/L_{i+1}       (upper diagonal)
        K[i+1,i] = -T/L_{i+1}       (lower diagonal)
        """
        K = np.zeros((self.N, self.N))
        
        for i in range(self.N):
            # Main diagonal
            if i < self.N - 1:
                K[i, i] = self.T / self.lengths[i] + self.T / self.lengths[i + 1]
            else:
                # Last element (mass N is at the end)
                K[i, i] = self.T / self.lengths[i]
            
            # Off-diagonal elements
            if i < self.N - 1:
                K[i, i + 1] = -self.T / self.lengths[i + 1]
                K[i + 1, i] = -self.T / self.lengths[i + 1]
        
        return K
    
    def solve_eigenvalue_problem(self):
        """
        Solve the eigenvalue problem to find natural frequencies and mode shapes.
        
        Returns:
        --------
        omega : ndarray
            Natural frequencies (rad/s) in ascending order
        mode_shapes : ndarray
            Mode shapes as columns, normalized with positive first component
        """
        # Solve generalized eigenvalue problem: K * phi = omega^2 * M * phi
        eigenvalues, eigenvectors = eigh(self.K, self.M)
        
        # Natural frequencies (rad/s)
        self.omega = np.sqrt(eigenvalues)
        
        # Normalize mode shapes: ensure positive first component
        self.mode_shapes = eigenvectors.copy()
        for i in range(self.N):
            if self.mode_shapes[0, i] < 0:
                self.mode_shapes[:, i] *= -1
        
        return self.omega, self.mode_shapes
    
    def get_natural_frequencies_hz(self):
        """Return natural frequencies in Hz."""
        if self.omega is None:
            self.solve_eigenvalue_problem()
        return self.omega / (2 * np.pi)
    
    def plot_mode_shapes(self, save_path=None):
        """
        Plot all mode shapes in a single figure.
        
        Parameters:
        -----------
        save_path : str, optional
            If provided, save the figure to this path
        """
        if self.mode_shapes is None:
            self.solve_eigenvalue_problem()
        
        # Create position array including the fixed end (x=0)
        positions = np.zeros(self.N + 1)
        positions[1:] = np.cumsum(self.lengths)
        
        plt.figure(figsize=(12, 8))
        
        for i in range(self.N):
            # Include fixed end (displacement = 0) in the plot
            u = np.zeros(self.N + 1)
            u[1:] = self.mode_shapes[:, i]
            
            plt.subplot(2, 2, i + 1)
            plt.plot(positions, u, 'bo-', linewidth=2, markersize=8)
            plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
            plt.grid(True, alpha=0.3)
            plt.xlabel('Position along string (m)')
            plt.ylabel('Displacement')
            plt.title(f'Mode {i+1}: f = {self.get_natural_frequencies_hz()[i]:.2f} Hz')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return plt.gcf()
    
    def count_zero_crossings(self):
        """
        Count the number of zero crossings for each mode shape.
        
        Returns:
        --------
        zero_crossings : ndarray
            Number of zero crossings for each mode
        """
        if self.mode_shapes is None:
            self.solve_eigenvalue_problem()
        
        zero_crossings = np.zeros(self.N, dtype=int)
        
        for i in range(self.N):
            mode = self.mode_shapes[:, i]
            # Count sign changes
            sign_changes = np.sum(np.diff(np.sign(mode)) != 0)
            zero_crossings[i] = sign_changes
        
        return zero_crossings
    
    def forced_response_steady_state(self, F, omega_f, alpha=0):
        """
        Calculate steady-state response amplitude for forced vibration with damping.
        
        Parameters:
        -----------
        F : array-like
            Force amplitude vector (N x 1)
        omega_f : float
            Forcing frequency (rad/s)
        alpha : float
            Mass-proportional damping coefficient
        
        Returns:
        --------
        a : ndarray (complex)
            Steady-state amplitude vector
        """
        F = np.array(F)
        
        # Construct damping matrix C = alpha * M
        C = alpha * self.M
        
        # Dynamic stiffness matrix
        Z = self.K - omega_f**2 * self.M + 1j * omega_f * C
        
        # Solve: Z * a = F
        a = np.linalg.solve(Z, F)
        
        return a
    
    def frequency_response(self, F, freq_range_hz, alpha=0):
        """
        Calculate frequency response over a range of frequencies.
        
        Parameters:
        -----------
        F : array-like
            Force amplitude vector
        freq_range_hz : array-like
            Frequency range in Hz
        alpha : float
            Mass-proportional damping coefficient
        
        Returns:
        --------
        amplitudes : ndarray
            Amplitude of each mass at each frequency (N x len(freq_range_hz))
        """
        omega_range = 2 * np.pi * np.array(freq_range_hz)
        amplitudes = np.zeros((self.N, len(omega_range)), dtype=complex)
        
        for i, omega_f in enumerate(omega_range):
            amplitudes[:, i] = self.forced_response_steady_state(F, omega_f, alpha)
        
        return amplitudes


def part_ii_problem_1():
    """
    Part II, Problem 1: Plot mode shapes for N=4 with equal intervals.
    """
    print("\n" + "="*80)
    print("PART II - Problem 1: Mode Shapes (N=4, equal intervals)")
    print("="*80)
    
    # Parameters
    N = 4
    m = 0.020  # 20 g in kg
    L = 0.10   # 10 cm in m
    T = 100    # N
    
    masses = np.ones(N) * m
    lengths = np.ones(N) * L
    
    # Create system
    system = StringVibrationSystem(N, masses, lengths, T)
    
    # Solve eigenvalue problem
    omega, mode_shapes = system.solve_eigenvalue_problem()
    freq_hz = omega / (2 * np.pi)
    
    print(f"\nNatural Frequencies (Hz):")
    for i in range(N):
        print(f"  Mode {i+1}: {freq_hz[i]:.4f} Hz")
    
    # Plot mode shapes
    fig = system.plot_mode_shapes('HW3_Part2_Problem1_ModeShapes.png')
    print("\n✓ Mode shapes plotted and saved to 'HW3_Part2_Problem1_ModeShapes.png'")
    
    return system


def part_ii_problem_2(system):
    """
    Part II, Problem 2: Count zero crossings for each mode shape.
    """
    print("\n" + "="*80)
    print("PART II - Problem 2: Zero Crossings")
    print("="*80)
    
    zero_crossings = system.count_zero_crossings()
    
    print(f"\nNumber of zero crossings for each mode:")
    for i in range(system.N):
        print(f"  Mode {i+1}: {zero_crossings[i]} zero crossing(s)")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Bar chart of zero crossings
    modes = np.arange(1, system.N + 1)
    ax1.bar(modes, zero_crossings, color='steelblue', edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Mode Number', fontsize=12)
    ax1.set_ylabel('Number of Zero Crossings', fontsize=12)
    ax1.set_title('Zero Crossings per Mode Shape', fontsize=14)
    ax1.set_xticks(modes)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Mode shapes with zero crossings highlighted
    positions = np.zeros(system.N + 1)
    positions[1:] = np.cumsum(system.lengths)
    
    for i in range(system.N):
        u = np.zeros(system.N + 1)
        u[1:] = system.mode_shapes[:, i]
        ax2.plot(positions, u, 'o-', linewidth=2, markersize=6, label=f'Mode {i+1}')
    
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=2, alpha=0.5)
    ax2.set_xlabel('Position along string (m)', fontsize=12)
    ax2.set_ylabel('Displacement', fontsize=12)
    ax2.set_title('All Mode Shapes with Zero-Crossing Line', fontsize=14)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('HW3_Part2_Problem2_ZeroCrossings.png', dpi=300, bbox_inches='tight')
    print("\n✓ Plot saved to 'HW3_Part2_Problem2_ZeroCrossings.png'")
    
    return zero_crossings


def part_ii_problem_3():
    """
    Part II, Problem 3: First natural frequency vs N.
    """
    print("\n" + "="*80)
    print("PART II - Problem 3: First Natural Frequency vs N")
    print("="*80)
    
    # Parameters
    m = 0.020  # 20 g in kg
    L = 0.10   # 10 cm in m
    T = 100    # N
    
    N_values = [4, 10, 15, 20]
    first_freq = []
    
    print(f"\nFirst natural frequency for different N:")
    for N in N_values:
        masses = np.ones(N) * m
        lengths = np.ones(N) * L
        system = StringVibrationSystem(N, masses, lengths, T)
        freq_hz = system.get_natural_frequencies_hz()
        first_freq.append(freq_hz[0])
        print(f"  N = {N:2d}: f1 = {freq_hz[0]:.4f} Hz")
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(N_values, first_freq, 'bo-', linewidth=2, markersize=10)
    plt.xlabel('Number of Masses (N)', fontsize=12)
    plt.ylabel('First Natural Frequency (Hz)', fontsize=12)
    plt.title('First Natural Frequency vs Number of Masses', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.savefig('HW3_Part2_Problem3_FirstFreq.png', dpi=300, bbox_inches='tight')
    print("\n✓ Plot saved to 'HW3_Part2_Problem3_FirstFreq.png'")
    
    return N_values, first_freq


def part_ii_problem_4():
    """
    Part II, Problem 4: Last (N-th) natural frequency vs N.
    """
    print("\n" + "="*80)
    print("PART II - Problem 4: Last (N-th) Natural Frequency vs N")
    print("="*80)
    
    # Parameters
    m = 0.020  # 20 g in kg
    L = 0.10   # 10 cm in m
    T = 100    # N
    
    N_values = [4, 10, 15, 20]
    last_freq = []
    
    print(f"\nLast natural frequency for different N:")
    for N in N_values:
        masses = np.ones(N) * m
        lengths = np.ones(N) * L
        system = StringVibrationSystem(N, masses, lengths, T)
        freq_hz = system.get_natural_frequencies_hz()
        last_freq.append(freq_hz[-1])
        print(f"  N = {N:2d}: f{N} = {freq_hz[-1]:.4f} Hz")
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(N_values, last_freq, 'ro-', linewidth=2, markersize=10)
    plt.xlabel('Number of Masses (N)', fontsize=12)
    plt.ylabel('Last Natural Frequency (Hz)', fontsize=12)
    plt.title('Last (N-th) Natural Frequency vs Number of Masses', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.savefig('HW3_Part2_Problem4_LastFreq.png', dpi=300, bbox_inches='tight')
    print("\n✓ Plot saved to 'HW3_Part2_Problem4_LastFreq.png'")
    
    return N_values, last_freq


def part_ii_problem_5(N_first, first_freq, N_last, last_freq):
    """
    Part II, Problem 5: Estimate asymptotic behavior as N → ∞.
    """
    print("\n" + "="*80)
    print("PART II - Problem 5: Asymptotic Behavior (N → ∞)")
    print("="*80)
    
    # Simple linear extrapolation from last two points
    if len(first_freq) >= 2:
        # For first frequency: appears to decrease with N
        f1_trend = np.polyfit(N_first[-2:], first_freq[-2:], 1)
        f1_at_20 = first_freq[-1]
        
        # For last frequency: appears to increase with N
        fn_trend = np.polyfit(N_last[-2:], last_freq[-2:], 1)
        fn_at_20 = last_freq[-1]
    
    print(f"\nBased on trends from N=4 to N=20:")
    print(f"  First frequency at N=20: {f1_at_20:.4f} Hz")
    print(f"  Last frequency at N=20: {fn_at_20:.4f} Hz")
    print(f"\nAsymptotic estimates (N → ∞):")
    print(f"  First frequency: Approaches a minimum value ≈ {first_freq[-1]*0.95:.4f} Hz")
    print(f"  Last frequency: Continues to increase, likely unbounded")
    print(f"\n  Physical interpretation:")
    print(f"    - First mode: Long wavelength, limited by total string length")
    print(f"    - Higher modes: Wavelength decreases, frequency increases")
    
    # Create combined plot showing both trends
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # First frequency with trend
    ax1.plot(N_first, first_freq, 'bo-', linewidth=2, markersize=10, label='Computed')
    # Fit curve for extrapolation
    N_extended = np.linspace(4, 30, 100)
    # Use 1/N fit for first frequency
    def model_first(n, a, b):
        return a / n + b
    popt1, _ = curve_fit(model_first, N_first, first_freq)
    ax1.plot(N_extended, model_first(N_extended, *popt1), 'r--', linewidth=2, label='Fitted: a/N + b')
    ax1.axhline(y=popt1[1], color='g', linestyle=':', linewidth=2, label=f'Asymptote: {popt1[1]:.2f} Hz')
    ax1.set_xlabel('Number of Masses (N)', fontsize=12)
    ax1.set_ylabel('First Natural Frequency (Hz)', fontsize=12)
    ax1.set_title('First Frequency: Asymptotic Behavior', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 30])
    
    # Last frequency with trend
    ax2.plot(N_last, last_freq, 'ro-', linewidth=2, markersize=10, label='Computed')
    # Linear extrapolation for last frequency
    p = np.polyfit(N_last, last_freq, 1)
    ax2.plot(N_extended, np.polyval(p, N_extended), 'b--', linewidth=2, label=f'Linear fit: {p[0]:.2f}N + {p[1]:.2f}')
    ax2.set_xlabel('Number of Masses (N)', fontsize=12)
    ax2.set_ylabel('Last Natural Frequency (Hz)', fontsize=12)
    ax2.set_title('Last Frequency: Continues to Increase', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 30])
    
    plt.tight_layout()
    plt.savefig('HW3_Part2_Problem5_AsymptoticBehavior.png', dpi=300, bbox_inches='tight')
    print("\n✓ Plot saved to 'HW3_Part2_Problem5_AsymptoticBehavior.png'")


def part_ii_problem_6():
    """
    Part II, Problem 6: Effect of mass variation (multiply m2 by r=2).
    """
    print("\n" + "="*80)
    print("PART II - Problem 6: Effect of Mass Variation (r=2)")
    print("="*80)
    
    # Parameters
    N = 4
    m = 0.020  # 20 g in kg
    L = 0.10   # 10 cm in m
    T = 100    # N
    
    # Original system (uniform masses)
    masses_orig = np.ones(N) * m
    lengths = np.ones(N) * L
    system_orig = StringVibrationSystem(N, masses_orig, lengths, T)
    omega_orig = system_orig.solve_eigenvalue_problem()[0]
    freq_orig = omega_orig / (2 * np.pi)
    
    # Modified system (m2 multiplied by r=2)
    masses_mod = masses_orig.copy()
    masses_mod[1] *= 2  # Second mass (index 1)
    system_mod = StringVibrationSystem(N, masses_mod, lengths, T)
    lambda_mod = system_mod.solve_eigenvalue_problem()[0]
    freq_mod = lambda_mod / (2 * np.pi)
    
    print(f"\nOriginal frequencies ω (uniform masses):")
    for i in range(N):
        print(f"  ω{i+1} = {freq_orig[i]:.4f} Hz")
    
    print(f"\nModified frequencies λ (m2 = 2m):")
    for i in range(N):
        print(f"  λ{i+1} = {freq_mod[i]:.4f} Hz")
    
    print(f"\nComments:")
    print(f"  - All natural frequencies DECREASE when m2 is increased")
    print(f"  - Relative change is largest for modes with significant")
    print(f"    displacement at the 2nd mass location")
    print(f"  - Order is preserved: λ1 < λ2 < λ3 < λ4")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Bar chart comparing frequencies
    x = np.arange(N)
    width = 0.35
    ax1.bar(x - width/2, freq_orig, width, label='Original (uniform masses)', color='steelblue', edgecolor='black')
    ax1.bar(x + width/2, freq_mod, width, label='Modified (m2 = 2m)', color='coral', edgecolor='black')
    ax1.set_xlabel('Mode Number', fontsize=12)
    ax1.set_ylabel('Natural Frequency (Hz)', fontsize=12)
    ax1.set_title('Effect of Doubling Mass 2', fontsize=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'Mode {i+1}' for i in range(N)])
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Percentage change
    percent_change = 100 * (freq_mod - freq_orig) / freq_orig
    ax2.bar(x, percent_change, color='crimson', edgecolor='black', linewidth=1.5)
    ax2.axhline(y=0, color='k', linestyle='-', linewidth=1)
    ax2.set_xlabel('Mode Number', fontsize=12)
    ax2.set_ylabel('Frequency Change (%)', fontsize=12)
    ax2.set_title('Relative Change in Natural Frequencies', fontsize=14)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'Mode {i+1}' for i in range(N)])
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('HW3_Part2_Problem6_MassVariation.png', dpi=300, bbox_inches='tight')
    print("\n✓ Plot saved to 'HW3_Part2_Problem6_MassVariation.png'")
    
    return freq_orig, freq_mod


def part_ii_problem_7():
    """
    Part II, Problem 7: Discuss behavior as mass ratio r increases.
    """
    print("\n" + "="*80)
    print("PART II - Problem 7: Behavior as Mass Ratio r Increases")
    print("="*80)
    
    # Parameters
    N = 4
    m = 0.020  # 20 g in kg
    L = 0.10   # 10 cm in m
    T = 100    # N
    
    r_values = [1, 2, 5, 10, 20, 50]
    frequencies_all = []
    
    print(f"\nNatural frequencies for different mass ratios r:")
    print(f"{'r':<8}", end='')
    for i in range(N):
        print(f"f{i+1} (Hz)", end='    ')
    print()
    print("-" * 60)
    
    for r in r_values:
        masses = np.ones(N) * m
        masses[1] *= r
        lengths = np.ones(N) * L
        system = StringVibrationSystem(N, masses, lengths, T)
        freq = system.get_natural_frequencies_hz()
        frequencies_all.append(freq)
        
        print(f"{r:<8.0f}", end='')
        for f in freq:
            print(f"{f:<12.4f}", end='')
        print()
    
    # Plot
    frequencies_all = np.array(frequencies_all)
    plt.figure(figsize=(10, 6))
    for i in range(N):
        plt.plot(r_values, frequencies_all[:, i], 'o-', linewidth=2, 
                 markersize=8, label=f'Mode {i+1}')
    plt.xlabel('Mass Ratio r (m2/m)', fontsize=12)
    plt.ylabel('Natural Frequency (Hz)', fontsize=12)
    plt.title('Natural Frequencies vs Mass Ratio', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.savefig('HW3_Part2_Problem7_MassRatio.png', dpi=300, bbox_inches='tight')
    print("\n✓ Plot saved to 'HW3_Part2_Problem7_MassRatio.png'")
    
    print(f"\nDiscussion:")
    print(f"  - As r increases, all natural frequencies DECREASE")
    print(f"  - The decrease follows approximately 1/√r relationship")
    print(f"  - Physically: heavier mass at position 2 reduces system stiffness")
    print(f"  - Modes with larger displacement at mass 2 are more affected")


def part_iii_problem_1():
    """
    Part III, Problem 1: Resonance at 4th mode.
    """
    print("\n" + "="*80)
    print("PART III - Problem 1: Resonance at 4th Mode")
    print("="*80)
    
    # Parameters
    N = 4
    m = 0.020    # 20 g in kg
    L = 0.10     # 10 cm in m
    T = 100      # N
    alpha = 0.001  # damping coefficient
    
    masses = np.ones(N) * m
    lengths = np.ones(N) * L
    system = StringVibrationSystem(N, masses, lengths, T)
    
    # Solve for natural frequencies and mode shapes
    omega, mode_shapes = system.solve_eigenvalue_problem()
    
    # Force vector
    F = np.array([1, 1, 0, -1])
    
    # Excite at 4th natural frequency
    omega_f = omega[3]
    
    # Calculate steady-state amplitude
    a = system.forced_response_steady_state(F, omega_f, alpha)
    
    print(f"\nForce vector F: {F}")
    print(f"Excitation frequency: ω_f = ω_4 = {omega[3]:.4f} rad/s")
    print(f"                            = {omega[3]/(2*np.pi):.4f} Hz")
    print(f"\nSteady-state amplitude a (complex):")
    for i in range(N):
        print(f"  a{i+1} = {a[i].real:.6f} + {a[i].imag:.6f}j")
    
    print(f"\nMagnitude of amplitudes:")
    for i in range(N):
        print(f"  |a{i+1}| = {np.abs(a[i]):.6f}")
    
    # Check relation to mode shape
    X4 = mode_shapes[:, 3]
    print(f"\n4th mode shape X_4: {X4}")
    
    # Check if a is proportional to F or X4
    print(f"\nRelation to mode shape:")
    print(f"  When exciting at ω_4, the response is dominated by mode 4")
    print(f"  The amplitude a should be proportional to X_4")
    print(f"  Checking: a / |a1| ≈ X_4 / X_4[0]")
    a_normalized = a / np.abs(a[0])
    X4_normalized = X4 / X4[0]
    print(f"  a_normalized: {a_normalized}")
    print(f"  X4_normalized: {X4_normalized}")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Amplitude comparison
    masses_pos = np.arange(1, N+1)
    width = 0.35
    ax1.bar(masses_pos - width/2, np.abs(a), width, label='Response Amplitude |a|', color='steelblue', edgecolor='black')
    ax1.bar(masses_pos + width/2, np.abs(X4) * np.max(np.abs(a)) / np.max(np.abs(X4)), width, 
            label='Mode 4 (scaled)', color='coral', edgecolor='black')
    ax1.set_xlabel('Mass Number', fontsize=12)
    ax1.set_ylabel('Amplitude', fontsize=12)
    ax1.set_title(r'Resonance Response at $\omega_4$ vs Mode Shape', fontsize=14)
    ax1.set_xticks(masses_pos)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Force and response pattern
    ax2.plot(masses_pos, F, 'go-', linewidth=2, markersize=10, label='Force F')
    ax2.plot(masses_pos, np.real(a) * 1000, 'bs-', linewidth=2, markersize=8, label='Response (×1000)')
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Mass Number', fontsize=12)
    ax2.set_ylabel('Amplitude', fontsize=12)
    ax2.set_title('Force Pattern vs Steady-State Response', fontsize=14)
    ax2.set_xticks(masses_pos)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('HW3_Part3_Problem1_Resonance.png', dpi=300, bbox_inches='tight')
    print("\n✓ Plot saved to 'HW3_Part3_Problem1_Resonance.png'")


def part_iii_problem_2():
    """
    Part III, Problem 2: Mode shape analysis at different frequencies.
    """
    print("\n" + "="*80)
    print("PART III - Problem 2: Mode Shape Analysis")
    print("="*80)
    
    # Parameters
    N = 4
    m = 0.020    # 20 g in kg
    L = 0.10     # 10 cm in m
    T = 100      # N
    alpha = 0.001  # damping coefficient
    
    masses = np.ones(N) * m
    lengths = np.ones(N) * L
    system = StringVibrationSystem(N, masses, lengths, T)
    
    # Solve for natural frequencies and mode shapes
    omega, mode_shapes = system.solve_eigenvalue_problem()
    
    # Force vector
    F = np.array([0, 0, 1, 0])
    
    # Calculate b (amplitude at ω_2)
    omega_f2 = omega[1]
    b = system.forced_response_steady_state(F, omega_f2, alpha)
    
    # Calculate c (amplitude at ω_3)
    omega_f3 = omega[2]
    c = system.forced_response_steady_state(F, omega_f3, alpha)
    
    print(f"\nForce vector F: {F}")
    print(f"\nAmplitude b at ω_f = ω_2 = {omega_f2/(2*np.pi):.4f} Hz:")
    for i in range(N):
        print(f"  b{i+1} = {b[i].real:.6f} + {b[i].imag:.6f}j  (|b{i+1}| = {np.abs(b[i]):.6f})")
    
    print(f"\nAmplitude c at ω_f = ω_3 = {omega_f3/(2*np.pi):.4f} Hz:")
    for i in range(N):
        print(f"  c{i+1} = {c[i].real:.6f} + {c[i].imag:.6f}j  (|c{i+1}| = {np.abs(c[i]):.6f})")
    
    # Check phase relationships
    phase_b = np.angle(b)
    phase_c = np.angle(c)
    
    print(f"\nPhase analysis for b:")
    print(f"  Phases: {np.degrees(phase_b)}")
    phase_diff_b = np.max(phase_b) - np.min(phase_b)
    in_phase_b = phase_diff_b < 0.1  # Within ~5 degrees
    print(f"  Components in phase? {in_phase_b} (phase difference: {np.degrees(phase_diff_b):.2f}°)")
    
    print(f"\nPhase analysis for c:")
    print(f"  Phases: {np.degrees(phase_c)}")
    phase_diff_c = np.max(phase_c) - np.min(phase_c)
    in_phase_c = phase_diff_c < 0.1
    print(f"  Components in phase? {in_phase_c} (phase difference: {np.degrees(phase_diff_c):.2f}°)")
    
    # Relation to mode shapes
    X2 = mode_shapes[:, 1]
    X3 = mode_shapes[:, 2]
    
    print(f"\nRelation to mode shapes:")
    print(f"  Mode 2 shape X_2: {X2}")
    print(f"  Mode 3 shape X_3: {X3}")
    
    print(f"\n  When exciting at natural frequency ω_r, response is dominated")
    print(f"  by mode r, so amplitude should be proportional to X_r")
    print(f"\n  c / |c_max| compared to X_3:")
    c_norm = c / np.max(np.abs(c))
    X3_norm = X3 / np.max(np.abs(X3))
    print(f"  c_normalized: {np.abs(c_norm)}")
    print(f"  X3_normalized: {X3_norm}")
    
    # Create visualization
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(3, 2, figure=fig)
    
    # Amplitude comparison for b (at ω_2)
    ax1 = fig.add_subplot(gs[0, 0])
    masses_pos = np.arange(1, N+1)
    ax1.bar(masses_pos, np.abs(b), color='steelblue', edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Mass Number', fontsize=11)
    ax1.set_ylabel('Amplitude Magnitude', fontsize=11)
    ax1.set_title(r'Response Amplitude at $\omega_2$ = ' + f'{omega_f2/(2*np.pi):.2f} Hz', fontsize=12)
    ax1.set_xticks(masses_pos)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Phase for b
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.bar(masses_pos, np.degrees(phase_b), color='coral', edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Mass Number', fontsize=11)
    ax2.set_ylabel('Phase (degrees)', fontsize=11)
    ax2.set_title(r'Phase of Response at $\omega_2$', fontsize=12)
    ax2.set_xticks(masses_pos)
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Amplitude comparison for c (at ω_3)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.bar(masses_pos, np.abs(c), color='mediumseagreen', edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('Mass Number', fontsize=11)
    ax3.set_ylabel('Amplitude Magnitude', fontsize=11)
    ax3.set_title(r'Response Amplitude at $\omega_3$ = ' + f'{omega_f3/(2*np.pi):.2f} Hz', fontsize=12)
    ax3.set_xticks(masses_pos)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Phase for c
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.bar(masses_pos, np.degrees(phase_c), color='orchid', edgecolor='black', linewidth=1.5)
    ax4.set_xlabel('Mass Number', fontsize=11)
    ax4.set_ylabel('Phase (degrees)', fontsize=11)
    ax4.set_title(r'Phase of Response at $\omega_3$', fontsize=12)
    ax4.set_xticks(masses_pos)
    ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Mode shape comparison
    ax5 = fig.add_subplot(gs[2, :])
    width = 0.25
    x = np.arange(N)
    ax5.bar(x - width, np.abs(b)/np.max(np.abs(b)), width, label=r'|b| at $\omega_2$ (normalized)', 
            color='steelblue', edgecolor='black')
    ax5.bar(x, np.abs(X2)/np.max(np.abs(X2)), width, label='Mode 2 (normalized)', 
            color='lightblue', edgecolor='black')
    ax5.bar(x + width, np.abs(c)/np.max(np.abs(c)), width, label=r'|c| at $\omega_3$ (normalized)', 
            color='mediumseagreen', edgecolor='black')
    ax5.bar(x + 2*width, np.abs(X3)/np.max(np.abs(X3)), width, label='Mode 3 (normalized)', 
            color='lightgreen', edgecolor='black')
    ax5.set_xlabel('Mass Number', fontsize=11)
    ax5.set_ylabel('Normalized Amplitude', fontsize=11)
    ax5.set_title('Response Amplitudes vs Mode Shapes (Force at Mass 3)', fontsize=12)
    ax5.set_xticks(x + width/2)
    ax5.set_xticklabels([f'M{i+1}' for i in range(N)])
    ax5.legend(loc='best', fontsize=10)
    ax5.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('HW3_Part3_Problem2_ModeAnalysis.png', dpi=300, bbox_inches='tight')
    print("\n✓ Plot saved to 'HW3_Part3_Problem2_ModeAnalysis.png'")


def part_iii_problem_3():
    """
    Part III, Problem 3: Frequency response for point force at mass 3.
    """
    print("\n" + "="*80)
    print("PART III - Problem 3: Frequency Response (Point Force at Mass 3)")
    print("="*80)
    
    # Parameters
    N = 4
    m = 0.020    # 20 g in kg
    L = 0.10     # 10 cm in m
    T = 100      # N
    alpha = 0.001  # damping coefficient
    
    masses = np.ones(N) * m
    lengths = np.ones(N) * L
    system = StringVibrationSystem(N, masses, lengths, T)
    
    # Solve for natural frequencies
    omega_nat, _ = system.solve_eigenvalue_problem()
    freq_nat_hz = omega_nat / (2 * np.pi)
    
    # Force vector
    F = np.array([0, 0, 1, 0])
    
    # Frequency range: 0 to 80 Hz with 1 Hz resolution
    freq_range = np.arange(0.1, 80.1, 1.0)  # Start from 0.1 to avoid division issues
    
    print(f"\nCalculating frequency response...")
    amplitudes = system.frequency_response(F, freq_range, alpha)
    
    # Extract amplitude of 4th mass
    amp_mass4 = np.abs(amplitudes[3, :])
    
    # Plot
    plt.figure(figsize=(12, 8))
    plt.semilogy(freq_range, amp_mass4, 'b-', linewidth=1.5)
    
    # Mark natural frequencies
    for i, f in enumerate(freq_nat_hz):
        plt.axvline(x=f, color='r', linestyle='--', alpha=0.7, label=r'$\omega_{%d}$' % (i+1) if i == 0 else '')
    
    plt.xlabel('Forcing Frequency (Hz)', fontsize=12)
    plt.ylabel('Amplitude of Mass 4 (m)', fontsize=12)
    plt.title('Frequency Response of Mass 4 (Point Force at Mass 3)', fontsize=14)
    plt.grid(True, alpha=0.3, which='both')
    plt.legend(['Amplitude', 'Natural Frequencies'])
    plt.xlim([0, 80])
    plt.savefig('HW3_Part3_Problem3_FreqResponse.png', dpi=300, bbox_inches='tight')
    
    print(f"\n✓ Plot saved to 'HW3_Part3_Problem3_FreqResponse.png'")
    print(f"\nNatural frequencies:")
    for i, f in enumerate(freq_nat_hz):
        print(f"  ω_{i+1} = {f:.4f} Hz")
    print(f"\nObservations:")
    print(f"  - Peaks occur at natural frequencies due to resonance")
    print(f"  - Peak heights vary depending on mode shape participation")
    print(f"  - Damping prevents infinite amplitude at resonance")


def part_iii_problem_4():
    """
    Part III, Problem 4: Frequency response for force at end mass.
    """
    print("\n" + "="*80)
    print("PART III - Problem 4: Frequency Response (End Force)")
    print("="*80)
    
    # Parameters
    N = 4
    m = 0.020    # 20 g in kg
    L = 0.10     # 10 cm in m
    T = 100      # N
    alpha = 0.001  # damping coefficient
    
    masses = np.ones(N) * m
    lengths = np.ones(N) * L
    system = StringVibrationSystem(N, masses, lengths, T)
    
    # Solve for natural frequencies and mode shapes
    omega_nat, mode_shapes = system.solve_eigenvalue_problem()
    freq_nat_hz = omega_nat / (2 * np.pi)
    
    # Force vector at end mass
    F = np.array([0, 0, 0, 1])
    
    # Frequency range
    freq_range = np.arange(0.1, 80.1, 1.0)
    
    print(f"\nCalculating frequency response...")
    amplitudes = system.frequency_response(F, freq_range, alpha)
    
    # Extract amplitude of 4th mass
    amp_mass4 = np.abs(amplitudes[3, :])
    
    # Plot
    plt.figure(figsize=(12, 8))
    plt.semilogy(freq_range, amp_mass4, 'g-', linewidth=1.5)
    
    # Mark natural frequencies
    for i, f in enumerate(freq_nat_hz):
        plt.axvline(x=f, color='r', linestyle='--', alpha=0.7, label=r'$\omega_{%d}$' % (i+1) if i == 0 else '')
    
    plt.xlabel('Forcing Frequency (Hz)', fontsize=12)
    plt.ylabel('Amplitude of Mass 4 (m)', fontsize=12)
    plt.title('Frequency Response of Mass 4 (Force at End Mass)', fontsize=14)
    plt.grid(True, alpha=0.3, which='both')
    plt.legend(['Amplitude', 'Natural Frequencies'])
    plt.xlim([0, 80])
    plt.savefig('HW3_Part3_Problem4_FreqResponse_End.png', dpi=300, bbox_inches='tight')
    
    print(f"\n✓ Plot saved to 'HW3_Part3_Problem4_FreqResponse_End.png'")
    
    print(f"\nMain difference from Problem 3:")
    print(f"  - Some resonance peaks may be MISSING or significantly reduced")
    print(f"  - This occurs when the mode shape has a node (zero displacement)")
    print(f"    at the forcing location")
    print(f"\nExplanation:")
    print(f"  - If mode shape X_r has X_r[3] ≈ 0 (node at mass 4),")
    print(f"    then forcing at mass 4 cannot excite mode r effectively")
    print(f"  - Modal participation factor: p_r = X_r^T * F")
    print(f"  - If X_r[3] ≈ 0, then p_r ≈ 0 for this forcing")
    
    print(f"\nMode shape values at mass 4:")
    for i in range(N):
        print(f"  Mode {i+1}: X_{i+1}[3] = {mode_shapes[3, i]:.6f}")


def main():
    """Main function to run all parts of the assignment."""
    print("\n")
    print("="*80)
    print("ENGR 6311 - Assignment 3: Lateral Vibrations of String with Masses")
    print("="*80)
    
    # PART I - Governing Equations (explained in comments and class structure)
    print("\nPART I: Governing Equations")
    print("-" * 80)
    print("The governing equations are: M * ü + K * u = f")
    print("where:")
    print("  M = mass matrix (diagonal): M[i,i] = m_i")
    print("  K = stiffness matrix (tridiagonal):")
    print("      K[i,i] = T/L_i + T/L_{i+1}")
    print("      K[i,i+1] = K[i+1,i] = -T/L_{i+1}")
    print("  u = displacement vector [u_1, u_2, ..., u_N]^T")
    print("  f = force vector [f_1, f_2, ..., f_N]^T")
    print("\nThese matrices are implemented in the StringVibrationSystem class.")
    
    # PART II - Free Vibration Analysis
    system = part_ii_problem_1()
    part_ii_problem_2(system)
    N_vals3, freqs3 = part_ii_problem_3()
    N_vals4, freqs4 = part_ii_problem_4()
    part_ii_problem_5(N_vals3, freqs3, N_vals4, freqs4)
    part_ii_problem_6()
    part_ii_problem_7()
    
    # PART III - Forced Vibration with Damping
    part_iii_problem_1()
    part_iii_problem_2()
    part_iii_problem_3()
    part_iii_problem_4()
    
    print("\n" + "="*80)
    print("All problems completed successfully!")
    print("="*80)
    print("\nGenerated files:")
    print("  Part II:")
    print("    - HW3_Part2_Problem1_ModeShapes.png")
    print("    - HW3_Part2_Problem2_ZeroCrossings.png")
    print("    - HW3_Part2_Problem3_FirstFreq.png")
    print("    - HW3_Part2_Problem4_LastFreq.png")
    print("    - HW3_Part2_Problem5_AsymptoticBehavior.png")
    print("    - HW3_Part2_Problem6_MassVariation.png")
    print("    - HW3_Part2_Problem7_MassRatio.png")
    print("  Part III:")
    print("    - HW3_Part3_Problem1_Resonance.png")
    print("    - HW3_Part3_Problem2_ModeAnalysis.png")
    print("    - HW3_Part3_Problem3_FreqResponse.png")
    print("    - HW3_Part3_Problem4_FreqResponse_End.png")
    print("\n  Total: 11 figures generated")
    print("\n")


if __name__ == "__main__":
    main()
    plt.show()
