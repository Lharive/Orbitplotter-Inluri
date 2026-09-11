# Special Thanks to Artifexian, who's Worldsmith 7.01 Calculator was the chief reference for my own spreadsheet, Lightmapper Inluri
# Worldsmith 7.01 was still a spreadsheet that fundamentally dealt with single-star systems, so it was unable to meet my needs. 
# Lightmapper Inluri started as my attempt to use  it (and my own limited ability) to extend it into binary systems, although it grew into something larger.
# OrbitPlotter Inluri is the Python translation of the Lightmapper Inluri spreadsheet but has a different scope.
# This is v2 of OrbitPlotter Inluri, because the previous one was kind of a mess to read through. I had initially paused work on it to read up on the literature but when I returned to it, I found it an eyesore. 
# Project scope has not changed

import numpy as np 

# Helper functions for robust analytical integration and sampling
def integrate_power_law(gamma, low, high):
    if np.isclose(gamma, -1.0): # is it near -1?
        return np.log(high / low) # x^-1 integrates differently
    return (high**(gamma + 1.0) - low**(gamma + 1.0)) / (gamma + 1.0)

def sample_power_law(gamma, low, high, w):
    if np.isclose(gamma, -1.0):
        return low * (high / low)**w
    return (low**(gamma + 1.0) + w * (high**(gamma + 1.0) - low**(gamma + 1.0)))**(1.0 / (gamma + 1.0))

def mass_to_radius(M):
    if M >= 1.0:
        return M**1.0
    else:
        return M**0.8

############################ CONSTANTS AND PARAMETERS: THE COMPENDIUM ####################################

M1_MIN, M1_MAX = 0.8, 1.2                # valid primary-mass range, Moe & Di Stefano (2017)
LOGP_MEAN, LOGP_STD = 5.0, 2.3           # Raghavan et al. (2010) solar-type period distribution
LOGP_MIN, LOGP_MAX = 0.2, 3.0            # close-binary regime where Rayleigh e-model is valid, Wu et al. (2024)
LOGP_CIRCULAR = 1.0                      # below this, tidal circularization : e = 0
GAMMA_SMALL, GAMMA_LARGE = 0.3, -0.5     # Moe & Di Stefano (2017) Eq. 13, Eq. 9
Q_SMALL_LO, Q_SMALL_HI = 0.1, 0.3
Q_LARGE_LO, Q_LARGE_HI = 0.3, 1.0
Q_TWIN_LO, Q_TWIN_HI = 0.95, 1.0
RAYLEIGH_SCALE = 0.3

###########################################################################################################

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

    if logP < LOGP_CIRCULAR:
        e = 0.0  
    else:
        e = np.random.rayleigh(scale=RAYLEIGH_SCALE, size=None) # Rayleigh Distribution is the distribution for binary stars within the above fixed period bounds, Wu et al. (2024)
        while not 0.0 < e < e_max:
            e = np.random.rayleigh(scale=RAYLEIGH_SCALE, size=None)  

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
    anchor : dict
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
    P_yr = P / 365.2525
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

if __name__ == "__main__":
    # Set seed for reproducible trial runs
    np.random.seed(42)  
    
    print("=" * 65)
    print("      ORBITPLOTTER INLURI: PHASE I + PHASE II STEP 1")
    print("=" * 65)
    
    n=int(input("Enter the number of systems to generate: "))

    choose = input("Do you want to input your own primary masses? (y/n): ").strip().lower()

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

        print(f"\n--- SYSTEM #{i+1} ---")
        print(f"Primary Mass (M1)      : {sy['M1']:.3f} M_sol")
        print(f"Secondary Mass (M2)    : {sy['M2']:.3f} M_sol (q = {sy['q']:.3f})")
        print(f"Binary Period (P)      : {sy['P']:.2f} days (logP = {sy['logP']:.3f})")
        print(f"Binary Eccentricity (e): {sy['e']:.3f}")
        print(f"Total Binary Mass      : {orb['M_bin']:.3f} M_sol")
        print(f"Mass Ratio Param (mu)  : {orb['mu_bin']:.3f}")
        print(f"Binary Separation (a)  : {orb['a_bin']:.4f} AU")
        print(f"Holman Ratio (a_c/a_b) : {orb['ratio']:.3f}")
        print(f"Critical Stability (a_c): {orb['a_crit']:.4f} AU")
        print(f"\n ----------------------------------------------\n")
        
    print("\n" + "=" * 65)
