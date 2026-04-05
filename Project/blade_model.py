"""Bladed-disk matrix model for tuned and mistuned cyclic assemblies.

This module provides helper functions to build nondimensional matrices for a
ring of Nb coupled SDOF blades and compute steady-state complex response.

Quick start from repository root:

1) Single tuned solve at one frequency
    python Project/blade_model.py --nb 6 --h 0.01 --kc 0.01 --omega 1.0

2) Tuned response chart for two coupling cases
    python Project/blade_model.py --nb 6 --h 0.01 --kc 0.01 --make-chart \
      --kc-list 0.01 0.05 --omega-min 0.6 --omega-max 1.5 --num-points 700 \
      --chart-output Project/figures/response_nb6_h001_kc001_005.png

3) Monte Carlo statistics chart (Part IIIb)
    python Project/blade_model.py --nb 6 --h 0.01 --kc 0.01 --make-statistics-chart \
      --kc-list 0.01 0.05 --mistune-magnitudes 0.01 0.05 --stats-samples 100 \
      --omega-min 0.6 --omega-max 1.5 --num-points 700 \
      --stats-output Project/figures/mistuning_statistics_nb6.png

4) AF histograms (Part IIIc)
    python Project/blade_model.py --nb 6 --h 0.01 --kc 0.01 --make-af-histogram \
      --kc-list 0.01 0.05 --mistune-magnitudes 0.01 0.05 --stats-samples 100 \
      --omega-min 0.6 --omega-max 1.5 --num-points 700 --af-bins 20 \
      --af-output Project/figures/af_histograms_nb6.png

5) Surrogate vs Monte Carlo comparison (Part Vb)
    python Project/blade_model.py --nb 6 --h 0.01 --kc 0.01 --make-surrogate-comparison \
      --kc-list 0.01 0.05 --mistune-magnitudes 0.01 0.05 --stats-samples 100 \
      --surrogate-train-samples 30 --surrogate-eval-samples 3000 \
      --omega-min 0.6 --omega-max 1.5 --num-points 700 \
      --surrogate-output Project/figures/surrogate_vs_mc_nb6.png
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np


def _cyclic_coupling_matrix(nb: int) -> np.ndarray:
    """Build the ring Laplacian matrix with 2 on the diagonal and -1 to neighbors."""
    if nb < 2:
        raise ValueError("nb must be at least 2")

    L = np.zeros((nb, nb), dtype=float)
    for j in range(nb):
        L[j, j] = 2.0
        L[j, (j - 1) % nb] = -1.0
        L[j, (j + 1) % nb] = -1.0
    return L


def build_nondimensional_mck(
    nb: int,
    kc: float,
    h: float,
    delta_m: Optional[np.ndarray] = None,
    delta_k: Optional[np.ndarray] = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build nondimensional M, C, K from Eq. (1) in the README."""
    delta_m_arr = np.zeros(nb) if delta_m is None else np.asarray(delta_m, dtype=float)
    delta_k_arr = np.zeros(nb) if delta_k is None else np.asarray(delta_k, dtype=float)

    if delta_m_arr.shape != (nb,) or delta_k_arr.shape != (nb,):
        raise ValueError("delta_m and delta_k must have shape (nb,)")

    M = np.diag(1.0 + delta_m_arr)
    C = h * np.eye(nb)
    K_tuned = np.eye(nb) + kc * _cyclic_coupling_matrix(nb)
    K = K_tuned + np.diag(delta_k_arr)
    return M, C, K


def traveling_wave_force(nb: int, amplitude: float = 1.0) -> np.ndarray:
    """Complex force vector F_hat for F_j = amplitude*cos(w t - 2*pi*j/nb)."""
    j = np.arange(1, nb + 1)
    return amplitude * np.exp(-1j * 2.0 * np.pi * j / nb)


def dynamic_stiffness(M: np.ndarray, C: np.ndarray, K: np.ndarray, omega: float) -> np.ndarray:
    """Build dynamic stiffness matrix Z(omega) = -omega^2 M + i*omega*C + K."""
    return -(omega**2) * M + 1j * omega * C + K


def steady_state_response(
    M: np.ndarray,
    C: np.ndarray,
    K: np.ndarray,
    omega: float,
    F_hat: np.ndarray,
) -> np.ndarray:
    """Solve Z(omega) X = F_hat for the complex steady-state amplitude X."""
    Z = dynamic_stiffness(M, C, K, omega)
    return np.linalg.solve(Z, F_hat)


def frequency_response_max_amplitude(
    nb: int,
    h: float,
    kc: float,
    omega_values: np.ndarray,
    delta_m: Optional[np.ndarray] = None,
    delta_k: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Compute max blade amplitude over a frequency sweep."""
    M, C, K = build_nondimensional_mck(
        nb=nb,
        kc=kc,
        h=h,
        delta_m=delta_m,
        delta_k=delta_k,
    )
    F_hat = traveling_wave_force(nb, amplitude=1.0)

    amplitudes = np.zeros_like(omega_values, dtype=float)
    for i, omega in enumerate(omega_values):
        X = steady_state_response(M, C, K, omega=omega, F_hat=F_hat)
        amplitudes[i] = np.max(np.abs(X))
    return amplitudes


def blade_response_amplitude(
    nb: int,
    h: float,
    kc: float,
    omega_values: np.ndarray,
    blade_index: int = 0,
    delta_m: Optional[np.ndarray] = None,
    delta_k: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Compute the amplitude of one blade over a frequency sweep."""
    M, C, K = build_nondimensional_mck(
        nb=nb,
        kc=kc,
        h=h,
        delta_m=delta_m,
        delta_k=delta_k,
    )
    F_hat = traveling_wave_force(nb, amplitude=1.0)

    amplitudes = np.zeros_like(omega_values, dtype=float)
    for i, omega in enumerate(omega_values):
        X = steady_state_response(M, C, K, omega=omega, F_hat=F_hat)
        amplitudes[i] = np.abs(X[blade_index])
    return amplitudes


def generate_mistuning_sample(
    nb: int,
    magnitude: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate one random mistuning vector delta_k = magnitude * r."""
    r = rng.standard_normal(nb)
    r = np.clip(r, -1.0, 1.0)
    return magnitude * r


def build_surrogate_features(delta_k_samples: np.ndarray) -> np.ndarray:
    """Build simple polynomial features [1, x_i, x_i^2] for each mistuning sample."""
    linear = delta_k_samples
    quadratic = delta_k_samples**2
    bias = np.ones((delta_k_samples.shape[0], 1), dtype=float)
    return np.hstack([bias, linear, quadratic])


def train_blade_response_surrogate(
    nb: int,
    h: float,
    kc: float,
    omega_values: np.ndarray,
    magnitude: float,
    num_train: int,
    blade_index: int = 0,
    seed: int = 6311,
) -> np.ndarray:
    """Train a frequency-wise polynomial surrogate for |X_j|.

    Returns
    -------
    beta : ndarray, shape (1 + 2*nb, n_freq)
        Least-squares coefficients for each frequency point.
    """
    rng = np.random.default_rng(seed)
    Y = np.zeros((num_train, omega_values.size), dtype=float)
    delta_k_samples = np.zeros((num_train, nb), dtype=float)

    for i in range(num_train):
        delta_k = generate_mistuning_sample(nb=nb, magnitude=magnitude, rng=rng)
        delta_k_samples[i, :] = delta_k
        Y[i, :] = blade_response_amplitude(
            nb=nb,
            h=h,
            kc=kc,
            omega_values=omega_values,
            blade_index=blade_index,
            delta_m=np.zeros(nb),
            delta_k=delta_k,
        )

    Phi = build_surrogate_features(delta_k_samples)
    beta, *_ = np.linalg.lstsq(Phi, Y, rcond=None)
    return beta


def surrogate_statistics(
    nb: int,
    magnitude: float,
    beta: np.ndarray,
    num_eval: int,
    seed: int = 7001,
) -> tuple[np.ndarray, np.ndarray]:
    """Predict mean/std using surrogate with many cheap random evaluations."""
    rng = np.random.default_rng(seed)
    delta_k_eval = np.zeros((num_eval, nb), dtype=float)
    for i in range(num_eval):
        delta_k_eval[i, :] = generate_mistuning_sample(nb=nb, magnitude=magnitude, rng=rng)

    Phi_eval = build_surrogate_features(delta_k_eval)
    Y_pred = Phi_eval @ beta
    return Y_pred.mean(axis=0), Y_pred.std(axis=0)


def surrogate_vs_monte_carlo(
    nb: int,
    h: float,
    kc: float,
    omega_values: np.ndarray,
    magnitude: float,
    num_mc: int,
    num_train: int,
    num_surrogate_eval: int,
    blade_index: int = 0,
    seed: int = 6311,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict]:
    """Compare surrogate statistics against direct Monte Carlo statistics."""
    mean_mc, std_mc, tuned = monte_carlo_blade_statistics(
        nb=nb,
        h=h,
        kc=kc,
        omega_values=omega_values,
        magnitude=magnitude,
        num_samples=num_mc,
        blade_index=blade_index,
        seed=seed,
    )

    beta = train_blade_response_surrogate(
        nb=nb,
        h=h,
        kc=kc,
        omega_values=omega_values,
        magnitude=magnitude,
        num_train=num_train,
        blade_index=blade_index,
        seed=seed + 100,
    )
    mean_sur, std_sur = surrogate_statistics(
        nb=nb,
        magnitude=magnitude,
        beta=beta,
        num_eval=num_surrogate_eval,
        seed=seed + 200,
    )

    eps = 1e-12
    errors = {
        "mean_rel_l2": float(np.linalg.norm(mean_sur - mean_mc) / (np.linalg.norm(mean_mc) + eps)),
        "std_rel_l2": float(np.linalg.norm(std_sur - std_mc) / (np.linalg.norm(std_mc) + eps)),
        "mean_peak_abs": float(np.max(np.abs(mean_sur - mean_mc))),
        "std_peak_abs": float(np.max(np.abs(std_sur - std_mc))),
        "mean_peak_rel_pct": float(100.0 * np.max(np.abs(mean_sur - mean_mc) / (np.maximum(mean_mc, eps)))),
        "std_peak_rel_pct": float(100.0 * np.max(np.abs(std_sur - std_mc) / (np.maximum(std_mc, eps)))),
    }
    return mean_mc, std_mc, mean_sur, std_sur, errors


def monte_carlo_blade_statistics(
    nb: int,
    h: float,
    kc: float,
    omega_values: np.ndarray,
    magnitude: float,
    num_samples: int,
    blade_index: int = 0,
    seed: int = 6311,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute mean/std of one blade response over mistuned assemblies."""
    rng = np.random.default_rng(seed)
    samples = np.zeros((num_samples, omega_values.size), dtype=float)

    for sample_index in range(num_samples):
        delta_m = np.zeros(nb)
        delta_k = generate_mistuning_sample(nb=nb, magnitude=magnitude, rng=rng)
        samples[sample_index, :] = blade_response_amplitude(
            nb=nb,
            h=h,
            kc=kc,
            omega_values=omega_values,
            blade_index=blade_index,
            delta_m=delta_m,
            delta_k=delta_k,
        )

    mean_response = samples.mean(axis=0)
    std_response = samples.std(axis=0)
    tuned_response = blade_response_amplitude(
        nb=nb,
        h=h,
        kc=kc,
        omega_values=omega_values,
        blade_index=blade_index,
    )
    return mean_response, std_response, tuned_response


def global_max_response(
    nb: int,
    h: float,
    kc: float,
    omega_values: np.ndarray,
    delta_m: Optional[np.ndarray] = None,
    delta_k: Optional[np.ndarray] = None,
) -> float:
    """Compute max over all blades and frequencies: max_{j,omega}|X_j(omega)|."""
    M, C, K = build_nondimensional_mck(
        nb=nb,
        kc=kc,
        h=h,
        delta_m=delta_m,
        delta_k=delta_k,
    )
    F_hat = traveling_wave_force(nb, amplitude=1.0)

    max_val = 0.0
    for omega in omega_values:
        X = steady_state_response(M, C, K, omega=omega, F_hat=F_hat)
        max_val = max(max_val, float(np.max(np.abs(X))))
    return max_val


def amplification_factor(
    nb: int,
    h: float,
    kc: float,
    omega_values: np.ndarray,
    delta_m: Optional[np.ndarray] = None,
    delta_k: Optional[np.ndarray] = None,
) -> float:
    """Compute AF = max mistuned response / max tuned response."""
    tuned_max = global_max_response(nb=nb, h=h, kc=kc, omega_values=omega_values)
    mist_max = global_max_response(
        nb=nb,
        h=h,
        kc=kc,
        omega_values=omega_values,
        delta_m=delta_m,
        delta_k=delta_k,
    )
    return mist_max / tuned_max


def monte_carlo_af_distribution(
    nb: int,
    h: float,
    kc: float,
    omega_values: np.ndarray,
    magnitude: float,
    num_samples: int,
    seed: int = 6311,
) -> np.ndarray:
    """Compute AF samples for random mistuned assemblies at one M and kc."""
    rng = np.random.default_rng(seed)
    tuned_max = global_max_response(nb=nb, h=h, kc=kc, omega_values=omega_values)

    af_values = np.zeros(num_samples, dtype=float)
    for i in range(num_samples):
        delta_m = np.zeros(nb)
        delta_k = generate_mistuning_sample(nb=nb, magnitude=magnitude, rng=rng)
        mist_max = global_max_response(
            nb=nb,
            h=h,
            kc=kc,
            omega_values=omega_values,
            delta_m=delta_m,
            delta_k=delta_k,
        )
        af_values[i] = mist_max / tuned_max
    return af_values


def generate_response_chart(
    nb: int,
    h: float,
    kc_values: list[float],
    omega_min: float,
    omega_max: float,
    num_points: int,
    output_path: Path,
) -> Path:
    """Generate and save frequency-response chart for one or more coupling values."""
    omega_values = np.linspace(omega_min, omega_max, num_points)

    plt.figure(figsize=(9, 5.5))
    for kc in kc_values:
        response = frequency_response_max_amplitude(
            nb=nb,
            h=h,
            kc=kc,
            omega_values=omega_values,
        )
        plt.plot(omega_values, response, linewidth=2.0, label=f"kc = {kc:.3f}")

    plt.xlabel("Nondimensional forcing frequency omega_f")
    plt.ylabel("Max steady-state amplitude max_j |X_j|")
    plt.title(f"Bladed Ring Response (Nb={nb}, h={h})")
    plt.grid(True, alpha=0.35)
    plt.legend()
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    return output_path


def generate_statistics_chart(
    nb: int,
    h: float,
    kc_values: list[float],
    mistune_magnitudes: list[float],
    omega_min: float,
    omega_max: float,
    num_points: int,
    num_samples: int,
    output_path: Path,
    blade_index: int = 0,
    seed: int = 6311,
) -> Path:
    """Generate Monte Carlo statistics charts for mistuned blade response."""
    omega_values = np.linspace(omega_min, omega_max, num_points)

    fig, axes = plt.subplots(
        len(mistune_magnitudes),
        len(kc_values),
        figsize=(5.2 * len(kc_values), 4.2 * len(mistune_magnitudes)),
        sharex=True,
        sharey=False,
    )

    axes_array = np.atleast_2d(axes)

    for row_index, magnitude in enumerate(mistune_magnitudes):
        for col_index, kc in enumerate(kc_values):
            axis = axes_array[row_index, col_index]
            mean_response, std_response, tuned_response = monte_carlo_blade_statistics(
                nb=nb,
                h=h,
                kc=kc,
                omega_values=omega_values,
                magnitude=magnitude,
                num_samples=num_samples,
                blade_index=blade_index,
                seed=seed + 17 * row_index + col_index,
            )

            axis.plot(omega_values, tuned_response, color="black", linestyle="--", linewidth=2.0, label="tuned")
            axis.plot(omega_values, mean_response, color="tab:blue", linewidth=2.0, label="mean mistuned")
            axis.fill_between(
                omega_values,
                mean_response - std_response,
                mean_response + std_response,
                color="tab:blue",
                alpha=0.2,
                label="mean ± 1 std",
            )
            axis.set_title(f"kc={kc:.3f}, M={100.0 * magnitude:.1f}%")
            axis.grid(True, alpha=0.35)

            if col_index == 0:
                axis.set_ylabel("Blade amplitude |X_j|")
            if row_index == len(mistune_magnitudes) - 1:
                axis.set_xlabel("Nondimensional forcing frequency omega_f")
            if row_index == 0 and col_index == len(kc_values) - 1:
                axis.legend(loc="best")

    fig.suptitle(f"Mistuned Response Statistics for Blade {blade_index + 1}", y=0.995)
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def generate_af_histograms(
    nb: int,
    h: float,
    kc_values: list[float],
    mistune_magnitudes: list[float],
    omega_min: float,
    omega_max: float,
    num_points: int,
    num_samples: int,
    output_path: Path,
    bins: int = 20,
    seed: int = 6311,
) -> tuple[Path, list[tuple[float, float, float, float, float]]]:
    """Generate AF histogram grid and return summary stats per panel.

    Returns
    -------
    output_path : Path
        Saved figure path.
    summary_rows : list of tuples
        (kc, M, mean_af, std_af, max_af)
    """
    omega_values = np.linspace(omega_min, omega_max, num_points)
    fig, axes = plt.subplots(
        len(mistune_magnitudes),
        len(kc_values),
        figsize=(5.2 * len(kc_values), 4.2 * len(mistune_magnitudes)),
        sharex=False,
        sharey=False,
    )
    axes_array = np.atleast_2d(axes)

    summary_rows: list[tuple[float, float, float, float, float]] = []

    for row_index, magnitude in enumerate(mistune_magnitudes):
        for col_index, kc in enumerate(kc_values):
            axis = axes_array[row_index, col_index]
            af_values = monte_carlo_af_distribution(
                nb=nb,
                h=h,
                kc=kc,
                omega_values=omega_values,
                magnitude=magnitude,
                num_samples=num_samples,
                seed=seed + 17 * row_index + col_index,
            )

            mean_af = float(np.mean(af_values))
            std_af = float(np.std(af_values))
            max_af = float(np.max(af_values))
            summary_rows.append((kc, magnitude, mean_af, std_af, max_af))

            axis.hist(af_values, bins=bins, color="tab:blue", alpha=0.75, edgecolor="white")
            axis.axvline(1.0, color="black", linestyle="--", linewidth=1.8, label="AF = 1")
            axis.axvline(mean_af, color="tab:red", linestyle="-", linewidth=1.8, label=f"mean = {mean_af:.3f}")
            axis.set_title(f"kc={kc:.3f}, M={100.0 * magnitude:.1f}%")
            axis.set_xlabel("Amplification factor (AF)")
            if col_index == 0:
                axis.set_ylabel("Count")
            axis.grid(True, alpha=0.3)
            axis.legend(loc="best")

    fig.suptitle("Amplification Factor Histograms", y=0.995)
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path, summary_rows


def generate_surrogate_comparison_chart(
    nb: int,
    h: float,
    kc_values: list[float],
    mistune_magnitudes: list[float],
    omega_min: float,
    omega_max: float,
    num_points: int,
    num_mc_samples: int,
    num_train_samples: int,
    num_surrogate_eval: int,
    output_path: Path,
    blade_index: int = 0,
    seed: int = 6311,
) -> tuple[Path, list[tuple[float, float, float, float, float, float]]]:
    """Generate surrogate-vs-MC plots and return error summary rows.

    Returns rows as (kc, M, mean_rel_l2, std_rel_l2, mean_peak_rel_pct, std_peak_rel_pct).
    """
    omega_values = np.linspace(omega_min, omega_max, num_points)
    fig, axes = plt.subplots(
        len(mistune_magnitudes),
        len(kc_values),
        figsize=(5.2 * len(kc_values), 4.2 * len(mistune_magnitudes)),
        sharex=True,
        sharey=False,
    )
    axes_array = np.atleast_2d(axes)
    summary_rows: list[tuple[float, float, float, float, float, float]] = []

    for row_index, magnitude in enumerate(mistune_magnitudes):
        for col_index, kc in enumerate(kc_values):
            axis = axes_array[row_index, col_index]
            mean_mc, std_mc, mean_sur, std_sur, errors = surrogate_vs_monte_carlo(
                nb=nb,
                h=h,
                kc=kc,
                omega_values=omega_values,
                magnitude=magnitude,
                num_mc=num_mc_samples,
                num_train=num_train_samples,
                num_surrogate_eval=num_surrogate_eval,
                blade_index=blade_index,
                seed=seed + 23 * row_index + col_index,
            )

            summary_rows.append(
                (
                    kc,
                    magnitude,
                    errors["mean_rel_l2"],
                    errors["std_rel_l2"],
                    errors["mean_peak_rel_pct"],
                    errors["std_peak_rel_pct"],
                )
            )

            axis.plot(omega_values, mean_mc, color="tab:blue", linewidth=2.0, label="MC mean")
            axis.plot(omega_values, mean_sur, color="tab:orange", linewidth=2.0, linestyle="--", label="surrogate mean")
            axis.fill_between(
                omega_values,
                mean_mc - std_mc,
                mean_mc + std_mc,
                color="tab:blue",
                alpha=0.15,
                label="MC ± 1 std",
            )
            axis.fill_between(
                omega_values,
                mean_sur - std_sur,
                mean_sur + std_sur,
                color="tab:orange",
                alpha=0.12,
                label="surrogate ± 1 std",
            )
            axis.set_title(
                f"kc={kc:.3f}, M={100.0*magnitude:.1f}%\n"
                f"e_mean={100.0*errors['mean_rel_l2']:.2f}%, e_std={100.0*errors['std_rel_l2']:.2f}%"
            )
            axis.grid(True, alpha=0.35)
            if col_index == 0:
                axis.set_ylabel("Blade amplitude |X_j|")
            if row_index == len(mistune_magnitudes) - 1:
                axis.set_xlabel("Nondimensional forcing frequency omega_f")
            if row_index == 0 and col_index == len(kc_values) - 1:
                axis.legend(loc="best", fontsize=9)

    fig.suptitle(f"Surrogate vs Monte Carlo (Blade {blade_index + 1})", y=0.995)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path, summary_rows


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build tuned blade-ring matrices and optional response chart."
    )
    # Core model parameters.
    parser.add_argument("--nb", type=int, default=8, help="Number of blades")
    parser.add_argument("--h", type=float, default=0.01, help="Nondimensional damping h")
    parser.add_argument("--kc", type=float, default=0.05, help="Nondimensional coupling kc")
    parser.add_argument("--omega", type=float, default=1.0, help="Nondimensional excitation frequency")
    parser.add_argument(
        "--kc-list",
        type=float,
        nargs="+",
        default=[0.05],
        help="One or more kc values for frequency-response chart",
    )
    # Frequency sweep controls used by all chart workflows.
    parser.add_argument("--omega-min", type=float, default=0.6, help="Chart sweep minimum")
    parser.add_argument("--omega-max", type=float, default=1.5, help="Chart sweep maximum")
    parser.add_argument("--num-points", type=int, default=600, help="Chart sweep points")
    parser.add_argument(
        "--chart-output",
        type=str,
        default="Project/figures/tuned_response_chart.png",
        help="Output image path for response chart",
    )
    # Turn on to draw the tuned response chart for one or more kc cases.
    parser.add_argument(
        "--make-chart",
        action="store_true",
        help="Generate frequency-response chart for kc-list",
    )
    # Turn on to draw Monte Carlo mean/std response charts.
    parser.add_argument(
        "--make-statistics-chart",
        action="store_true",
        help="Generate Monte Carlo statistics chart for mistuned assemblies",
    )
    # Turn on to draw AF histograms over random mistuned assemblies.
    parser.add_argument(
        "--make-af-histogram",
        action="store_true",
        help="Generate amplification-factor histograms for Monte Carlo mistuned assemblies",
    )
    # Turn on to compare surrogate statistics against direct Monte Carlo.
    parser.add_argument(
        "--make-surrogate-comparison",
        action="store_true",
        help="Generate surrogate-vs-Monte-Carlo comparison chart and errors",
    )
    parser.add_argument(
        "--mistune-scale",
        type=float,
        default=0.0,
        help="Uniform random mistuning magnitude for delta_m and delta_k",
    )
    parser.add_argument(
        "--delta-m",
        type=float,
        nargs="*",
        default=None,
        help="Explicit nondimensional mass mistuning vector of length nb",
    )
    parser.add_argument(
        "--delta-k",
        type=float,
        nargs="*",
        default=None,
        help="Explicit nondimensional stiffness mistuning vector of length nb",
    )
    parser.add_argument(
        "--mistune-magnitudes",
        type=float,
        nargs="+",
        default=[0.01, 0.05],
        help="Mistuning magnitudes M for statistics plots",
    )
    parser.add_argument(
        "--stats-samples",
        type=int,
        default=100,
        help="Number of mistuned assemblies per mistuning magnitude",
    )
    parser.add_argument(
        "--stats-output",
        type=str,
        default="Project/figures/mistuning_statistics_nb6.png",
        help="Output image path for statistics chart",
    )
    parser.add_argument(
        "--stats-blade-index",
        type=int,
        default=0,
        help="Blade index used for the statistics plot",
    )
    parser.add_argument(
        "--surrogate-train-samples",
        type=int,
        default=30,
        help="Number of full solves used to train surrogate per case",
    )
    parser.add_argument(
        "--surrogate-eval-samples",
        type=int,
        default=3000,
        help="Number of surrogate evaluations per case for statistics",
    )
    parser.add_argument(
        "--surrogate-output",
        type=str,
        default="Project/figures/surrogate_vs_mc_nb6.png",
        help="Output image path for surrogate comparison figure",
    )
    parser.add_argument(
        "--af-output",
        type=str,
        default="Project/figures/af_histograms_nb6.png",
        help="Output image path for AF histogram figure",
    )
    parser.add_argument(
        "--af-bins",
        type=int,
        default=20,
        help="Number of bins for AF histograms",
    )
    parser.add_argument("--seed", type=int, default=6311, help="Random seed")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    # Mistuning input priority:
    # 1) Explicit vectors (--delta-m and --delta-k), if supplied.
    # 2) Random mistuning from --mistune-scale.
    # 3) Tuned case (all zeros).
    if args.delta_m is not None or args.delta_k is not None:
        if args.delta_m is None or args.delta_k is None:
            raise ValueError("Both --delta-m and --delta-k must be provided together.")
        delta_m = np.asarray(args.delta_m, dtype=float)
        delta_k = np.asarray(args.delta_k, dtype=float)
        if delta_m.shape != (args.nb,) or delta_k.shape != (args.nb,):
            raise ValueError("Explicit mistuning vectors must have length nb.")
    else:
        rng = np.random.default_rng(args.seed)
        if args.mistune_scale > 0.0:
            delta_m = rng.uniform(-args.mistune_scale, args.mistune_scale, size=args.nb)
            delta_k = rng.uniform(-args.mistune_scale, args.mistune_scale, size=args.nb)
        else:
            delta_m = np.zeros(args.nb)
            delta_k = np.zeros(args.nb)

    # Always run one baseline solve so users can immediately inspect M, K, and |X|.
    M, C, K = build_nondimensional_mck(
        nb=args.nb,
        kc=args.kc,
        h=args.h,
        delta_m=delta_m,
        delta_k=delta_k,
    )

    F_hat = traveling_wave_force(args.nb, amplitude=1.0)
    X = steady_state_response(M, C, K, omega=args.omega, F_hat=F_hat)

    np.set_printoptions(precision=4, suppress=True)
    print("M =")
    print(M)
    print("\nK =")
    print(K)
    print("\n|X| =")
    print(np.abs(X))

    # Optional workflow 1: tuned response chart(s).
    if args.make_chart:
        saved = generate_response_chart(
            nb=args.nb,
            h=args.h,
            kc_values=args.kc_list,
            omega_min=args.omega_min,
            omega_max=args.omega_max,
            num_points=args.num_points,
            output_path=Path(args.chart_output),
        )
        print(f"\nSaved response chart: {saved}")

    # Optional workflow 2: Monte Carlo response statistics.
    if args.make_statistics_chart:
        saved = generate_statistics_chart(
            nb=args.nb,
            h=args.h,
            kc_values=args.kc_list,
            mistune_magnitudes=args.mistune_magnitudes,
            omega_min=args.omega_min,
            omega_max=args.omega_max,
            num_points=args.num_points,
            num_samples=args.stats_samples,
            output_path=Path(args.stats_output),
            blade_index=args.stats_blade_index,
            seed=args.seed,
        )
        print(f"\nSaved statistics chart: {saved}")

    # Optional workflow 3: amplification-factor histograms.
    if args.make_af_histogram:
        saved, rows = generate_af_histograms(
            nb=args.nb,
            h=args.h,
            kc_values=args.kc_list,
            mistune_magnitudes=args.mistune_magnitudes,
            omega_min=args.omega_min,
            omega_max=args.omega_max,
            num_points=args.num_points,
            num_samples=args.stats_samples,
            output_path=Path(args.af_output),
            bins=args.af_bins,
            seed=args.seed,
        )
        print(f"\nSaved AF histogram chart: {saved}")
        print("AF summary (kc, M, mean, std, max):")
        for kc, magnitude, mean_af, std_af, max_af in rows:
            print(f"kc={kc:.3f}, M={magnitude:.3f}, mean={mean_af:.4f}, std={std_af:.4f}, max={max_af:.4f}")

    # Optional workflow 4: surrogate vs Monte Carlo comparison.
    if args.make_surrogate_comparison:
        saved, rows = generate_surrogate_comparison_chart(
            nb=args.nb,
            h=args.h,
            kc_values=args.kc_list,
            mistune_magnitudes=args.mistune_magnitudes,
            omega_min=args.omega_min,
            omega_max=args.omega_max,
            num_points=args.num_points,
            num_mc_samples=args.stats_samples,
            num_train_samples=args.surrogate_train_samples,
            num_surrogate_eval=args.surrogate_eval_samples,
            output_path=Path(args.surrogate_output),
            blade_index=args.stats_blade_index,
            seed=args.seed,
        )
        print(f"\nSaved surrogate comparison chart: {saved}")
        print("Surrogate error summary (kc, M, mean_rel_l2, std_rel_l2, mean_peak_rel_pct, std_peak_rel_pct):")
        for kc, magnitude, e_mean, e_std, peak_mean_pct, peak_std_pct in rows:
            print(
                f"kc={kc:.3f}, M={magnitude:.3f}, "
                f"mean_rel_l2={e_mean:.4f}, std_rel_l2={e_std:.4f}, "
                f"mean_peak_rel_pct={peak_mean_pct:.2f}, std_peak_rel_pct={peak_std_pct:.2f}"
            )


if __name__ == "__main__":
    main()
