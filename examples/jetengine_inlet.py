# %% Imports
from sympy import Piecewise
from examples.fluid_mechanics import M, Rs, u, gamma_g, Cpg
from examples.thermodynamics import T0, P0, P, T, PR, T02, P02, gamma, Cp
from theoris import Symbol, FunctionSymbol, SymbolMapping, DataObject, Section, Documentation


DOC_NAME = "Inlet Thermodynamics"

# %% Symbols
u_i, T1_i, P1_i, T01_i = [
    Symbol.inherit(
        u,
        name="u_i",
        description="engine inlet {description}",
    ),
    Symbol.inherit(
        T,
        name="T1_i",
        description="engine inlet {description}",
        latex="T_{1_i}"
    ),
    Symbol.inherit(
        P,
        name="P1_i",
        description="engine inlet {description}",
        latex="P_{1_i}"
    ),
    Symbol(
        name="T01_i",
        description="engine inlet {description}",
        latex="T_{01_i}"
    )
]

gamma_i = Symbol.inherit(
    gamma_g,
    name="gamma_i",
    description="inlet {description}",
    latex="\\gamma_i",
)

Cp_i = FunctionSymbol(
    Cpg,
    [
        SymbolMapping(gamma_g, gamma_i)
    ],
    name="Cp_i",
    description="compressor {description}",
    latex="Cp_i",
)


# %% Engine Inlet Stagnation Temperature
M_i = FunctionSymbol(
    M,
    [
        SymbolMapping(u, u_i),
        SymbolMapping(gamma, gamma_i),
        SymbolMapping(T, T1_i)
    ],
    name="M_i",
    description="engine inlet {description}",
    latex="M_i"
)


# %% Engine Inlet Stagnation Temperature
T01_i = FunctionSymbol(
    T0,
    [
        SymbolMapping(u, u_i),
        SymbolMapping(Cp, Cp_i),
        SymbolMapping(T, T1_i)
    ],
    name=T01_i.name,
    description=T01_i.description,
    latex=T01_i.latex
)

# %% Engine Inlet Stagnation Pressure
P01_i = FunctionSymbol(
    P0,
    [
        SymbolMapping(gamma, gamma_i),
        SymbolMapping(P, P1_i),
        SymbolMapping(T0, T01_i),
        SymbolMapping(T, T1_i)
    ],
    name="P01_i",
    description="engine inlet {description}",
    latex="P_{01_i}"
)


# %%  Engine Inlet Pressure Ratio
PR_i = Symbol.inherit(
    PR,
    Piecewise(
        (1.0, M_i <= 1),
        (1.0 - 0.075*(M_i - 1.0) ** 1.35, M_i > 1),
    ),
    name="PR_i",
    description="{description} between engine inlet and compressor and/or fan",
    latex="PR_i"
)

# %% Engine Inlet Efficiency
eta_i = Symbol(
    "eta_i",
    PR_i,
    description="efficiency between engine inlet and compressor and/or fan",
    latex="\\eta_i"
)

# Compressor Inlet Conditions

# %% Compressor Inlet Stagnation Temperature
T02_i = Symbol.inherit(
    T02,
    T01_i,
    name="T02_i",
    description="engine inlet {description}",
    latex="T02_i"
)

# %% Compressor Inlet Stagnation Pressure
P02_i = Symbol.inherit(
    P02,
    PR_i * P01_i,
    name="P02_i",
    description="engine inlet {description}",
    latex="P02_i"
)


# %% Documentation
documentation = Documentation(
    DOC_NAME,
    [
        Section.from_symbol(
            PR_i,
            "Inlet Pressure Ratio",
            args=[M_i],
            # citation=CUMPSTY_2003_BOOK.citation(210),
            show_in_documentation=True
        ),
        Section.from_data_object(
            DataObject(
                "InletThermodynamics",
                attributes=[gamma_i, Cp_i, M_i, eta_i, PR_i,
                            P1_i, P02_i, T1_i, T01_i, P01_i, T02_i]
            ),
            "Inlet Thermodynamics",
            args=[gamma_i, Rs, u_i, T1_i, P1_i],
            show_in_documentation=True
        )
    ]
)
