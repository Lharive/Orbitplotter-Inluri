# Special Thanks to Artifexian, who's Worldsmith 7.01 Calculator was the chief reference for my own spreadsheet, Lightmapper Inluri
# OrbitPlotter Inluri is the Python translation of the Lightmapper Inluri spreadsheet

def lum(mass): #returns output in Lsol
    if mass < 0.43:
        return 0.23 * (mass)**(2.3)
    elif  0.43 <= mass < 2:
        return (mass)**4
    elif 2 <= mass < 55:
        return 1.4* (mass)**(3.5)
    else:
        return 32000 * mass

def get_star(name):
    mass = float(input(f"Mass of {name} in Msol: ")) # must be in Msol
    lumin = lum(mass)
    radius = (10**0.003)*(mass**0.724) # from logR = 0.003 + 0.724log(M)
    return mass, lumin, radius #returns in Msol, Lsol, and Rsol respectively

def MaxStarAge(mass,lumin): #returns output in Gyrs
    return 10 * (mass/lumin)

# Section A: Star Parameters

print("\n-------------------------- Section A: Star Parameters --------------\n")

M1, L1, R1 = get_star("Star 1")
M2, L2, R2 = get_star("Star 2")
System_Age = float(input("Input the age of your stars in Gyrs ")) # must be in Gyrs
MaxSysAge = min(MaxStarAge(M1,L1),MaxStarAge(M2,L2))

while System_Age > MaxSysAge:
    print("Your input age is too high as the system will already have evolved past main sequence assumptions. Please retry")
    System_Age = float(input("Input the age of your stars in Gyrs ")) # must be in Gyrs

q = min(M1,M2)/max(M1,M2) #i dont know why i computed this, but i'll just leave this here for now

# output section

print("\n\n")
print("Star 1: mass =", M1, "luminosity =", L1, "maximum age =",MaxStarAge(M1,L1), "radius =",R1)
print("Star 2: mass =", M2, "luminosity =", L2, "maximum age =",MaxStarAge(M2,L2), "radius =",R2)
print("Maximum Age of the System",MaxSysAge)
print("mass ratio q=",q)
print("\n\n")
# need to calc density, temperature for Section A to be over
# Section B covers dynamic of the two stars

print("\n-------------------------- Section B: Dynamic of the Two Stars --------------\n")


