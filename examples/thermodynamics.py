# %% Imports
from pathlib import Path
from sympy import solve
from theoris.generators.code import CodeGenerator
from theoris.utils.units import ureg
from theoris import Section, Symbol, ExternalFunctionSymbol,  Documentation

DOC_NAME = "Thermodynamics"

# %% Symbols
T, T0, P0, T01, P01, PR, eta_poly, u = [
    Symbol(
        "T",
        description="static fluid temperature",
        latex="T",
        units=ureg.K
    ),
    Symbol(
        "T0",
        description="stagnation temperature",
        latex="T_0",
        units=ureg.K
    ),
    Symbol(
        "P0",
        description="stagnation pressure",
        latex="P_0",
        units=ureg.Pa
    ),
    Symbol(
        "T01",
        description="stagnation inlet temperature",
        latex="T_{01}",
        units=ureg.K
    ),
    Symbol(
        "P01",
        description="stagnation inlet pressure",
        latex="T_{01}",
        units=ureg.Pa
    ),
    Symbol(
        "PR",
        description="pressure ratio",
        units=ureg.dimensionless
    ),
    Symbol(
        "eta_poly",
        description="polytropic efficiency",
        latex="\\eta_{poly}",
        units=ureg.dimensionless
    ),
    Symbol(
        "u",
        description="flow velocity",
        units=ureg.m/ureg.s
    ),
]

# %% Ratio of Specific Heats
gamma = ExternalFunctionSymbol(
    "gamma",
    description="ratio of specific heats",
    latex="\\gamma",
    units=ureg.dimensionless
)

# %% Specific Heat Constant Pressure
Cp = ExternalFunctionSymbol(
    "Cp",
    description="specific heat at constant pressure",
    latex="C_p",
    units=ureg.J / (ureg.kg * ureg.K)
)


# %% Outlet Stagnation Pressure
P02 = Symbol(
    "P02",
    PR * P01,
    description="stagnation outlet pressure",
    latex="P0_2",
    units=ureg.Pa
)

# %% Pressure Ratio
PR.set_expression(
    P02 / P01
)

# %% Outlet Stagnation Temperature
T02 = Symbol(
    "T02",
    T01 * (PR ** ((gamma-1)/(eta_poly*gamma))),
    description="stagnation outlet temperature",
    latex="T0_2",
    units=ureg.K
)

# %% Stagnation Temperature Change
DeltaT0 = Symbol(
    "DeltaT0",
    T02 - T01,
    description="stagnation temperature change between inlet and outlet",
    latex="\\Delta T_0",
    units=ureg.K
)

# %% Temperature Ratio
TR = Symbol(
    "TR",
    T02 / T01,
    description="stagnation temperature ratio between outlet and inlet",
    units=ureg.dimensionless
)

# %% Enthalpy Change
Deltah = Symbol(
    "Deltah",
    Cp*DeltaT0,
    description="enthalpy change between inlet and outlet",
    latex="\\Delta h",
    units=ureg.J / ureg.kg
)

# %% Static Temperature
T.set_expression(
    T0 - ((u**2)/(2*Cp))
)

# %% Stagnation Temperature
T0.set_expression(
    solve(T.expression - T, T0)[0]
)

# %% Static Pressure
P = Symbol(
    "P",
    P0 * ((T / T0) ** (gamma/(gamma-1))),
    description="static fluid pressure",
    latex="P",
    units=ureg.Pa
)

# %% Stagnation Pressure
P0.set_expression(
    solve(P.expression - P, P0)[0]
)

# %% Stagnation Temperature
T0.set_expression(
    solve(T.expression - T, T0)[0]
)

# %% Documentation
documentation = Documentation(
    DOC_NAME,
    [
        Section.from_symbol(
            gamma,
            "Ratio of Specific Heats",
            args=[T0],
            show_in_documentation=True
        ),
        Section.from_symbol(
            Cp,
            "Specific Heat Constant Pressure",
            args=[T0],
            show_in_documentation=True
        ),
        Section.from_symbol(
            T,
            "Static Temperature",
            args=[T0, u, Cp],
            show_in_documentation=True
        ),
        Section.from_symbol(
            P,
            "Static Pressure",
            args=[T, T0, P0, gamma],
            show_in_documentation=True
        ),
        Section.from_symbol(
            T0,
            "Stagnation Temperature",
            args=[T, u, Cp],
            show_in_documentation=True
        ),
        Section.from_symbol(
            P0,
            "Stagnation Pressure",
            args=[T, T0, P, gamma],
            show_in_documentation=True
        ),
        Section.from_symbol(
            P02,
            "Outlet Stagnation Pressure",
            args=[PR, P01],
            show_in_documentation=True
        ),
        Section.from_symbol(
            T02,
            "Outlet Stagnation Temperature",
            args=[PR, T01, gamma, eta_poly],
            show_in_documentation=True
        ),
        Section.from_symbol(
            DeltaT0,
            "Delta Temperature",
            args=[T01, T02],
            show_in_documentation=True
        ),
        Section.from_symbol(
            Deltah,
            "Delta Enthalpy",
            args=[DeltaT0, Cp],
            show_in_documentation=True
        ),
        Section.from_symbol(
            TR,
            "Temperature Ratio",
            args=[T01, T02],
            show_in_documentation=True
        ),
    ]
)
# %%
# Generate code
output_dir = Path("out")
output_dir.mkdir(exist_ok=True)

print("\nGenerating code...")
cgen = CodeGenerator(output_dir)
cgen.generate_code(documentation)
# %%
