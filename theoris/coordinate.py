from pint import Quantity
from theoris.utils.sympy import LatexPrinter
from theoris.symbol import Symbol, Section
from sympy import Matrix


class Coordinate(Matrix):
    def __new__(cls, name: str, ref: Matrix, section: Section = None, description: str = None, latex: str = None, units: Quantity = None, statement_operation: str = None):
        latex = latex if latex is not None else name
        description = description if description is not None else name

        x = Symbol(
            "{name}_x".format(name=name),
            ref[0],
            section=section,
            description="x-coordinate of {description}".format(
                description=description),
            latex="{{{latex}}}_x".format(
                latex=latex if latex is not None else name),
            units=units
        )
        y = Symbol(
            "{name}_y".format(name=name),
            ref[1],
            section=section,
            description="y-coordinate of {description}".format(
                description=description),
            latex="{{{latex}}}_y".format(
                latex=latex if latex is not None else name),
            units=units
        )
        obj = Matrix.__new__(cls, [[x], [y]])
        obj.x = x
        obj.y = y
        return obj

    def __init__(self, name: str, ref: Matrix, section: Section = None, description: str = None, latex: str = None, units: Quantity = None, statement_operation: str = None):

        self.name = name
        self.ref = ref
        self.section = section
        self.units = units
        self.description = description if description is not None else ""
        self.latex = latex if latex is not None else name
        self.x = self[0]
        self.y = self[1]
        if self.section is not None:
            self.section.add_statement(self.x)
            self.section.add_statement(self.y)

    def _repr_latex_(self):
        if self.ref is not None:
            latex_ref_str = LatexPrinter().doprint(self.ref)
            return "${0} = {1}$".format(self.latex, latex_ref_str)
        else:
            return "${0}$".format(self.latex)
