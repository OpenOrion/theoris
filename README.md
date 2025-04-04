# Theoris

## Overview

Theoris is a powerful tool for symbolic computation, code generation, and documentation generation. It allows you to define symbols with physical quantities, establish mathematical relationships between them, verify proofs, and automatically generate code and documentation.

## Installation

To install the library, use the following command:

```bash
pip install theoris

# To add z3 proof solver
pip install z3-solver
```

## Core Concepts

- **Symbol**: Represents a variable with physical units, description, and optional mathematical expression.
- **Section**: Groups related symbols together, similar to a function or method.
- **Documentation**: Contains sections and is used to generate code and documentation.

## Simple Example

Here's a simple example demonstrating how to use the library to model the relationship between temperature, pressure, and density in an ideal gas:

```python
from theoris.utils.units import ureg
from theoris import Symbol, Section, Documentation, generate

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

# Define a symbol with an expression relating it to other symbols
rho = Symbol(
    "rho",
    P / (R * T),  # Expression
    description="density",
    latex="\\rho",
    units=ureg.kg / ureg.m**3
)

# Create a documentation object with sections
documentation = Documentation(
    "Ideal Gas",
    [
        Section.from_symbol(
            rho,
            "Density",
            args=[P, T, R],
            show_in_documentation=True
        )
    ]
)

# Generate code
generate = generate(documentation, "./output", "code")
```

This example:
1. Defines symbols for gas constant, temperature, and pressure with appropriate units
2. Creates a density symbol with an expression relating it to the other symbols
3. Creates a documentation object with a section for the density calculation
4. Generates code and documentation for the model

## Features

- **Symbolic Computation**: Define symbols and mathematical relationships between them.
- **Physical Units**: Automatic unit conversion and validation using the Pint library.
- **Code Generation**: Generate code from symbolic expressions.
- **Documentation Generation**: Generate documentation with LaTeX equations.
- **Diagram Generation**: Generate diagrams from block inputs and outputs.
- **Coordinate System**: Work with coordinate systems using the Coordinate class.
- **Proof Verification**: Verify mathematical properties and constraints using SMT solvers.

## Advanced Usage

For more advanced usage, see the example files:
- `examples/thermodynamics.py`: Models thermodynamic relationships
- `examples/fluid_mechanics.py`: Models fluid mechanics relationships
- `examples/proof_verification_example.py`: Demonstrates proof verification capabilities
- `examples/inlet.py`: Demonstrates coordinate systems and extensions

These examples demonstrate:
- Importing symbols between models
- Using external function symbols
- Adding citations to documentation
- Creating complex mathematical relationships
- Verifying mathematical properties and constraints
- Working with coordinate systems and arrays

## Proof Verification

The Codegen Library includes proof verification capabilities that allow you to verify mathematical properties and constraints of your symbolic expressions using SMT (Satisfiability Modulo Theories) solvers.

### Example

Here's a simple example demonstrating how to use the proof verification capabilities:

```python
from theoris import Symbol, Section, Documentation
from theoris.verification import verify, implies
from theoris.utils.units import ureg

# Define symbols with physical units
T = Symbol("T", description="temperature", units=ureg.K)
P = Symbol("P", description="pressure", units=ureg.Pa)
V = Symbol("V", description="volume", units=ureg.m**3)
n = Symbol("n", description="number of moles", units=ureg.mol)
R = Symbol("R", 8.314, description="gas constant", units=ureg.J/(ureg.mol*ureg.K))

# Define the ideal gas law: PV = nRT
P.set_expression(n * R * T / V)

# Add constraints to the pressure symbol
P.add_constraint(P > 0, "Pressure is always positive")
P.add_constraint(
    P.expression.diff(T) > 0,
    "Pressure increases as temperature increases (at constant volume and moles)"
)

# Verify the constraints
results = P.verify_constraints()
print(P.get_proof_summary())
```

### Verification Capabilities

The proof verification module supports:

- **Property Verification**: Verify that symbols satisfy certain properties (e.g., bounds, monotonicity).
- **Equivalence Checking**: Verify that two expressions are equivalent.
- **Implication Verification**: Verify that one property implies another.
- **Conservation Laws**: Verify that conservation laws hold (e.g., sum of inputs equals sum of outputs).
- **Boundary Conditions**: Verify behavior at edge cases.

### Integration with Documentation

Proof results can be included in the generated documentation, providing formal verification of the mathematical models.

## Coordinate Systems

The Codegen Library includes support for coordinate systems through the `Coordinate` class. This allows you to work with 2D coordinates and perform operations on them.

### Example

```python
from sympy import Matrix
from theoris.coordinate import Coordinate
from theoris.utils.units import ureg

# Create a coordinate
position = Coordinate(
    name="position",
    ref=Matrix([10, 20]),  # x=10, y=20
    description="object position",
    units=ureg.m
)

# Access x and y components
print(position.x)  # Symbol representing x-coordinate
print(position.y)  # Symbol representing y-coordinate

# Use in expressions
velocity = Coordinate(
    name="velocity",
    ref=Matrix([5, 10]),
    description="object velocity",
    units=ureg.m/ureg.s
)
```

### Extensions

The library includes several extensions for working with coordinates:

- **Array**: Work with arrays of symbols
- **CoordinateJoin**: Join multiple coordinates together
- **Interval**: Define intervals with min and max values
- **ExternalFunction**: Use external functions in symbolic expressions

## License

This project is licensed under the MIT License.