# Special Thanks to Artifexian, who's Worldsmith 7.01 Calculator was the chief reference for my own spreadsheet, Lightmapper Inluri
# Worldsmith 7.01 was still a spreadsheet that fundamentally dealt with single-star systems, so it was unable to meet my needs. 
# Lightmapper Inluri started as my attempt to use  it (and my own limited ability) to extend it into binary systems, although it grew into something larger.
# OrbitPlotter Inluri is the Python translation of the Lightmapper Inluri spreadsheet but has a different scope.
# This is v2 of OrbitPlotter Inluri, because the previous one was kind of a mess to read through. I had initially paused work on it to read up on the literature but when I returned to it, I found it an eyesore. 
# Project scope has not changed

import numpy as np # type: ignore
import random


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
LOGP_CIRCULAR = 1.0                      # below this, tidal circularization -> e = 0
GAMMA_SMALL, GAMMA_LARGE = 0.3, -0.5     # M&DS17 Eq. 13, Eq. 9
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
    else:
        F_twin = 0.0  # twin fraction for logP > logP_twin, Moe & Di Stefano (2017)


# finding analytical areas ^
    I_small = integrate_power_law(GAMMA_SMALL, Q_SMALL_LO, Q_SMALL_HI)
    I_large = (Q_SMALL_HI**(GAMMA_SMALL - GAMMA_LARGE)) * integrate_power_law(GAMMA_LARGE, Q_LARGE_LO, Q_LARGE_HI)    
# Calculate the precise probability of falling into the excess twin regime
    P_twin = F_twin / (1.0 + (1.0 - F_twin) * (I_small / I_large)) #derived from F_twin = N_twin/(N_twin+N_large), N_small/N_large = I_small/I_large, and P_twin = N_twin/(N_twin+N_small+N_large)

# Roll random variable U to decide mass ratio path
    U = random.random()
    if U < P_twin: # twin excess path: sample uniformly when near identical masses
        q = random.uniform(Q_TWIN_LO, Q_TWIN_HI) 
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
    e_max = 1.0 - (P/2.0)**(-2.0/3.0) # this is the maximum eccentricity of the binary system, which is now defined by the period P


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

if __name__ == "__main__":
    M1 = float(input(f"Input Mass of your Primary Star in Msol between {M1_MIN} and {M1_MAX}: "))
    while not (M1_MIN <= M1 <= M1_MAX):
        M1 = float(input(f"Invalid! Primary Star's mass must be between {M1_MIN} and {M1_MAX}: "))

    sys = generate_system(M1)
    for k, v in sys.items():
        print(k, "=", v)
