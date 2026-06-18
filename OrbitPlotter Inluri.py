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
    return mass, lumin #returns in Msol and Lsol respectively

def MaxStarAge(mass,lumin): #returns output in Gyrs
    return 10 * (mass/lumin)

# Section A: Star Parameters
m1, L1 = get_star("Star 1")
m2, L2 = get_star("Star 2")
System_Age = float(input("Input the age of your stars in Gyrs ")) # must be in Gyrs
MaxSysAge = min(MaxStarAge(m1,L1),MaxStarAge(m2,L2))

while System_Age > MaxSysAge:
    print("Your input age is too high as the system will already have evolved past main sequence assumptions. Please retry")
    System_Age = float(input("Input the age of your stars in Gyrs ")) # must be in Gyrs

q = m2/m1 #i dont know why i computed this, but i'll just leave this here for now

print("Star 1: mass =", m1, "luminosity =", L1, "maximum age =",MaxStarAge(m1,L1))
print("Star 2: mass =", m2, "luminosity =", L2, "maximum age =",MaxStarAge(m2,L2))
print("Maximum Age of the System",MaxSysAge)

