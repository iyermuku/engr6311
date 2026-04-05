# ENGR 6311 Project Report
## Simplest Bladed-Disk Vibration Model

**Course:** ENGR 6311 - Vibrations in Machines and Structures  
**Topic:** Forced response of tuned and mistuned cyclic blade assemblies

## Executive Summary

This report develops the simplest discrete model for a bladed disk. Each blade is represented by a single degree of freedom with baseline mass `m0`, stiffness `k0`, and structural damping `h0`. Adjacent blades are coupled by a spring `c0`, and the assembly is excited by a traveling-wave force. The model is written in dimensional and nondimensional form, then converted to steady-state complex matrix form for both tuned and mistuned cases.

## Part I - Model Construction

### Physical Description and Assumptions

1. The disk contains `Nb` blades.
2. Blade `j` has one generalized displacement coordinate `uj(t)`.
3. Each blade is coupled to blades `j-1` and `j+1` by coupling stiffness `c0`.
4. Baseline tuned properties are identical across blades.
5. Mistuning is represented as random perturbations in each blade mass and stiffness.
6. Traveling-wave forcing is applied at blade tips.

Cyclic indexing is used throughout:

`u0 = uNb`, `uNb+1 = u1`.

### Dimensional Equations of Motion

Traveling-wave forcing:

`fj(t) = F0 cos(Omega t - 2 pi j / Nb)`

Mistuned physical properties:

`kj = k0 (1 + delta_kj)`,

`mj = m0 (1 + delta_mj)`.

Blade `j` equation:

`mj u_ddot_j + h0 u_dot_j + kj uj + c0 (2 uj - uj+1 - uj-1) = F0 cos(Omega t - 2 pi j / Nb)`.

### Nondimensional Equation (Required Form)

Define nondimensional displacement and time:

`xj(t) = uj(t) k0 / F0`,

`t = tau sqrt(k0/m0)`.

Define nondimensional parameters:

`h = h0 / sqrt(k0 m0)`,

`kc = c0 / k0`,

`omega_f = Omega / sqrt(k0/m0)`.

Then

`(1 + delta_mj) x_ddot_j + h x_dot_j + (1 + delta_kj) xj + kc (2xj - xj+1 - xj-1) = cos(omega_f t - 2 pi j/Nb),  j = 1, ..., Nb`  (1)

with periodic boundary conditions:

`x0 = xNb`, `xNb+1 = x1`.

## Part II - Steady-State Response Discussion (Tuned Assembly)

This section discusses the tuned response chart generated for:

1. `Nb = 6`
2. `h = 0.01`
3. `0.6 <= omega_f <= 1.5`
4. Weak coupling: `kc = 0.01`
5. Moderate coupling: `kc = 0.05`

The response metric is the maximum blade amplitude over the ring:

`A(omega_f) = max_j |X_j(omega_f)|`.

### Case A: Weak Coupling (`kc = 0.01`)

For weak coupling, the resonance peak appears close to the single-blade natural frequency (`omega_f` near 1). Because blades are only lightly tied together, the coupling contribution to effective stiffness is small, and the peak location remains close to the uncoupled value. The curve is sharply peaked because damping is low (`h = 0.01`).

### Case B: Moderate Coupling (`kc = 0.05`)

For moderate coupling, the peak shifts to a higher `omega_f`. This follows directly from the tuned stiffness matrix

`K_tuned = (1 + 2 kc) I - kc (P + P^T)`,

where increasing `kc` raises modal frequencies associated with the traveling-wave pattern. The peak remains narrow due to the same damping level, but its center frequency increases compared with the weak-coupling case.

### Comparative Interpretation

1. Increasing coupling (`kc`) increases effective collective stiffness, so resonance moves to higher frequency.
2. With fixed damping `h`, both cases show high-amplitude resonant amplification and narrow bandwidth.
3. The weak-coupling case is more blade-local in behavior, while moderate coupling enforces stronger interblade coordination.
4. Even in this simplest tuned model, coupling level is a key design lever for resonance placement and dynamic margins.

Overall, the chart confirms expected cyclic-system behavior: stronger interblade coupling shifts the forced-response peak upward in nondimensional frequency.

### Numerical Peak Summary from the Sweep

The following approximate peak values are extracted from the same sweep used for the chart (`Nb=6`, `h=0.01`, `0.6 <= omega_f <= 1.5`, 700 points):

| Coupling case | `kc` | Approx. peak frequency `omega_f,peak` | Approx. peak amplitude `max_j |X_j|` |
|---|---:|---:|---:|
| Weak coupling | 0.01 | 1.0056 | 98.756 |
| Moderate coupling | 0.05 | 1.0249 | 97.495 |

## Part III - Mistuned Assembly Response

Now consider mistuning only in the blade elastic properties, with

`delta_mj = 0`

and

`delta_kj = M rj`,

where `M = 0.01` and

`rj = {0.91, -0.03, 0.60, -0.72, -0.16, 0.83}`.

For this case, the known mistuning vector is

`delta_k = {0.0091, -0.0003, 0.0060, -0.0072, -0.0016, 0.0083}`.

The mistuned steady-state response is obtained from the same complex matrix equation used in Part II,

`Z_mist(omega_f) X_mist = F_hat`,

with

`Z_mist = -omega_f^2 M_mist + i omega_f C_mist + K_mist`.

Using the same sweep range and forcing pattern as Part II, the mistuned response produces larger peak amplitudes than the tuned assembly. The response remains resonant near the same frequency band, but the amplitude envelope changes because the cyclic symmetry is broken.

### Numerical Peak Summary for the Mistuned Assembly

| Coupling case | `kc` | Approx. peak frequency `omega_f,peak` | Approx. peak amplitude `max_j |X_j|` | Increase vs tuned |
|---|---:|---:|---:|---:|
| Weak coupling | 0.01 | 1.0056 | 116.271 | 17.7% |
| Moderate coupling | 0.05 | 1.0249 | 112.199 | 15.1% |

### Discussion of Tuned vs Mistuned Response

1. The mistuned assembly exhibits higher response amplitudes than the tuned assembly for both coupling values.
2. The weak-coupling case is the most sensitive to mistuning because the blades are less constrained by neighboring motion, so local stiffness variations have a stronger effect.
3. The moderate-coupling case is still affected, but the stronger interblade interaction spreads the response more evenly around the ring.
4. At resonance, the mistuned response becomes nonuniform across the blades, which is consistent with modal localization.
5. In the sample mistuned case, the largest response shifts to blade 5 for `kc = 0.01` and blade 2 for `kc = 0.05`, showing that mistuning can move the hot spot from blade to blade.

This behavior is important in practice because a small stiffness scatter can create a large increase in the maximum blade amplitude, even when the forcing frequency and overall system parameters are unchanged.

## Part III(b) - Statistical Response of Mistuned Assemblies

To obtain statistical information about the mistuned response, the single-assembly calculation from Part III(a) was repeated for 100 different mistuned assemblies at each mistuning magnitude. The stiffness mistuning was modeled as

`delta_kj = M rj`,

with `delta_mj = 0`, where `M = 0.01` and `M = 0.05` were used for the two cases. For each assembly, the blade stiffness perturbations were sampled randomly, and the blade-1 response amplitude was computed over the same frequency sweep as in Part II.

The reported statistics are:

`A_bar_j(omega_f) = mean(|X_j(omega_f)|)`

and the one-sigma spread

`sigma_j(omega_f) = std(|X_j(omega_f)|)`.

The tuned response is shown on the same figure for direct comparison. The resulting statistics chart is saved as `Project/figures/mistuning_statistics_nb6.png`.

### Interpretation of the Statistics Figure

1. The mean response of the selected blade stays close to the tuned curve for weak mistuning, but it drops below the tuned peak as mistuning increases.
2. The standard deviation grows significantly at larger mistuning magnitudes, showing that the response becomes much less predictable from blade to blade.
3. The response peak remains near the same frequency band, but the average peak is broadened and reduced because energy is redistributed across the ring.
4. The spread is larger for `M = 5%` than for `M = 1%`, which is the expected trend for stronger stiffness scatter.

### Numerical Summary for Part III(b)

The table below lists the approximate peak of the mean blade response, the standard deviation at that peak, and the tuned response at the same frequency. These values come from the 100-sample Monte Carlo sweep over `0.6 <= omega_f <= 1.5`.

| Mistuning magnitude | `kc` | `omega_f,peak` | Mean blade amplitude `A_bar_j` | Std. dev. `sigma_j` | Tuned amplitude at same frequency |
|---|---:|---:|---:|---:|---:|
| 1% | 0.01 | 1.0043 | 88.391 | 18.053 | 98.622 |
| 1% | 0.05 | 1.0249 | 89.863 | 18.555 | 97.495 |
| 5% | 0.01 | 1.0056 | 40.498 | 27.045 | 98.756 |
| 5% | 0.05 | 1.0236 | 54.307 | 27.201 | 95.450 |

The main conclusion is that stronger mistuning reduces the average resonance level of a particular blade but increases the uncertainty in the response. That is a signature of localization: the response is no longer shared evenly around the disk, and individual blades can behave very differently even under the same excitation.

## Part III(c) - Amplification Factor (AF)

For a given forcing level, define the amplification factor (AF) as

`AF = max_{j, omega_f} |X_j^mist(omega_f)| / max_{j, omega_f} |X_j^tuned(omega_f)|`.

By this definition:

1. `AF > 1` means the mistuned assembly has a higher worst-case response than the tuned assembly.
2. `AF = 1` means no change in the worst-case maximum response.
3. `AF < 1` means the mistuned assembly reduces the worst-case maximum response.

### AF for the Part III(a) Mistuned Assembly

Using `delta_k = {0.0091, -0.0003, 0.0060, -0.0072, -0.0016, 0.0083}`, `delta_m = 0`, and the same sweep (`0.6 <= omega_f <= 1.5`):

| Coupling case | `kc` | AF |
|---|---:|---:|
| Weak coupling | 0.01 | 1.177 |
| Moderate coupling | 0.05 | 1.151 |

Both values are greater than 1, so this specific mistuning increases the worst-case response in both coupling regimes.

#### Quick Report Table: Part III(a) AF Percent Increase

`AF percent increase = (AF - 1) x 100%`

| Coupling case | `kc` | AF | AF percent increase |
|---|---:|---:|---:|
| Weak coupling | 0.01 | 1.177 | 17.7% |
| Moderate coupling | 0.05 | 1.151 | 15.1% |

### AF Histograms for the Part III(b) Mistuned Sets

AF was computed for all Monte Carlo mistuned assemblies from Part III(b) (`100` assemblies per case, `M=1%` and `M=5%`, with `kc=0.01` and `kc=0.05`). The histogram figure is saved as `Project/figures/af_histograms_nb6.png`.

| Mistuning magnitude | `kc` | Mean AF | Std. dev. | Max AF (sample) |
|---|---:|---:|---:|---:|
| 1% | 0.01 | 1.216 | 0.067 | 1.362 |
| 1% | 0.05 | 1.162 | 0.045 | 1.242 |
| 5% | 0.01 | 1.211 | 0.084 | 1.427 |
| 5% | 0.05 | 1.184 | 0.098 | 1.510 |

#### Quick Report Table: Monte Carlo AF Percent Increase

`Mean AF percent increase = (Mean AF - 1) x 100%`

| Mistuning magnitude | `kc` | Mean AF | Mean AF percent increase |
|---|---:|---:|---:|
| 1% | 0.01 | 1.216 | 21.6% |
| 1% | 0.05 | 1.162 | 16.2% |
| 5% | 0.01 | 1.211 | 21.1% |
| 5% | 0.05 | 1.184 | 18.4% |

Headline metric: the worst observed amplification in this study is a 51.0% increase (`AF_max = 1.510`) at `M = 5%` and `kc = 0.05`.

### Discussion

1. All AF distributions are centered above 1, indicating that mistuning generally increases the worst-case maximum response for this setup.
2. The spread of AF increases at higher mistuning (`M=5%`), especially for `kc=0.05`, where the largest observed AF is about `1.51`.
3. Even when average blade response may decrease (Part III(b)), the global worst-case response can still increase, which is exactly what AF is designed to quantify.
4. AF therefore provides a conservative risk metric for high-cycle fatigue screening in mistuned bladed disks.

## Steady-State Formulation in Complex Form

Write the response and forcing as real parts of complex harmonics:

`x(t) = Re{X exp(i omega_f t)}`,

`f(t) = Re{F_hat exp(i omega_f t)}`,

with forcing vector entries

`F_hat_j = exp(-i 2 pi j / Nb)`.

Substituting into Eq. (1) gives the algebraic steady-state system:

`Z(omega_f) X = F_hat`,

where

`Z(omega_f) = -omega_f^2 M + i omega_f C + K`.

### Tuned Case (Matrix Notation)

For `delta_mj = 0`, `delta_kj = 0` for all blades:

`M_tuned = I`,

`C_tuned = h I`,

`K_tuned = (1 + 2 kc) I - kc (P + P^T)`.

`P` is the cyclic forward-shift permutation matrix. Equivalently, `K_tuned` is circulant with main diagonal `1 + 2 kc`, first off-diagonals `-kc`, and wrap-around corner terms `-kc`.

Steady-state solution:

`X_tuned = Z_tuned(omega_f)^(-1) F_hat`,

`Z_tuned = -omega_f^2 M_tuned + i omega_f C_tuned + K_tuned`.

### Mistuned Case (Matrix Notation)

For random perturbations `delta_mj`, `delta_kj`:

`M_mist = diag(1 + delta_m1, ..., 1 + delta_mNb)`,

`C_mist = h I`,

`K_mist = K_tuned + diag(delta_k1, ..., delta_kNb)`.

Steady-state solution:

`X_mist = Z_mist(omega_f)^(-1) F_hat`,

`Z_mist = -omega_f^2 M_mist + i omega_f C_mist + K_mist`.

Because cyclic symmetry is broken in `M_mist` and `K_mist`, modal families are no longer perfectly decoupled and response localization can occur.

## Relevance to Real Bladed Disks

This model is important because it reproduces the essential forced-response behavior of real rotors while staying analytically and computationally simple. The tuned case captures nodal-diameter response under traveling-wave excitation, while the mistuned case explains blade-to-blade amplitude scatter and localization, both of which are directly related to high-cycle fatigue risk and durability margins in turbomachinery design.

## Part IV - Summary of Findings

This study shows that mistuning has a strong and practical influence on the vibration behavior of bladed disks, even in a simple one-DOF-per-blade model.

1. In the tuned assembly, the forced response is highly structured by cyclic symmetry, with resonance peaks that shift predictably as coupling `kc` changes.
2. Introducing mistuning in stiffness (`delta_kj`) breaks cyclic symmetry and makes the blade responses nonuniform, producing localization and blade-to-blade amplitude scatter.
3. For the specific mistuned set in Part III(a), the worst-case response increases relative to tuned (`AF > 1` for both coupling values), confirming that small property deviations can amplify critical vibration levels.
4. The Monte Carlo results in Part III(b) and Part III(c) show that uncertainty grows with mistuning magnitude: higher `M` leads to broader response spread and wider AF distributions.
5. A key engineering result is that average response trends alone can be misleading: even when mean response decreases for a selected blade, the global maximum response can still increase, which is captured by the AF metric.
6. From a design and reliability perspective, mistuning should be treated as a risk driver for high-cycle fatigue, and robust assessment should combine deterministic response curves with statistical measures (mean, standard deviation, and AF histograms).

Overall, the project confirms that mistuning is not only a small perturbation effect; it can materially alter resonance severity, redistribute vibration energy among blades, and increase worst-case dynamic loading.

## Part V - Alternatives to Direct Monte Carlo for Mistuning Statistics

The Part III statistical study used repeated deterministic solves over many mistuned realizations and frequencies. While this is feasible for the present low-order model, it becomes expensive for high-fidelity finite-element bladed-disk models with many degrees of freedom and multiple forcing conditions. Several alternatives are commonly used to reduce computational cost.

1. Reduced-order models (ROMs): Build a low-dimensional basis from selected full-order modes and solve mistuned response in reduced coordinates. Examples include component mode synthesis and modal substructuring approaches.
2. Subset-based mistuning methods: Represent mistuning using a small set of physically meaningful parameters and map them to response metrics. This reduces the random space dimension before uncertainty propagation.
3. Surrogate modeling: Train response surfaces (for example polynomial chaos, Gaussian process models, or neural-network surrogates) from a limited set of high-fidelity samples, then evaluate statistics cheaply.
4. Sparse sampling and smart design of experiments: Replace brute-force random sampling with Latin hypercube, sparse grids, or adaptive sampling near resonance regions where response sensitivity is highest.
5. Stochastic perturbation methods: For small mistuning levels, compute moments of response from first- or second-order expansions around the tuned solution instead of repeated full solves.
6. Multi-fidelity workflows: Combine many cheap low-fidelity evaluations with a small number of expensive high-fidelity solves for correction or calibration.
7. Parallel and GPU-accelerated solvers: Keep the Monte Carlo framework but distribute realizations and frequency points across cores, nodes, or accelerators.

In practice, robust industrial workflows often combine these ideas: reduced-order modeling to cut per-solve cost, adaptive sampling to cut the number of solves, and limited high-fidelity validation to preserve accuracy in critical operating ranges.

### Part V(b) Surrogate Approximation of Mistuning Statistics

A simple polynomial surrogate was used as a practical low-cost alternative to direct Monte Carlo for the Part III(b) statistics.

For each frequency, the blade-1 response amplitude was approximated as:

`|X_j| ~ b0 + sum_i bi delta_ki + sum_i ci delta_ki^2`.

Workflow used in this project:

1. Train the surrogate with `30` full-model mistuned samples per case.
2. Evaluate the surrogate with `3000` random mistuning samples.
3. Compare surrogate mean/std curves against direct Monte Carlo (`100` full-model samples).

Comparison figure: `Project/figures/surrogate_vs_mc_nb6.png`.

#### Surrogate Error vs Direct Monte Carlo

| Mistuning magnitude | `kc` | Mean-curve rel. L2 error | Std-curve rel. L2 error | Peak mean pointwise error | Peak std pointwise error |
|---|---:|---:|---:|---:|---:|
| 1% | 0.01 | 2.44% | 5.88% | 4.62% | 11.32% |
| 1% | 0.05 | 1.67% | 6.10% | 5.25% | 16.02% |
| 5% | 0.01 | 4.42% | 10.17% | 11.43% | 22.85% |
| 5% | 0.05 | 13.70% | 13.90% | 23.72% | 28.57% |

The surrogate is very accurate for mild mistuning (`M=1%`) and still useful at `M=5%`, though error increases for the strongest case (`kc=0.05`, `M=5%`).

Recommended usage: use the surrogate model for fast screening and uncertainty sweeps, then validate only the highest-risk operating points with direct Monte Carlo or full-order simulations.

## Python Model

A Python implementation that builds tuned and mistuned mass and stiffness matrices is provided in `Project/blade_model.py`.

Run it from the repository root:

```powershell
c:/Users/mukun/Documents/engr6311/engr6311/.venv/Scripts/python.exe Project/blade_model.py --nb 6 --h 0.01 --kc 0.01
```

Generate the two-case tuned response chart used in Part II:

```powershell
c:/Users/mukun/Documents/engr6311/engr6311/.venv/Scripts/python.exe Project/blade_model.py --nb 6 --h 0.01 --kc 0.01 --make-chart --kc-list 0.01 0.05 --omega-min 0.6 --omega-max 1.5 --num-points 700 --chart-output Project/figures/response_nb6_h001_kc001_005.png
```

Generate the mistuned response at the specified blade deviations:

```powershell
c:/Users/mukun/Documents/engr6311/engr6311/.venv/Scripts/python.exe Project/blade_model.py --nb 6 --h 0.01 --kc 0.01 --delta-m 0 0 0 0 0 0 --delta-k 0.0091 -0.0003 0.0060 -0.0072 -0.0016 0.0083 --make-chart --kc-list 0.01 0.05 --omega-min 0.6 --omega-max 1.5 --num-points 700 --chart-output Project/figures/mistuned_response_nb6.png
```

Generate the Part III(b) statistics chart:

```powershell
c:/Users/mukun/Documents/engr6311/engr6311/.venv/Scripts/python.exe Project/blade_model.py --nb 6 --h 0.01 --kc 0.01 --make-statistics-chart --kc-list 0.01 0.05 --mistune-magnitudes 0.01 0.05 --omega-min 0.6 --omega-max 1.5 --num-points 700 --stats-samples 100 --stats-output Project/figures/mistuning_statistics_nb6.png
```

Generate the surrogate-vs-Monte-Carlo comparison:

```powershell
c:/Users/mukun/Documents/engr6311/engr6311/.venv/Scripts/python.exe Project/blade_model.py --nb 6 --h 0.01 --kc 0.01 --make-surrogate-comparison --kc-list 0.01 0.05 --mistune-magnitudes 0.01 0.05 --omega-min 0.6 --omega-max 1.5 --num-points 700 --stats-samples 100 --surrogate-train-samples 30 --surrogate-eval-samples 3000 --surrogate-output Project/figures/surrogate_vs_mc_nb6.png
```

Generate the Part III(c) AF histograms:

```powershell
c:/Users/mukun/Documents/engr6311/engr6311/.venv/Scripts/python.exe Project/blade_model.py --nb 6 --h 0.01 --kc 0.01 --make-af-histogram --kc-list 0.01 0.05 --mistune-magnitudes 0.01 0.05 --omega-min 0.6 --omega-max 1.5 --num-points 700 --stats-samples 100 --af-bins 20 --af-output Project/figures/af_histograms_nb6.png
```