# %%
"""
Example demonstrating code generation for energy calculations.

This example creates a section for calculating the total mechanical energy
of an object and generates code for it.
"""

from theoris.utils.symbols import resolve
from theoris.utils.units import ureg
from theoris import Symbol, Section, Documentation
from theoris.generators.code import CodeGenerator
from theoris.generators.documentation import DocumentationGenerator
from pathlib import Path


# %% Create symbols for inputs
mass = Symbol(
    "m",
    description="Mass of the object",
    latex="m",
    units=ureg.kg,
)

velocity = Symbol(
    "v",
    description="Velocity of the object",
    latex="v",
    units=ureg.m / ureg.s,
)

height = Symbol(
    "h",
    description="Height of the object above ground",
    latex="h",
    units=ureg.m,
)

gravity = Symbol(
    "g",
    9.81,  # Value
    description="Acceleration due to gravity",
    latex="g",
    units=ureg.m / ureg.s**2,
)

# Create intermediate symbols for kinetic and potential energy
kinetic_energy = Symbol(
    "E_k",
    0.5 * mass * velocity**2,
    description="Kinetic energy of the object",
    latex="E_k",
    units=ureg.J
)

potential_energy = Symbol(
    "E_p",
    mass * gravity * height,
    description="Potential energy of the object",
    latex="E_p",
    units=ureg.J
)

# Create a symbol for the output (total energy)
total_energy = Symbol(
    "E_total",
    kinetic_energy + potential_energy,
    description="Total mechanical energy of the object",
    latex="E_{total}",
    units=ureg.J
)


# %%
resolve(total_energy)


# %% Create a section for energy calculation
energy_section = Section.from_symbol(
    total_energy,
    "Energy Calculation",
    args=[mass, velocity, height, gravity],
    statements=[kinetic_energy, potential_energy, total_energy],
    show_in_documentation=True
)
energy_section


# %% Create a documentation object
documentation = Documentation(
    "Mechanical Energy Example",
    [energy_section],
)

# %% Generate documentation and code
print("\nGenerating documentation and code...")

# Create output directory
output_dir = Path("out")
output_dir.mkdir(exist_ok=True)

# Generate documentation
print("\nGenerating documentation...")
dgen = DocumentationGenerator(output_dir)
dgen.generate_documentation(documentation)

# Generate code
print("\nGenerating code...")
cgen = CodeGenerator(output_dir)
cgen.generate_code(documentation)

print(f"\nGeneration completed successfully!")
print(f"Documentation with diagrams: out/doc/diagrams/energy_calculation_io.png")
print(f"Generated code: out/lib/energy_calculation.py")

# %%
