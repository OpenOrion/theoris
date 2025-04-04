"""
Example demonstrating proof verification capabilities with the ideal gas law.

This example shows how to use the proof verification capabilities to verify
properties of the ideal gas law.
"""

from theoris.utils.units import ureg
from theoris import Symbol, Section

# Define symbolic variables for the ideal gas law
P_sym = Symbol('P')  # Pressure
V_sym = Symbol('V')  # Volume
n_sym = Symbol('n')  # Number of moles
R_sym = Symbol('R')  # Gas constant
T_sym = Symbol('T')  # Temperature

# Define the ideal gas law equation: PV = nRT
ideal_gas_law = P_sym * V_sym - n_sym * R_sym * T_sym

# Create a proof section for the ideal gas law
proof_section = Section(
    "Ideal Gas Law Proofs",
    description="Proofs related to the ideal gas law",
    show_in_documentation=True
)

# Add assumptions - simplified to avoid PySMT conversion issues
proof_section.add_assumption(P_sym > 0, "Pressure is positive")

# Add theorems about the ideal gas law
# Solve for P: P = nRT/V
P_expr = n_sym * R_sym * T_sym / V_sym

# Theorem 1: If temperature increases, pressure increases (at constant volume and moles)
T1 = Symbol('T1')
T2 = Symbol('T2')
P1 = n_sym * R_sym * T1 / V_sym
P2 = n_sym * R_sym * T2 / V_sym

proof_section.add_implication_theorem(
    T2 > T1,
    P2 > P1,
    "If temperature increases, pressure increases (at constant volume and moles)"
)

# Theorem 2: If volume decreases, pressure increases (at constant temperature and moles)
V1 = Symbol('V1')
V2 = Symbol('V2')
P1 = n_sym * R_sym * T_sym / V1
P2 = n_sym * R_sym * T_sym / V2

proof_section.add_implication_theorem(
    V1 > V2,
    P2 > P1,
    "If volume decreases, pressure increases (at constant temperature and moles)"
)

# Theorem 3: If number of moles increases, pressure increases (at constant temperature and volume)
n1 = Symbol('n1')
n2 = Symbol('n2')
P1 = n1 * R_sym * T_sym / V_sym
P2 = n2 * R_sym * T_sym / V_sym

proof_section.add_implication_theorem(
    n2 > n1,
    P2 > P1,
    "If number of moles increases, pressure increases (at constant temperature and volume)"
)

# Verify all theorems
print("Verifying theorems...")
results = proof_section.verify_theorems()

# Print the proof summary
print("\n" + proof_section.get_proof_summary())

# No code generation for now to avoid errors

# Example of using Symbol with verification capabilities
print("\n\nExample of using Symbol with verification capabilities:")

# Define symbols with physical units
R = Symbol(
    "R",
    8.314,  # Value
    description="universal gas constant",
    latex="R",
    units=ureg.J / (ureg.mol * ureg.K),
)

T = Symbol(
    "T",
    300.0,  # Value (300 K)
    description="temperature",
    latex="T",
    units=ureg.K
)

P = Symbol(
    "P",
    description="pressure",
    latex="P",
    units=ureg.Pa
)

V = Symbol(
    "V",
    0.0224,  # Value (22.4 L at STP)
    description="volume",
    latex="V",
    units=ureg.m**3
)

n = Symbol(
    "n",
    1.0,  # Value (1 mole)
    description="number of moles",
    latex="n",
    units=ureg.mol
)

# Define the ideal gas law: P = nRT/V
P.set_expression(n * R * T / V)

# Add constraints to the pressure symbol
P.add_constraint(P > 0, "Pressure is always positive")

# Verify the constraints
print("\nVerifying pressure constraints...")
P_results = P.verify_constraints()

# Print the proof results
print("\n" + P.get_proof_summary())

# Calculate the actual pressure value
# We can't directly convert the symbolic expression to float, so let's calculate it manually
n_val = 1.0  # 1 mole
R_val = 8.314  # J/(mol*K)
T_val = 300.0  # 300 K
V_val = 0.0224  # 22.4 L

P_val = n_val * R_val * T_val / V_val
print(f"\nCalculated pressure: {P_val:.2f} Pa")
print(f"Calculated pressure: {P_val / 101325:.2f} atm")
