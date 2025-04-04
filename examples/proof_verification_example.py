"""
Example demonstrating proof verification capabilities.

This example shows how to use the proof verification capabilities to verify
simple mathematical properties.
"""
# %%
from theoris import Symbol, Section

# Define a simple proof section
proof_section = Section(
    "Basic Mathematical Properties",
    description="Proofs of basic mathematical properties",
    show_in_documentation=True
)

# Create symbolic variables
x = Symbol('x')
y = Symbol('y')

# Add assumptions
proof_section.add_assumption(x > 0, "x is positive")
proof_section.add_assumption(y > 0, "y is positive")

# Add simple theorems
proof_section.add_theorem(x + y > 0, "Sum of positive numbers is positive")
proof_section.add_theorem(x * y > 0, "Product of positive numbers is positive")

# Add implication theorems
proof_section.add_implication_theorem(
    x > y,
    x**2 > y**2,
    "If x > y > 0, then x^2 > y^2"
)

# Verify all theorems
print("Verifying theorems...")
results = proof_section.verify_theorems()

# Print the proof summary
print("\n" + proof_section.get_proof_summary())

# Example of using ProofSymbol directly
x_symbol = Symbol(
    "x",
    expression=5,  # Assign a concrete value that satisfies the constraints
    description="A variable with value 5"
)

# Add constraints to the symbol
x_symbol.add_constraint(x_symbol > 0, "x is positive")
x_symbol.add_constraint(x_symbol < 10, "x is less than 10")

# Verify the constraints
print("\nVerifying x constraints...")
x_results = x_symbol.verify_constraints()

# Print the proof results
print("\n" + x_symbol.get_proof_summary())
# %%
