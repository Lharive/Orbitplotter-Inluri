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
    if np.isclose(gamma, -1.0):
        return np.log(high / low)
    return (high**(gamma + 1.0) - low**(gamma + 1.0)) / (gamma + 1.0)

def sample_power_law(gamma, low, high, w):
    if np.isclose(gamma, -1.0):
        return low * (high / low)**w
    return (low**(gamma + 1.0) + w * (high**(gamma + 1.0) - low**(gamma + 1.0)))**(1.0 / (gamma + 1.0))



M1 = float(input("Input Mass of your Primary Star in Msol between 0.8 and 1.2 ")) # Need primary mass
while not 0.8 <= M1 <= 1.2: # defined limit for lognormal distribution to be a valid model for circumbinary orbits, Moe & Di Stefano (2017) and Wu et al. (2024)
    M1 = float(input("Invalid! Primary Star's mass must be between 0.8 and 1.2 for this programme to yield correct results ")) 

# therefore, M1 is now in range


logP = np.random.normal(5.0, 2.3)
while not 0.2 <= logP <= 3.0:
    logP = np.random.normal(5.0, 2.3)  # logP limits for the close stellar binaries to follow a Rayleigh distribution for binary eccentricities is logP > 0.2 and logP < 3.0, per  Wu et al. (2024)

# Binary Periodicity sampled and in correct range

logP_twin = 8.0 - M1  

if logP < 1:
    F_twin = 0.30 - 0.15 * np.log10(M1)  # twin fraction for logP < 1, Moe & Di Stefano (2017)
elif 1 <= logP <= logP_twin:
    F_twin = (0.30 - 0.15 * np.log10(M1)) * (1-((logP-1)/(logP_twin-1)))  # twin fraction for 1 <= logP <= logP_twin, Moe & Di Stefano (2017)
else:
    F_twin = 0.0  # twin fraction for logP > logP_twin, Moe & Di Stefano (2017)


# Constant slopes for unevolved, close solar-type binaries
gamma_small = 0.3   # Moe & Di Stefano (2017) Equation 13
gamma_large = -0.5  # Moe & Di Stefano (2017) Equation 9

# Calculate analytical areas
I_small = integrate_power_law(gamma_small, 0.1, 0.3)
I_large = (0.3**(gamma_small - gamma_large)) * integrate_power_law(gamma_large, 0.3, 1.0)

# Calculate the precise probability of falling into the excess twin regime
P_twin = F_twin / (1.0 + (1.0 - F_twin) * (I_small / I_large))

# Roll random variable U to decide mass ratio path
U = random.random()

if U < F_twin: # twin excess path: sample uniformly when near identical masses
    q = random.uniform(0.95, 1.0) 
else: 
    # broken power law
    # Rescale U to a new uniform random variable V in [0, 1)
    V = (U - P_twin) / (1.0 - P_twin)
    
    # Check conditional regime split at q = 0.3
    P_small_cond = I_small / (I_small + I_large)
    
    if V < P_small_cond:
        # Sample q dynamically in the small-q interval [0.1, 0.3)
        W = V / P_small_cond
        q = sample_power_law(gamma_small, 0.1, 0.3, W)
    else:
        # Sample q dynamically in the large-q interval [0.3, 1.0]
        W = (V - P_small_cond) / (1.0 - P_small_cond)
        q = sample_power_law(gamma_large, 0.3, 1.0, W)

M2 = q* M1 # this is the mass of the secondary star, which is now defined by the mass ratio q and the primary mass M1

P = 10**logP # this is the period of the binary system in days, which is now defined by the logP variable
e_max = 1.0 - (P/2.0)**(-2.0/3.0) # this is the maximum eccentricity of the binary system, which is now defined by the period P


if logP < 1:
    e = 0.0  # circular orbit for logP < 1
else:
    e = np.random.rayleigh(scale=0.3, size=None) # Rayleigh Distribution is the distribution for binary stars within the above fixed period bounds, Wu et al. (2024)
    while not 0.0 < e < e_max:
        e = np.random.rayleigh(scale=0.3, size=None)  

print("Primary Mass M1 =", M1, "Msol")
print("Secondary Mass M2 =", M2, "Msol")
print("Binary Period P =", P, "days")
print("Eccentricity e =", e)