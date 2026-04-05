# ENGR 6311 Project Report
## Forced Response of Tuned and Mistuned Bladed Disks

**Course:** ENGR 6311 - Vibrations in Machines and Structures  
**Student:** Mukund Rajamony  
**Institution:** Concordia University  
**Date:** April 2026

---

## Executive Summary

This report develops and studies a cyclic bladed-disk model. Each blade is represented by one degree of freedom, neighboring blades are coupled by elastic links, and the system is excited by a traveling-wave forcing pattern. The report compares tuned and mistuned assemblies, quantifies statistical behavior under random mistuning, evaluates amplification-factor distributions, and introduces a simple surrogate model to reduce computational effort.

Main findings:

1. Increasing coupling stiffness shifts tuned resonance to higher nondimensional frequency.
2. Mistuning breaks cyclic symmetry and causes nonuniform blade response and localization.
3. The worst-case response in mistuned systems is consistently larger than in tuned systems for the tested cases.
4. Amplification-factor histograms show non-negligible probability of severe response amplification.
5. A quadratic surrogate model reproduces Monte Carlo trends well for mild mistuning and remains useful for moderate mistuning.

---

## Nomenclature

| Symbol | Scientific definition | Units / study values |
|---|---|---|
| $N_b$ | Number of blades | $6.0\times10^{0}$ |
| $u_j(t)$ | Physical generalized displacement of blade $j$ | m |
| $x_j(t)$ | Nondimensional generalized displacement of blade $j$ | -- |
| $m_0, k_0, h_0$ | Baseline blade mass, stiffness, and damping constants | model constants |
| $c_0$ | Interblade coupling stiffness | model constant |
| $\delta m_j$ | Mass mistuning of blade $j$ | -- |
| $\delta k_j$ | Stiffness mistuning of blade $j$ | -- |
| $F_0, \Omega$ | Forcing amplitude and forcing frequency | forcing inputs |
| $h$ | $h=\dfrac{h_0}{\sqrt{k_0m_0}}$ | $1.0\times10^{-2}$ |
| $k_c$ | $k_c=\dfrac{c_0}{k_0}$ | $1.0\times10^{-2},\;5.0\times10^{-2}$ |
| $\omega_f$ | $\omega_f=\dfrac{\Omega}{\sqrt{k_0/m_0}}$ | sweep: $6.0\times10^{-1}$ to $1.5\times10^{0}$ |
| $M$ | Mistuning magnitude in $\delta k_j=Mr_j$ | $1.0\times10^{-2},\;5.0\times10^{-2}$ |
| $N_{MC}$ | Monte Carlo assemblies per case | $1.0\times10^{2}$ |

---

## Part I. Model Formulation

### 1. Traveling-Wave Forcing and Mistuning

The traveling-wave force on blade $j$ is

$$
f_j(t) = F_0 \cos\left(\Omega t - \frac{2\pi j}{N_b}\right).
$$

Mistuned blade properties are

$$
m_j = m_0(1+\delta m_j), \qquad k_j = k_0(1+\delta k_j).
$$

The dimensional blade equation is

$$
m_j\ddot{u}_j + h_0\dot{u}_j + k_j u_j + c_0(2u_j-u_{j+1}-u_{j-1}) = F_0 \cos\left(\Omega t - \frac{2\pi j}{N_b}\right).
$$

Cyclic boundary conditions:

$$
u_0=u_{N_b}, \qquad u_{N_b+1}=u_1.
$$

### 2. Nondimensional Form

Define

$$
x_j = \frac{k_0}{F_0}u_j, \qquad t = \tau\sqrt{\frac{k_0}{m_0}}, \qquad h = \frac{h_0}{\sqrt{k_0m_0}}, \qquad k_c=\frac{c_0}{k_0}, \qquad \omega_f=\frac{\Omega}{\sqrt{k_0/m_0}}.
$$

The nondimensional governing equation is

$$
(1+\delta m_j)\ddot{x}_j + h\dot{x}_j + (1+\delta k_j)x_j + k_c(2x_j-x_{j+1}-x_{j-1}) = \cos\left(\omega_f t - \frac{2\pi j}{N_b}\right), \quad j=1,\dots,N_b.
\tag{1}
$$

### 3. Complex Steady-State Form

Assume

$$
\mathbf{x}(t)=\Re\{\mathbf{X}e^{i\omega_f t}\}, \qquad \mathbf{f}(t)=\Re\{\hat{\mathbf{F}}e^{i\omega_f t}\},
$$

with

$$
\hat{F}_j=e^{-i2\pi j/N_b}.
$$

Then

$$
\mathbf{Z}(\omega_f)\mathbf{X}=\hat{\mathbf{F}}, \qquad \mathbf{Z}(\omega_f)=-\omega_f^2\mathbf{M}+i\omega_f\mathbf{C}+\mathbf{K}.
$$

Tuned case:

$$
\mathbf{M}=\mathbf{I}, \qquad \mathbf{C}=h\mathbf{I}, \qquad
\mathbf{K}_{\text{tuned}}=(1+2k_c)\mathbf{I}-k_c(\mathbf{P}+\mathbf{P}^T).
$$

Mistuned case:

$$
\mathbf{M}_{\text{mist}}=\mathrm{diag}(1+\delta m_1,\dots,1+\delta m_{N_b}),
$$
$$
\mathbf{C}_{\text{mist}}=h\mathbf{I},
$$
$$
\mathbf{K}_{\text{mist}}=\mathbf{K}_{\text{tuned}}+\mathrm{diag}(\delta k_1,\dots,\delta k_{N_b}).
$$

---

## Part II. Tuned Assembly Response

Study conditions:

- $N_b=6$
- $h=1.0\times10^{-2}$
- $6.0\times10^{-1} \le \omega_f \le 1.5\times10^{0}$
- weak coupling: $k_c=1.0\times10^{-2}$
- moderate coupling: $k_c=5.0\times10^{-2}$

Response metric:

$$
A(\omega_f)=\max_j |X_j(\omega_f)|.
$$

![Tuned frequency response (N_b=6.0x10^0, h=1.0x10^-2)](figures/response_nb6_h001_kc001_005.png)

**Figure 1.** Tuned response for weak and moderate coupling.

### Numerical Peak Summary (Tuned)

| Coupling case | $k_c$ | $\omega_{f,\text{peak}}$ | $\max_j|X_j|$ |
|---|---:|---:|---:|
| Weak coupling | $1.0\times10^{-2}$ | $1.0056\times10^{0}$ | $9.8756\times10^{1}$ |
| Moderate coupling | $5.0\times10^{-2}$ | $1.0249\times10^{0}$ | $9.7495\times10^{1}$ |

Interpretation: increasing coupling shifts resonance toward higher frequency while maintaining a narrow resonant peak due to low damping.

---

## Part III. Mistuned Assembly Studies

### Part III(a). Deterministic Mistuned Case

Given

$$
\delta m_j=0, \qquad \delta k_j = Mr_j,
$$

with

$$
M=1.0\times10^{-2}, \qquad r_j=\{9.1\times10^{-1},-3.0\times10^{-2},6.0\times10^{-1},-7.2\times10^{-1},-1.6\times10^{-1},8.3\times10^{-1}\},
$$

so

$$
\delta k=\{0.0091,-0.0003,0.0060,-0.0072,-0.0016,0.0083\}.
$$

![Mistuned response for prescribed deterministic case](figures/mistuned_response_nb6.png)

**Figure 2.** Mistuned deterministic response for both coupling values.

| Coupling case | $k_c$ | $\omega_{f,\text{peak}}$ | $\max_j|X_j|$ | Increase vs tuned |
|---|---:|---:|---:|---:|
| Weak coupling | $1.0\times10^{-2}$ | $1.0056\times10^{0}$ | $1.16271\times10^{2}$ | $1.77\times10^{1}\%$ |
| Moderate coupling | $5.0\times10^{-2}$ | $1.0249\times10^{0}$ | $1.12199\times10^{2}$ | $1.51\times10^{1}\%$ |

### Part III(b). Monte Carlo Statistics

For each case, $N_{MC}=1.0\times10^{2}$ random mistuned assemblies were simulated for $M=1.0\times10^{-2}$ and $M=5.0\times10^{-2}$. For blade $j$:

$$
\bar{A}_j(\omega_f)=\mathbb{E}[|X_j(\omega_f)|], \qquad \sigma_j(\omega_f)=\sqrt{\mathbb{V}[|X_j(\omega_f)|]}.
$$

![Monte Carlo mean and standard deviation versus tuned response](figures/mistuning_statistics_nb6.png)

**Figure 3.** Monte Carlo statistics for blade 1 (mean and $\pm1\sigma$).

| Mistuning magnitude | $k_c$ | $\omega_{f,\text{peak}}$ | $\bar{A}_j$ at peak | $\sigma_j$ at peak | Tuned amplitude at same frequency |
|---|---:|---:|---:|---:|---:|
| $1.0\times10^{-2}$ | $1.0\times10^{-2}$ | $1.0043\times10^{0}$ | $8.8391\times10^{1}$ | $1.8053\times10^{1}$ | $9.8622\times10^{1}$ |
| $1.0\times10^{-2}$ | $5.0\times10^{-2}$ | $1.0249\times10^{0}$ | $8.9863\times10^{1}$ | $1.8555\times10^{1}$ | $9.7495\times10^{1}$ |
| $5.0\times10^{-2}$ | $1.0\times10^{-2}$ | $1.0056\times10^{0}$ | $4.0498\times10^{1}$ | $2.7045\times10^{1}$ | $9.8756\times10^{1}$ |
| $5.0\times10^{-2}$ | $5.0\times10^{-2}$ | $1.0236\times10^{0}$ | $5.4307\times10^{1}$ | $2.7201\times10^{1}$ | $9.5450\times10^{1}$ |

### Part III(c). Amplification Factor

Define amplification factor

$$
AF = \frac{\max_{j,\omega_f}|X_j^{\text{mist}}(\omega_f)|}{\max_{j,\omega_f}|X_j^{\text{tuned}}(\omega_f)|}.
$$

#### Part III(a) AF values

| Coupling case | $k_c$ | AF | AF percent increase |
|---|---:|---:|---:|
| Weak coupling | $1.0\times10^{-2}$ | $1.177\times10^{0}$ | $1.77\times10^{1}\%$ |
| Moderate coupling | $5.0\times10^{-2}$ | $1.151\times10^{0}$ | $1.51\times10^{1}\%$ |

#### AF histograms for Part III(b) random sets

![Amplification-factor histograms](figures/af_histograms_nb6.png)

**Figure 4.** AF distributions for $M=1\%$ and $M=5\%$ under both coupling values.

| Mistuning magnitude | $k_c$ | Mean AF | Std. dev. | Max AF (sample) | Mean AF percent increase |
|---|---:|---:|---:|---:|---:|
| $1.0\times10^{-2}$ | $1.0\times10^{-2}$ | $1.216\times10^{0}$ | $6.7\times10^{-2}$ | $1.362\times10^{0}$ | $2.16\times10^{1}\%$ |
| $1.0\times10^{-2}$ | $5.0\times10^{-2}$ | $1.162\times10^{0}$ | $4.5\times10^{-2}$ | $1.242\times10^{0}$ | $1.62\times10^{1}\%$ |
| $5.0\times10^{-2}$ | $1.0\times10^{-2}$ | $1.211\times10^{0}$ | $8.4\times10^{-2}$ | $1.427\times10^{0}$ | $2.11\times10^{1}\%$ |
| $5.0\times10^{-2}$ | $5.0\times10^{-2}$ | $1.184\times10^{0}$ | $9.8\times10^{-2}$ | $1.510\times10^{0}$ | $1.84\times10^{1}\%$ |

**Headline metric:** the worst observed amplification in this study is a $5.10\times10^{1}\%$ increase ($AF_{\max}=1.510\times10^{0}$) at $M=5.0\times10^{-2}$ and $k_c=5.0\times10^{-2}$.

---

## Part IV. Summary of Findings

1. Tuned resonance behavior is structured by cyclic symmetry and coupling strength.
2. Mistuning breaks symmetry, creates blade-to-blade variability, and can localize response.
3. For the deterministic mistuned set, worst-case response increases in both coupling cases.
4. Statistical variability increases with mistuning magnitude, and response uncertainty becomes significant.
5. Global worst-case amplification can increase even when average single-blade response decreases.
6. Amplification factor is a conservative and practical risk metric for vibration durability screening.

---

## Part V. Efficient Alternatives to Direct Monte Carlo

Direct Monte Carlo can be expensive for high-fidelity bladed-disk models. Practical alternatives include reduced-order models, adaptive sampling, and surrogate models.

The Part III statistical study used repeated deterministic solves over many mistuned realizations and frequencies. While this is feasible for the present low-order model, it becomes expensive for high-fidelity finite-element bladed-disk models with many degrees of freedom and multiple forcing conditions. Several alternatives are commonly used to reduce computational cost.

1. Reduced-order models (ROMs): Build a low-dimensional basis from selected full-order modes and solve mistuned response in reduced coordinates.
2. Subset-based mistuning methods: Represent mistuning using a small set of physically meaningful parameters and map them to response metrics.
3. Surrogate modeling: Train response surfaces (for example polynomial chaos, Gaussian process models, or neural-network surrogates) from a limited set of high-fidelity samples.
4. Sparse sampling and design of experiments: Replace brute-force random sampling with Latin hypercube, sparse grids, or adaptive sampling near resonance regions.
5. Stochastic perturbation methods: For small mistuning levels, compute response moments from low-order expansions around the tuned solution.
6. Multi-fidelity workflows: Combine many cheap low-fidelity evaluations with a smaller number of expensive high-fidelity solves for correction or calibration.
7. Parallel and GPU-accelerated solvers: Keep the Monte Carlo framework but distribute realizations and frequency points across cores, nodes, or accelerators.

In practice, robust industrial workflows often combine these ideas: reduced-order modeling to cut per-solve cost, adaptive sampling to cut the number of solves, and limited high-fidelity validation to preserve accuracy in critical operating ranges.

### Part V(b). Surrogate Approximation of Mistuning Statistics

A simple polynomial surrogate was used to approximate blade response statistics at each frequency:

$$
|X_j| \approx b_0 + \sum_i b_i\delta k_i + \sum_i c_i\delta k_i^2.
$$

Procedure:

1. Train on $3.0\times10^{1}$ full-model samples per case.
2. Evaluate on $3.0\times10^{3}$ surrogate samples.
3. Compare against $1.0\times10^{2}$-sample direct Monte Carlo.

![Surrogate versus Monte Carlo comparison](figures/surrogate_vs_mc_nb6.png)

**Figure 5.** Surrogate and direct Monte Carlo mean/$\pm1\sigma$ comparison for blade 1.

| Mistuning magnitude | $k_c$ | Mean-curve relative $L_2$ error | Std-curve relative $L_2$ error | Peak mean pointwise error | Peak std pointwise error |
|---|---:|---:|---:|---:|---:|
| $1.0\times10^{-2}$ | $1.0\times10^{-2}$ | $2.44\times10^{0}\%$ | $5.88\times10^{0}\%$ | $4.62\times10^{0}\%$ | $1.132\times10^{1}\%$ |
| $1.0\times10^{-2}$ | $5.0\times10^{-2}$ | $1.67\times10^{0}\%$ | $6.10\times10^{0}\%$ | $5.25\times10^{0}\%$ | $1.602\times10^{1}\%$ |
| $5.0\times10^{-2}$ | $1.0\times10^{-2}$ | $4.42\times10^{0}\%$ | $1.017\times10^{1}\%$ | $1.143\times10^{1}\%$ | $2.285\times10^{1}\%$ |
| $5.0\times10^{-2}$ | $5.0\times10^{-2}$ | $1.370\times10^{1}\%$ | $1.390\times10^{1}\%$ | $2.372\times10^{1}\%$ | $2.857\times10^{1}\%$ |

Recommended usage: use the surrogate model for fast screening and uncertainty sweeps, then validate only the highest-risk operating points with direct Monte Carlo or full-order simulations.

---

## Reproducibility Notes

All computations and figures in this report were generated from:

- GitHub project code: https://github.com/iyermuku/engr6311/tree/main/Project

- `Project/blade_model.py`
- `Project/figures/response_nb6_h001_kc001_005.png`
- `Project/figures/mistuned_response_nb6.png`
- `Project/figures/mistuning_statistics_nb6.png`
- `Project/figures/af_histograms_nb6.png`
- `Project/figures/surrogate_vs_mc_nb6.png`
