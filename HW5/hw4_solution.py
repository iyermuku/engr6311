"""
ENGR 6311 - Homework 4 Solution

Part I:
    Modal equations for a fixed-fixed string with a point viscous damper.
Part II:
    Single-mode approximation for a pinned-pinned beam with center harmonic force,
    including the first nonlinear curvature term.

Running this script will:
1) Print derived coefficients and matrices.
2) Generate figures in HW4/figures.
3) Save numerical highlights in HW4/results_summary.txt.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


# Plot defaults for clean figures.
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 11


def modal_shape(n: int, x: np.ndarray, L: float) -> np.ndarray:
    """Pinned/fixed-end string mode shape used for fixed-fixed string displacement field."""
    return np.sin(n * np.pi * x / L)


def part_i_string_modal_model(
    L: float,
    tension: float,
    rhoA: float,
    c_d: float,
    x_d: float,
    n_modes: int,
) -> Dict[str, np.ndarray]:
    """
    Build truncated modal model for a fixed-fixed string with point viscous damper.

    Governing PDE:
        rhoA * y_tt + c_d * delta(x-x_d) * y_t - T * y_xx = 0

    Expansion:
        y(x,t) = sum q_n(t) * sin(n*pi*x/L)

    Modal equations (truncated to N modes):
        M q_ddot + C q_dot + K q = 0

    with:
        M = (rhoA*L/2) I
        K_nn = T*n^2*pi^2/(2L)
        C_mn = c_d * sin(m*pi*x_d/L) * sin(n*pi*x_d/L)
    """
    modes = np.arange(1, n_modes + 1)
    phi_d = np.sin(modes * np.pi * x_d / L)

    modal_mass = rhoA * L / 2.0
    M = modal_mass * np.eye(n_modes)

    k_diag = tension * (modes**2) * np.pi**2 / (2.0 * L)
    K = np.diag(k_diag)

    # Rank-1 damping coupling induced by a single physical damper.
    C = c_d * np.outer(phi_d, phi_d)

    omega_n = modes * np.pi / L * np.sqrt(tension / rhoA)

    # Mass-normalized equations: q_ddot + Cn q_dot + Omega^2 q = 0
    Cn = C / modal_mass
    Omega2 = np.diag(omega_n**2)

    return {
        "modes": modes,
        "phi_d": phi_d,
        "M": M,
        "C": C,
        "K": K,
        "Cn": Cn,
        "Omega2": Omega2,
        "omega_n": omega_n,
        "modal_mass": np.array([modal_mass]),
    }


def part_ii_beam_single_mode(
    L: float,
    EI: float,
    rhoA: float,
    F0: float,
    Omega: float,
    damping_ratio: float = 0.01,
) -> Dict[str, float]:
    """
    Compute single-mode Duffing-type coefficients for a pinned-pinned beam.

    Using y(x,t)=q(t)*sin(pi x/L) and curvature approximation:
        kappa = y_xx / (1 + y_x^2)^(3/2) ~ y_xx * (1 - 1.5*y_x^2)

    First nonlinear retained term leads to:
        M q_ddot + C q_dot + K q - K3 q^3 = P cos(Omega t)

    where:
        M  = rhoA*L/2
        K  = EI*pi^4/(2*L^3)
        K3 = (3/4)*EI*pi^6/L^5   (softening cubic)
        P  = F0*sin(pi/2) = F0
    """
    M = rhoA * L / 2.0
    K = EI * np.pi**4 / (2.0 * L**3)
    K3 = 0.75 * EI * np.pi**6 / (L**5)
    P = F0

    omega1 = np.sqrt(K / M)
    C = 2.0 * damping_ratio * M * omega1

    beta = K3 / M
    forcing_per_mass = P / M

    return {
        "M": M,
        "C": C,
        "K": K,
        "K3": K3,
        "P": P,
        "omega1": omega1,
        "beta": beta,
        "forcing_per_mass": forcing_per_mass,
        "Omega": Omega,
    }


def simulate_linear_nonlinear(
    coeffs: Dict[str, float],
    q0: float = 0.0,
    qd0: float = 0.0,
    t_end: float = 30.0,
    points: int = 6000,
):
    """Integrate linear and nonlinear first-mode equations in time."""
    M = coeffs["M"]
    C = coeffs["C"]
    K = coeffs["K"]
    K3 = coeffs["K3"]
    P = coeffs["P"]
    Omega = coeffs["Omega"]

    def rhs_linear(t: float, state: np.ndarray) -> np.ndarray:
        q, qd = state
        qdd = (P * np.cos(Omega * t) - C * qd - K * q) / M
        return np.array([qd, qdd])

    def rhs_nonlinear(t: float, state: np.ndarray) -> np.ndarray:
        q, qd = state
        qdd = (P * np.cos(Omega * t) - C * qd - K * q + K3 * q**3) / M
        return np.array([qd, qdd])

    t_eval = np.linspace(0.0, t_end, points)

    sol_lin = solve_ivp(
        rhs_linear,
        (0.0, t_end),
        y0=np.array([q0, qd0]),
        t_eval=t_eval,
        method="RK45",
        rtol=1e-7,
        atol=1e-9,
    )

    sol_nonlin = solve_ivp(
        rhs_nonlinear,
        (0.0, t_end),
        y0=np.array([q0, qd0]),
        t_eval=t_eval,
        method="RK45",
        rtol=1e-7,
        atol=1e-9,
    )

    return sol_lin, sol_nonlin


def save_figures_and_summary(base_dir: Path) -> None:
    """Run both parts, save figures, and write a compact numerical summary file."""
    fig_dir = base_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Part I: string modal model
    # -------------------------
    string_params = {
        "L": 1.2,
        "tension": 120.0,
        "rhoA": 0.08,
        "c_d": 0.35,
        "x_d": 0.37,
        "n_modes": 6,
    }
    p1 = part_i_string_modal_model(**string_params)

    plt.figure(figsize=(8, 6))
    plt.imshow(p1["Cn"], cmap="viridis", aspect="auto")
    plt.colorbar(label="Mass-normalized damping coefficient")
    plt.title("Part I: Modal Damping Coupling Matrix")
    plt.xlabel("Mode index n")
    plt.ylabel("Mode index m")
    plt.tight_layout()
    plt.savefig(fig_dir / "part1_modal_damping_matrix.png", dpi=220)
    plt.close()

    # ----------------------------
    # Part II: beam single-mode ODE
    # ----------------------------
    beam_params = {
        "L": 1.0,
        "EI": 65.0,
        "rhoA": 0.75,
        "F0": 0.45,
        "Omega": 0.92 * np.sqrt(65.0 * np.pi**4 / (0.75 * 1.0**4)),
        "damping_ratio": 0.02,
    }
    p2 = part_ii_beam_single_mode(**beam_params)

    sol_lin, sol_nonlin = simulate_linear_nonlinear(
        p2,
        q0=0.0,
        qd0=0.0,
        t_end=25.0,
        points=5000,
    )

    # Time-history figure.
    plt.figure(figsize=(10, 5))
    plt.plot(sol_lin.t, sol_lin.y[0], label="Linear first-mode model", linewidth=1.7)
    plt.plot(sol_nonlin.t, sol_nonlin.y[0], label="Nonlinear first-mode model", linewidth=1.7)
    plt.title("Part II: Generalized Coordinate Response q(t)")
    plt.xlabel("Time (s)")
    plt.ylabel("q(t) (m, generalized)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "part2_time_history.png", dpi=220)
    plt.close()

    # Phase portrait (last part of simulation to approximate steady state).
    tail = int(0.35 * sol_nonlin.y.shape[1])
    plt.figure(figsize=(6.5, 5.5))
    plt.plot(sol_lin.y[0, -tail:], sol_lin.y[1, -tail:], label="Linear", linewidth=1.3)
    plt.plot(sol_nonlin.y[0, -tail:], sol_nonlin.y[1, -tail:], label="Nonlinear", linewidth=1.3)
    plt.title("Part II: Phase Portrait (Late-Time Response)")
    plt.xlabel("q")
    plt.ylabel("dq/dt")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "part2_phase_portrait.png", dpi=220)
    plt.close()

    # Save summary values used by report script.
    summary_path = base_dir / "results_summary.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write("[Part I Parameters]\n")
        for k, v in string_params.items():
            f.write(f"{k}={v}\n")

        f.write("\n[Part I Key Results]\n")
        f.write(f"modal_mass={p1['modal_mass'][0]:.8f}\n")
        f.write(f"omega_1={p1['omega_n'][0]:.8f}\n")
        f.write(f"omega_{string_params['n_modes']}={p1['omega_n'][-1]:.8f}\n")
        f.write(f"C11={p1['C'][0,0]:.8f}\n")
        f.write(f"C12={p1['C'][0,1]:.8f}\n")

        f.write("\n[Part II Parameters]\n")
        for k, v in beam_params.items():
            f.write(f"{k}={v}\n")

        f.write("\n[Part II Key Results]\n")
        f.write(f"M={p2['M']:.8f}\n")
        f.write(f"C={p2['C']:.8f}\n")
        f.write(f"K={p2['K']:.8f}\n")
        f.write(f"K3={p2['K3']:.8f}\n")
        f.write(f"omega1={p2['omega1']:.8f}\n")
        f.write(f"beta={p2['beta']:.8f}\n")

        lin_peak = float(np.max(np.abs(sol_lin.y[0])))
        nonlin_peak = float(np.max(np.abs(sol_nonlin.y[0])))
        f.write(f"linear_peak_q={lin_peak:.8f}\n")
        f.write(f"nonlinear_peak_q={nonlin_peak:.8f}\n")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    save_figures_and_summary(base_dir)

    print("HW4 solution artifacts generated successfully.")
    print(f"- Figures folder: {base_dir / 'figures'}")
    print(f"- Summary file:   {base_dir / 'results_summary.txt'}")

    print("\nPart I (general modal equation):")
    print("M q_ddot + C q_dot + K q = 0")
    print("C_mn = c_d * sin(m*pi*x_d/L) * sin(n*pi*x_d/L)")

    print("\nPart II (single-mode nonlinear beam equation):")
    print("M q_ddot + C q_dot + K q - K3 q^3 = P cos(Omega t)")


if __name__ == "__main__":
    main()
