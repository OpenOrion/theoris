# %% Imports
from sympy import sqrt
from theoris.utils.units import ureg
from theoris import Section, Symbol, Documentation
from theoris.citation import Website
from examples.thermodynamics import gamma, T, P, u, P0, T0

DOC_NAME = "Fluid Mechanics"

# %% Citation
NASA_GCR_WEBSITE = Website(
    title="NASA",
    base_url="https://www.grc.nasa.gov/",
)
CORRECTED_AIRFLOW_PER_AREA_CITATION = NASA_GCR_WEBSITE.citation(
    "Corrected Airflow per Area", "www/k-12/airplane/wcora.html"
)
VISCOSITY_CITATION = NASA_GCR_WEBSITE.citation(
    "Viscosity", "www/BGH/viscosity.html"
)

# %% Symbols
Rs, gamma_g, N, l, A = [
    Symbol(
        "Rs",
        description="specific gas constant",
        latex="R_s",
        units=ureg.J / (ureg.kg * ureg.K)
    ),
    Symbol(
        "gamma_g",
        description="gas ratio of specific heats",
        latex="\\gamma",
        units=ureg.dimensionless
    ),
    Symbol(
        "N",
        description="rotational speed",
        units=ureg.rpm
    ),
    Symbol(
        "l",
        description="characteristic length of problem",
        units=ureg.m,
    ),
    Symbol(
        "A",
        description="annulus flow area",
        units=ureg.m ** 2,
    )
]

# Gas Specific Heat at Constant Pressure
Cpg = Symbol(
    "Cpg",
    gamma_g * Rs / (gamma_g - 1),
    description="gas specific heat at constant pressure",
    latex="C_{p_g}",
    units=ureg.J / (ureg.kg * ureg.K)
)

# %% Constants
T0_ref, P0_ref, mu_ref = [
    Symbol(
        "T_ref",
        288.15,
        description="reference temperature at sea level",
        latex="T0_{ref}",
        units=ureg.K
    ),
    Symbol(
        "P0_ref",
        101325,
        description="reference pressure at sea level",
        latex="P0_{ref}",
        units=ureg.Pa
    ),
    Symbol(
        "mu_ref",
        1.73E-5,
        description="reference dynamic viscocity at sea level",
        latex="\\mu_{ref}",
        units=(ureg.N*ureg.s)/ureg.m**2
    ),
]

# %% Density
rho = Symbol(
    "rho",
    P / (Rs * T),
    description="fluid density",
    latex="\\rho",
    units=ureg.kg/ureg.m**3,
)

# %% Sonic Velocity
a = Symbol(
    "a",
    sqrt(gamma * Rs * T),
    description="speed of sound in medium",
    latex="a",
    units=ureg.m/ureg.s,
)

# %% Mach Number
M = Symbol(
    "M",
    u / a,
    description="mach number",
    units=ureg.dimensionless
)

# %% Dynamic Viscocity
C = Symbol(
    "C",
    110.4,
    description="sutherland constant",
    units=ureg.K,
)

mu = Symbol(
    "mu",
    mu_ref * ((T / T0_ref)**1.5) * ((T0_ref + C) / (T + C)),
    description="dynamic velocity using Sutherland's formula",
    latex="\\mu",
    units=(ureg.N*ureg.s)/ureg.m**2,
)

# %% Reynold's Number
Re = Symbol(
    "Re",
    rho * u * (l / mu),
    description="flow Reynold's number",
    units=ureg.dimensionless,
)

# %% Mass Flow Rate
# TODO: get to the bottom of these units later
mdot = Symbol(
    "mdot",
    ((A * P0) / sqrt(T0)),
    description="mass flow rate",
    latex="\\dot{m}",
    units=ureg.kg/ureg.s,
    has_forced_unit_conversion=True
)

# %% Corrected Mass Flow Rate
corr_compressible_air_const = Symbol(
    "corr_compressible_air_const",
    sqrt(gamma/Rs) * M * (1 + ((gamma - 1) / 2)
                          * M**2)**-((gamma+1)/(2*(gamma-1))),
    description="corrected compressible mass flow rate constant",
    latex="(corr \\ air \\ const)",
    units=ureg.dimensionless,
    has_forced_unit_conversion=True
)

mdot_corr_compressible = Symbol(
    "mdot_corr_compressible",
    mdot * corr_compressible_air_const,
    description="corrected compressible mass flow rate",
    latex="\\dot{m}_{corr_{compressible}}",
    units=ureg.kg/ureg.s
)

mdot_corr = Symbol(
    "mdot_corr",
    mdot * sqrt(T0/T0_ref)/sqrt(P0/P0_ref),
    description="corrected mass flow rate",
    latex="\\dot{m}_{corr}",
    units=ureg.kg/ureg.s
)

# %% Corrected Shaft Speed
N_corr = Symbol(
    "N_corr",
    N / sqrt(T0 / T0_ref),
    description="corrected shaft speed",
    latex="N_{corr}",
    units=ureg.rpm
)


# %% Annulus Area
A.set_expression(
    mdot / (rho*u),
)


# %% Documentation
documentation = Documentation(
    DOC_NAME,
    [
        Section.from_symbol(
            Cpg,
            "Gas Specific Heat at Constant Pressure",
            args=[gamma_g, Rs],
            show_in_documentation=True
        ),

        Section.from_symbol(
            rho,
            "Fluid Density",
            args=[P, T, Rs],
            show_in_documentation=True
        ),
        Section.from_symbol(
            a,
            "Sonic Velocity",
            args=[T, gamma, Rs],
            show_in_documentation=True
        ),
        Section.from_symbol(
            M,
            "Mach Number",
            args=[u, T, gamma, Rs],
            show_in_documentation=True
        ),
        Section.from_symbol(
            mu,
            "Dynamic Velocity",
            args=[T],
            citation=VISCOSITY_CITATION,
            show_in_documentation=True
        ),
        Section.from_symbol(
            Re,
            "Reynold Number",
            args=[u, l, rho, T],
            show_in_documentation=True
        ),
        Section.from_symbol(
            mdot,
            "Mass Flow Rate",
            args=[A, P0, T0],
            show_in_documentation=True
        ),
        Section.from_symbol(
            mdot_corr_compressible,
            "Corrected Compressible Mass Flow Rate",
            args=[A, P0, T0, M, gamma, Rs],
            citation=CORRECTED_AIRFLOW_PER_AREA_CITATION,
            show_in_documentation=True
        ),
        Section.from_symbol(
            mdot_corr,
            "Corrected Mass Flow Rate",
            args=[mdot, P0, T0],
            citation=CORRECTED_AIRFLOW_PER_AREA_CITATION,
            show_in_documentation=True
        ),
        Section.from_symbol(
            N_corr,
            "Corrected Shaft Speed",
            args=[N, T0],
            show_in_documentation=True
        ),
        Section.from_symbol(
            A,
            "Annulus Area",
            args=[mdot, u, rho],
            show_in_documentation=True
        ),
    ]
)