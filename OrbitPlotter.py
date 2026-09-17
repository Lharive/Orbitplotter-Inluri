# Special Thanks to Artifexian, who's Worldsmith 7.01 Calculator was the chief reference for my own spreadsheet, Lightmapper Inluri
# Worldsmith 7.01 was still a spreadsheet that fundamentally dealt with single-star systems, so it was unable to meet my needs. 
# Lightmapper Inluri started as my attempt to use  it (and my own limited ability) to extend it into binary systems, although it grew into something larger.
# OrbitPlotter Inluri is the Python translation of the Lightmapper Inluri spreadsheet but has a different scope.
# This is v2 of OrbitPlotter Inluri, because the previous one was kind of a mess to read through. I had initially paused work on it to read up on the literature but when I returned to it, I found it an eyesore. 
# Project scope has not changed

import numpy as np 
import pandas as pd
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

############################ CONSTANTS AND PARAMETERS: THE COMPENDIUM ####################################

EARTH_YEAR_DAYS = 365.2525
M1_MIN, M1_MAX = 0.8, 1.2                # valid primary-mass range, Moe & Di Stefano (2017)
LOGP_MEAN, LOGP_STD = 5.0, 2.3           # Raghavan et al. (2010) solar-type period distribution
LOGP_MIN, LOGP_MAX = 0.2, 3.0            # close-binary regime where Rayleigh e-model is valid, Wu et al. (2024)
LOGP_CIRCULAR = 1.0                      # below this, tidal circularization : e = 0
GAMMA_SMALL, GAMMA_LARGE = 0.3, -0.5     # Moe & Di Stefano (2017) Eq. 13, Eq. 9
Q_SMALL_LO, Q_SMALL_HI = 0.1, 0.3
Q_LARGE_LO, Q_LARGE_HI = 0.3, 1.0
Q_TWIN_LO, Q_TWIN_HI = 0.95, 1.0
RAYLEIGH_STAR_SCALE = 0.3
M_EARTH_TO_MSUN = 3.0037e-6
MIN_MASS, MAX_MASS = 0.5, 50 # in M_earth, also note that Dietrich et. al. (2024) actually had their masses randomly chosen for each planet with a uniform prior in log mass between one-third Earth mass and 3 Jupiter masses. This one is far narrower.
KAPPA = 500.0 # Concentration parameter for p=3 von Mises-Fisher distribution , from Li et al. (2018) 
PLANET_MIN_ECCENTRICITY, PLANET_MAX_ECCENTRICITY = 0.01, 0.07 # He et al. (2020) and Dietrich et al. (2024) describe the range of planet eccentricities as [0.01,0.07]
RAYLEIGH_PLANET_SCALE = 0.025 # Rayleigh distribution with scale = 0.025 (He et al. (2020); Dietrich et al. (2024)) is fair for planet eccentricity (in line with the [0.01,0.07] range described by He et al. (2020) and Dietrich et al. (2024))
MU_LOGNORMAL_DELTA = 3.14 # from Dietrich et al. (2024) for Nominal Kepler Analog Sets
SIGMA_LOGNORMAL_DELTA = 0.76 # from Dietrich et al. (2024) for Nominal Kepler Analog Sets
MIN_DELTA_HILL = 2 * np.sqrt(3)  # the theoretical minimum value of delta for Hill stability (taken from Dietrich et al. (2024) who in turn cite Birn (1973), Gladman (1993), and Tremaine (2023)) 

###########################################################################################################

# Helper functions for robust analytical integration and sampling
def integrate_power_law(gamma, low, high):
    if np.isclose(gamma, -1.0): # is it near -1?
        return np.log(high / low) # x^-1 integrates differently
    return (high**(gamma + 1.0) - low**(gamma + 1.0)) / (gamma + 1.0)

def sample_power_law(gamma, low, high, w):
    if np.isclose(gamma, -1.0):
        return low * (high / low)**w
    return (low**(gamma + 1.0) + w * (high**(gamma + 1.0) - low**(gamma + 1.0)))**(1.0 / (gamma + 1.0))

def sample_fisher_inclination():

    U = np.random.uniform(0, 1)
    del_i = np.arccos(1+(np.log(U))/KAPPA)

    return del_i

def mass_to_radius(M):
    if M >= 1.0:
        return M**1.0
    else:
        return M**0.8


def generate_system(M1):
    if not (M1_MIN <= M1 <= M1_MAX):
        raise ValueError(f"M1 must be between {M1_MIN} and {M1_MAX}")
# therefore, M1 is now in range


    logP = np.random.normal(LOGP_MEAN, LOGP_STD)
    while not (LOGP_MIN <= logP <= LOGP_MAX):
        logP = np.random.normal(LOGP_MEAN, LOGP_STD)
# Binary Periodicity sampled and in correct range

    logP_twin = 8.0 - M1  
    if logP < 1:
        F_twin = 0.30 - 0.15 * np.log10(M1)  # twin fraction for logP < 1, Moe & Di Stefano (2017)
    elif 1 <= logP <= logP_twin:
        F_twin = (0.30 - 0.15 * np.log10(M1)) * (1-((logP-1)/(logP_twin-1)))  # twin fraction for 1 <= logP <= logP_twin, Moe & Di Stefano (2017)
    else: # this branch is never triggering in practice
        F_twin = 0.0  # twin fraction for logP > logP_twin, Moe & Di Stefano (2017)


# finding analytical areas ^
    I_small = integrate_power_law(GAMMA_SMALL, Q_SMALL_LO, Q_SMALL_HI)
    I_large = (Q_SMALL_HI**(GAMMA_SMALL - GAMMA_LARGE)) * integrate_power_law(GAMMA_LARGE, Q_LARGE_LO, Q_LARGE_HI)    
# Calculate the precise probability of falling into the excess twin regime
    P_twin = F_twin / (1.0 + (1.0 - F_twin) * (I_small / I_large)) #derived from F_twin = N_twin/(N_twin+N_large), N_small/N_large = I_small/I_large, and P_twin = N_twin/(N_twin+N_small+N_large)

# Roll random variable U to decide mass ratio path
    U = np.random.random()
    if U < P_twin: # twin excess path: sample uniformly when near identical masses
        q = np.random.uniform(Q_TWIN_LO, Q_TWIN_HI) 
    else: 
    # broken power law
    # Rescale U to a new uniform random variable V in [0, 1)
        V = (U - P_twin) / (1.0 - P_twin)
    
    # Check conditional regime split at q = 0.3
        P_small_cond = I_small / (I_small + I_large)
    
        if V < P_small_cond:
        # Sample q dynamically in the small-q interval [0.1, 0.3)
            W = V / P_small_cond
            q = sample_power_law(GAMMA_SMALL, Q_SMALL_LO, Q_SMALL_HI, W)
        else:
        # Sample q dynamically in the large-q interval [0.3, 1.0]
            W = (V - P_small_cond) / (1.0 - P_small_cond)
            q = sample_power_law(GAMMA_LARGE, Q_LARGE_LO, Q_LARGE_HI, W)

    M2 = q* M1 # this is the mass of the secondary star, which is now defined by the mass ratio q and the primary mass M1

    P = 10**logP # this is the period of the binary system in days, which is now defined by the logP variable
    e_max = 1.0 - (P/2.0)**(-2.0/3.0) # Moe & Di Stefano (2017), Section 2, Equation (3)

    if e_max > 0.8:
        max_permissible_eccentricity = 0.8 # for the Holman and Weigert (1999) Empirical Polynomial, the range is determined for [0, 0.7-0.8], so we need to limit the maximum eccentricity to 0.8 for the polynomial to be valid
    else:
        max_permissible_eccentricity = e_max 

    if logP < LOGP_CIRCULAR:
        e = 0.0  
    else:
        e = np.random.rayleigh(scale=RAYLEIGH_STAR_SCALE, size=None) # Rayleigh Distribution is the distribution for binary stars within the above fixed period bounds, Wu et al. (2024)
        while not 0.0 < e < max_permissible_eccentricity:
            e = np.random.rayleigh(scale=RAYLEIGH_STAR_SCALE, size=None)  

    return {
        "M1": M1, "M2": M2, "q": q,
        "P": P, "logP": logP, "e": e,
        "R1": mass_to_radius(M1), "R2": mass_to_radius(M2),
    }
   

def get_ze_orbits(sy):
    """
    Phase II - Step 1: Calculate the binary anchor parameters and 
    the Holman & Wiegert (1999) critical stability radius (a_crit).
    
    Parameters:
    -----------
    sy : dict
        Output dictionary from Phase I containing:
        - M1 : Primary mass in M_sun
        - M2 : Secondary mass in M_sun
        - P  : Orbital period in days
        - e  : Binary eccentricity
        
    Returns:
    --------
    orbits : dict
        - M_bin  : Total binary mass (M_sun)
        - mu_bin : Binary mass ratio parameter M2 / (M1 + M2)
        - a_bin  : Binary semi-major axis (AU)
        - a_crit : Critical inner stability limit for planets (AU)
        - ratio  : Ratio of a_crit / a_bin
    """
    M1 = sy['M1']
    M2 = sy['M2']
    P = sy['P']
    e_bin = sy['e']

    # total host mass
    M_bin = M1 + M2

    # mass-ratio parameter
    mu_bin = M2 /M_bin

    # Kepler's Third Law to calculate semi-major axis 'a' in Astronomical Units (AU)
    P_yr = P / EARTH_YEAR_DAYS  # convert period from days to years
    a_bin = (M_bin * (P_yr**2))**(1.0 / 3.0)

    # a_crit = a_bin * ratio
    # from Holman and Wiegert (1999) a_c = 1.60 + 5.10*e - 2.22*e^2 + 4.12*mu -4.27*e*mu - 5.09 mu^2 + 4.61 e^2 mu^2
    ratio = 1.60 + 5.10*e_bin - 2.22*e_bin**2 + 4.12*mu_bin - 4.27*e_bin*mu_bin - 5.09*mu_bin**2 + 4.61*e_bin**2 * mu_bin**2

    # Physical critical semi-major axis
    a_crit = a_bin * ratio


    return {
        'M_bin': M_bin,
        'mu_bin': mu_bin,
        'a_bin': a_bin,
        'a_crit': a_crit,
        'ratio': ratio
    }


def exofirst(orb,MIN_MASS,MAX_MASS):

    log_m1 = np.random.uniform(np.log10(MIN_MASS), np.log10(MAX_MASS)) # from Dietrich et al. (2024)
    m1_earth = 10**log_m1

    m1_solar = m1_earth * M_EARTH_TO_MSUN

    pileup_factor = np.random.uniform(1.09, 1.46) # from Welsh et al. (2014)
    a_1 = orb['a_crit'] * pileup_factor # because a_1 ~ factor * a_crit

    M_bin = orb['M_bin']
    P_yr_1 = np.sqrt((a_1**3) / (M_bin + m1_solar))
    P_days_1 = P_yr_1 * EARTH_YEAR_DAYS

    planet1_inclination = sample_fisher_inclination() # Li et al. (2018) 

    e_1 = np.random.rayleigh(scale=RAYLEIGH_PLANET_SCALE)
    while not (PLANET_MIN_ECCENTRICITY < e_1 < PLANET_MAX_ECCENTRICITY):
        e_1 = np.random.rayleigh(scale=RAYLEIGH_PLANET_SCALE)

    return {
        'm1_earth': m1_earth,
        'm1_solar': m1_solar,
        'a_1': a_1,
        'P_days_1': P_days_1,
        'inclination': planet1_inclination,
        'e_1': e_1
    }

def planetmaker(orb,exoplanet1data, planetnum):

    # R_H = (a1+a2)/2 * [(m_p1+m_p2)/(3(M1+M2))]^(1/3)], from Li et al. (2018), Equation 26 -> mutual Hill Radius, adapted for Circumstellars
    # Delta = 2(a_2(1-e_2) - a_1(1+e_1)) / (R_H), from Dietrich et al. (2024) 
    # Assumption that Dietrich et al. (2024) definition of Delta holds even for Circumstellars

    # need planet 1 data

    planets = [exoplanet1data]

    # Generate Planets 2 through planetnum
    for p_idx in range(2, planetnum + 1):
        prev_planet = planets[-1]

        # Extract previous planet parameters
        a_prev = prev_planet.get('a_1', prev_planet.get('a'))
        e_prev = prev_planet.get('e_1', prev_planet.get('e'))
        m_prev_solar = prev_planet.get('m1_solar', prev_planet.get('m_solar'))

        # Sample planet mass log-uniformly in [MIN_MASS, MAX_MASS] Earth masses
        log_m_i = np.random.uniform(np.log10(MIN_MASS), np.log10(MAX_MASS))
        m_i_earth = 10**log_m_i
        m_i_solar = m_i_earth * M_EARTH_TO_MSUN

        # Calculate mutual mass ratio mu_m (Li et al. 2018, Eq. 26)
        mu_m = ((m_prev_solar + m_i_solar) / (3.0 * orb['M_bin'])) ** (1.0 / 3.0)


        # Sample eccentricity from Rayleigh(0.025) bounded in [0.01, 0.07]
        e_i = np.random.rayleigh(scale=RAYLEIGH_PLANET_SCALE)
        while not (PLANET_MIN_ECCENTRICITY < e_i < PLANET_MAX_ECCENTRICITY):
            e_i = np.random.rayleigh(scale=RAYLEIGH_PLANET_SCALE)

        # Sample mutual Hill spacing Delta ~ Log-Normal(3.14, 0.76) with Delta >= 8.0
        delta_ceiling = 2.0 * (1.0 - e_i) / mu_m  # if delta exceeds this, we're going to get negative values for a_i
        delta_i = np.random.lognormal(mean=MU_LOGNORMAL_DELTA, sigma=SIGMA_LOGNORMAL_DELTA)
        while not (MIN_DELTA_HILL <= delta_i < delta_ceiling):
            delta_i = np.random.lognormal(mean=MU_LOGNORMAL_DELTA, sigma=SIGMA_LOGNORMAL_DELTA)


        # Solve for outer semi-major axis a_i using exact eccentricity-dependent formula (Dietrich, Malhotra, & Apai 2024, Eq. 1)
        num = 2* (1.0 + e_prev) + (delta_i * mu_m )
        den = 2* (1.0 - e_i) - (delta_i * mu_m)
        a_i = a_prev * (num / den)

        # Compute orbital period in days via Kepler's 3rd Law
        P_i_days = np.sqrt(a_i**3 / (orb['M_bin'] + m_i_solar)) * EARTH_YEAR_DAYS

        # Sample mutual inclination delta_i (von Mises-Fisher, KAPPA = 500.0)
        incl_i = sample_fisher_inclination()

        # Store planet dictionary
        planet_data = {
            'planet_index': p_idx,
            'm_earth': m_i_earth,
            'm_solar': m_i_solar,
            'a': a_i,
            'P_days': P_i_days,
            'e': e_i,
            'inclination': incl_i,
            'delta_hill': delta_i
        }
        planets.append(planet_data)

    return planets

def export_system_data(binary_data, planets_list, output_mode, filename_prefix):
    """
    Exports system data to the terminal, a CSV/Excel spreadsheet, or both.
    
    Parameters:
        binary_data (dict): Binary star & stability parameters (M1, M2, a_bin, e_bin, a_crit, etc.).
        planets_list (list of dict): List of planet dictionaries from planetmaker().
        output_mode (str): 'terminal', 'csv', 'excel', or 'both'.
        filename_prefix (str): Base filename for exported spreadsheets.
    """
    df_planets = pd.DataFrame(planets_list)

    # Clean up and select display/export columns
    export_cols = ['planet_index', 'a', 'P_days', 'm_earth', 'e', 'inclination', 'delta_hill']
    col_names = {
        'planet_index': 'Planet_ID',
        'a': 'SemiMajorAxis_AU',
        'P_days': 'Period_Days',
        'm_earth': 'Mass_Mearth',
        'e': 'Eccentricity',
        'inclination': 'Inclination_deg',
        'delta_hill': 'Hill_Spacing_Delta'
    }
    df_export = df_planets[[c for c in export_cols if c in df_planets.columns]].rename(columns=col_names)
    
    # --- 1. TERMINAL OUTPUT ---
    if output_mode in ['terminal', 'both']:
        print("\n" + "="*70)
        print("          CIRCUMBINARY STAR SYSTEM & PLANETARY ARCHITECTURE         ")
        print("="*70)
        print(f"Primary Star Mass (M1)   : {binary_data['M1']:.2f} M_sun")
        print(f"Secondary Star Mass (M2) : {binary_data['M2']:.2f} M_sun")
        print(f"Binary Separation (a_bin): {binary_data['a_bin']:.4f} AU")
        print(f"Binary Period (P_bin)    : {binary_data['P_bin_days']:.2f} days")
        print(f"Binary Eccentricity      : {binary_data['e_bin']:.4f}")
        print(f"Critical Stability (a_crit): {binary_data['a_crit']:.4f} AU (Holman & Wiegert 1999)")
        print("-" * 70)
        print(df_export.to_string(index=False, float_format=lambda x: f"{x:8.4f}"))
        print("="*70 + "\n")

    # --- 2. SPREADSHEET OUTPUT (CSV) ---
    if output_mode in ['csv', 'both']:
        csv_filename = os.path.join(SCRIPT_DIR, f"{filename_prefix}.csv")
        df_export.to_csv(csv_filename, index=False)
        print(f"✓ Planet data successfully exported to CSV spreadsheet: {csv_filename}")

    # --- 3. SPREADSHEET OUTPUT (Excel with Multi-Tab Metadata) ---
    if output_mode in ['excel', 'both']:
        excel_filename = os.path.join(SCRIPT_DIR, f"{filename_prefix}.xlsx")
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            # Tab 1: Central Binary & System Metadata
            df_binary = pd.DataFrame([binary_data])
            df_binary.to_excel(writer, sheet_name='Binary_Stars', index=False)
            
            # Tab 2: Full Planet System Architecture
            df_export.to_excel(writer, sheet_name='Planets', index=False)
            
        print(f"✓ Multi-tab system spreadsheet exported to Excel: {excel_filename}")


if __name__ == "__main__":
    # Set seed for reproducible trial runs
   
    print("=" * 65)
    print("      ORBITPLOTTER INLURI: PHASE I, II, & INTERESTING SIDE-TANGENT; COMPLETE        ")
    print("=" * 65)

    print("\nWelcome to OrbitPlotter Inluri !!!! This program generates circumbinary star systems and their planetary architectures !!!\n")
    
    many_or_one = input("\nDo you have a custom number of systems to generate or are you okay with one? (yes, many = y | no, one is fine thank you =n ) ").strip().lower()
    if many_or_one == 'y':
        n = int(input("Enter the number of systems to generate: "))
    else:
        n = 1

    are_you_hungry_for_planets = input("\nDo you want to generate a custom number of planets, or are you fine with 10?  Note that all generated systems will have the same number of input planets. (i want my own number!! = y | ten is good, thanks = n): ").strip().lower()
    if are_you_hungry_for_planets == 'y':
        planetnum = int(input("Enter number of planets for the systems to have: "))
    else:
        planetnum = 10  # Default number of planets

    choose = input("\nDo you want to input your own primary masses? (y/n): ").strip().lower()
    choose_seed = input("Do you want to set a seed? (all generated systems will draw from the same seed) (y/n): ").strip().lower()
    if choose_seed == 'y':
        num_for_seed = int(input("Enter an integer seed value: "))
    else:
        num_for_seed = np.random.randint(1, 1000)
        print(f"\nRandom seed generated is: {num_for_seed}")

    np.random.seed(num_for_seed)  

    for i in range(0, n):
        if choose == 'y':
            M1 = float(input(f"Input Mass of your Primary Star in M_sol between {M1_MIN} and {M1_MAX} for SYSTEM #{i+1}: "))
            while not (M1_MIN <= M1 <= M1_MAX):
                M1 = float(input(f"Invalid! Primary Star's mass must be between {M1_MIN} and {M1_MAX} in M_sol: "))
        else:
            print(f"\nGenerated random primary mass for SYSTEM #{i+1} from the range between {M1_MIN} and {M1_MAX} M_sol !!")
            M1 = np.random.uniform(M1_MIN, M1_MAX)

        sy = generate_system(M1)
        orb = get_ze_orbits(sy)
        exoplanet1data = exofirst(orb, MIN_MASS, MAX_MASS)
        exoplanet1data_normalized = {
            'planet_index': 1,
            'm_earth': exoplanet1data['m1_earth'],
            'm_solar': exoplanet1data['m1_solar'],
            'a': exoplanet1data['a_1'],
            'P_days': exoplanet1data['P_days_1'],
            'e': exoplanet1data['e_1'],
            'inclination': exoplanet1data['inclination'],
            'delta_hill': None,  # planet 1 doesn't have a Hill-spacing value as it is anchored to a_crit instead
        }
        system_planets = [exoplanet1data_normalized] + planetmaker(orb, exoplanet1data, planetnum)[1:]
        binary_data = {**sy, **orb, 'P_bin_days': sy['P'], 'e_bin': sy['e']}

            # Prompt user for output preference
        print("\nSelect Output Preference:")
        print("  [1] Terminal Output Only")
        print("  [2] CSV Spreadsheet Only")
        print("  [3] Excel Workbook (.xlsx) with Binary & Planet Tabs")
        print("  [4] All Of The Above")

        choice = input("Enter option (1-4): ").strip()
    
        mode_map = {'1': 'terminal', '2': 'csv', '3': 'excel', '4': 'both'}
        selected_mode = mode_map.get(choice, 'both')
    
        export_system_data(binary_data, system_planets, output_mode=selected_mode, filename_prefix=f'circumbinary_system_{i+1}')
