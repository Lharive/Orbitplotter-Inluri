# Special Thanks to Artifexian, who's Worldsmith 7.01 Calculator was the chief reference for my own spreadsheet, Lightmapper Inluri
# Worldsmith 7.01 was still a spreadsheet that fundamentally dealt with single-star systems, so it was unable to meet my needs. 
# Lightmapper Inluri started as my attempt to use it (and my own limited ability) to extend it into binary systems, although it grew into something larger.
# OrbitPlotter Inluri is the Python translation of the Lightmapper Inluri spreadsheet but has a different scope.

##############################################3 Pre-Section: Define Functions and Formulae #####################################################

def lum(mass): #returns output in Lsol
    if mass < 0.43:
        return 0.23 * (mass)**(2.3)
    elif  0.43 <= mass < 2:
        return (mass)**4
    elif 2 <= mass < 55:
        return 1.4* (mass)**(3.5)
    else:
        return 32000 * mass

def MaxStarAge(mass,lumin): #returns output in Gyrs
    return 10 * (mass/lumin)

def density(mass,radius): #returns output in Dsol
    return mass/(radius**3) 

def temperature(radius,lumin): #returns output in Kelvin
    return 5776 * ((lumin/(radius)**2)**(0.25))

def get_star(name):
    mass = float(input(f"Mass of {name} in Msol: ")) # must be in Msol
    lumin = lum(mass)
    radius = (10**0.003)*(mass**0.724) # from logR = 0.003 + 0.724log(M)
    dense = density(mass,radius)
    temp = temperature(radius,lumin)
    return mass, lumin, radius, dense, temp #returns in Msol, Lsol, Rsol, Dsol, and Kelvin respectively

#####################################3 Section A: Star Parameters #####################################################################

print("\n-------------------------- Section A: Star Parameters --------------\n")

M1, L1, R1, D1, T1 = get_star("Star 1")
M2, L2, R2, D2, T2 = get_star("Star 2")
System_Age = float(input("Input the age of your stars in Gyrs ")) # must be in Gyrs
MaxSysAge = min(MaxStarAge(M1,L1),MaxStarAge(M2,L2))

while System_Age > MaxSysAge:
    print("Your input age is too high as the system will already have evolved past main sequence assumptions. Please retry")
    System_Age = float(input("Input the age of your stars in Gyrs ")) # must be in Gyrs

q = min(M1,M2)/max(M1,M2) #i dont know why i computed this, but i'll just leave this here for now

# output section

print("\n\n")
print("Star 1: mass =", M1, "luminosity =", L1, "maximum age =",MaxStarAge(M1,L1), "radius =",R1, "density =",D1, "surface temperature =", T1)
print("Star 2: mass =", M2, "luminosity =", L2, "maximum age =",MaxStarAge(M2,L2), "radius =",R2, "density =",D2, "surface temperature =", T2)
print("Maximum Age of the System",MaxSysAge)
print("mass ratio q=", q)
print("\n\n")
# Section B covers dynamic of the two stars

###############################################3 Section B: Dynamic of the Two Stars ###################################################################

print("\n-------------------------- Section B: Dynamic of the Two Stars --------------\n")


