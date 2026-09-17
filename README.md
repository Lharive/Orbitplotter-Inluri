# Orbitplotter-Inluri
Program to generate stable orbits for a star system with circumbinary orbits, based on certain input parameters and the use of a Monte Carlo Method, followed by certain checks on said generated orbits.

[More elaboration TBD]

Note that: I am new to GitHub and so a lot of the procedure, protocol, standards, meta, and so on are things I am unaware of. So this might look strange for quite some time. I will hopefully learn as I go.

# Phases:
* **Phase I:** Basic stellar dynamics between the two binary stars, as computed under the function `generate_system()`. `Status: Done`
* **Phase II:** Implement planetary orbits around the stellar binaries. `Status: Done`
* **Phase III-A:** Implement Simple System Visualization
* **Phase III-B:** Implement massification and/or visualization

**Note 1:** Phases III-A and III-B are not necessarily linear in implementation order (i.e. I -> II -> III-A -> III-B) and are essentially two separate paths that are neither mutually exclusive nor in any particular priority order.

**Note 2:** The excel and `.csv` output were implemented independently of the documented phases as a tangential change to make it easier to work with the generated data.


# Literature Used As Of Now:
### Moe & Di Stefano (2017): *"Mind Your Ps and Qs: The Interrelation between Period (P) and Mass-ratio (Q) Distributions of Binary Stars"* (ApJS, 230, 15)
- **Primary mass range** (`M1_MIN, M1_MAX = 0.8, 1.2`)
- **Broken power-law mass-ratio distribution**: two slopes (`GAMMA_SMALL`, `GAMMA_LARGE`) split at q = 0.3, plus an excess "twin" population for q > 0.95.
- **Twin fraction decay with period** (`F_twin`, `logP_twin`) and the derivation of `P_twin` from the twin/small/large population ratios.
- **Binary eccentricity ceiling vs. period** (`e_max = 1 - (P/2)^(-2/3)`).

### Raghavan et al. (2010): *"A Survey of Stellar Families: Multiplicity of Solar-Type Stars"* (ApJS, 190, 1)
- **Binary period distribution**: log-normal in log₁₀(P/days) with μ = 5.03, σ = 2.28 (`LOGP_MEAN, LOGP_STD = 5.0, 2.3`: rounded).
- **Tidal circularization boundary**: this paper reports solar-type binaries circularize below ~12 days

### Wu et al. (2024): *"Eccentricities of Close Stellar Binaries"* (ApJL, 982, L34)
- **Binary eccentricity model**: Rayleigh distribution, dN/de ∝ e·exp(−e²/2σ²) (`RAYLEIGH_STAR_SCALE = 0.3`).
- **Truncated "close-binary" period window** (`LOGP_MIN, LOGP_MAX = 0.2, 3.0`) where this Rayleigh model is asserted to hold.

### Holman & Wiegert (1999): *"Long-Term Stability of Planets in Binary Systems"* (AJ, 117, 621)
- **The `a_crit/a_bin` polynomial** in `get_ze_orbits()`: `1.60 + 5.10e − 2.22e² + 4.12μ − 4.27eμ − 5.09μ² + 4.61e²μ²`.

### Dietrich, Malhotra & Apai (2024): *"Statistical Distribution Function of Orbital Spacings in Planetary Systems"* (AJ, 167, 46)
- **Planet mass prior**: log-uniform in Earth masses (`MIN_MASS, MAX_MASS = 0.5, 50` — narrower than their full range of ⅓ M⊕ to 3 M_Jup).
- **Mutual Hill spacing Δ**, its eccentricity-dependent form, and the log-normal fit to Δ for their "Nominal Kepler Analog" set (`MU_LOGNORMAL_DELTA, SIGMA_LOGNORMAL_DELTA = 3.14, 0.76`) — used to solve for each successive planet's semi-major axis in `planetmaker()`.

### He et al. (2020): *"Architectures of Exoplanetary Systems III: Eccentricity and Mutual Inclination Distributions of AMD-stable Planetary Systems"* (AJ, 160, 276)
- **Planet eccentricity model**: small-σ Rayleigh distribution (`RAYLEIGH_PLANET_SCALE = 0.025`, bounded to `[0.01, 0.07]`), themselves referenced by _Dietrich, Malhotra & Apai (2024)_.

### Birn (1973), Gladman (1993), and Tremaine (2023): 
- Cited via _Dietrich, Malhotra & Apai (2024)_ as the classical celestial mechanics literature providing the analytical lower bound for 2-planet Hill stability Δ_min = 2√3 ≈ 3.46 (`MIN_DELTA_HILL`).

### Li, Holman, & Tao (2016): *"Uncovering Circumbinary Planetary Architectural Properties From Selection Biases"* (ApJ, 831, 96)
- **Planet inclination sampling** (`sample_fisher_inclination()`, `KAPPA = 500.0`): used for the first planet's tilt relative to the binary plane.
- **Mutual Hill radius formula** (their Eq. 26), adapted for the circumbinary/circumstellar case.

### Welsh et al. (2012): *"Recent Kepler Results On Circumbinary Planets "* (Proceedings of the International Astronomical Union 8(S293):125-132)
- **Pileup factor**: circumbinary planets' semi-major axes cluster at 1.09–1.46× the critical stability radius (`pileup_factor = np.random.uniform(1.09, 1.46)` in `exofirst()`).

### Non-scientific credit
- **Artifexian's *Worldsmith 7.01* Calculator**: the spreadsheet tool that inspired this project's original spreadsheet ancestor, *Lightmapper Inluri*. Not a scientific source; credited as design inspiration only.


# To - Do List For Now:

* Concretely Bound the Scope
* Continue writing about the limitations of the program
