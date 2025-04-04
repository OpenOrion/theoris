from typing import Union, List, Dict, Any, Optional
import inspect
from theoris.utils.ordered_set import OrderedSet
from theoris.citation import Citation
from theoris.base_symbol import BaseSymbol
from theoris.data_object import DataObject
from theoris.doc_object import DocObject

# Import verification components if available
try:
    from theoris.verification.constraints import (
        Constraint,
        PropertyConstraint,
        EquivalenceConstraint,
        ImplicationConstraint,
        ProofResult
    )
    from theoris.verification.pysmt_interface import SymbolicExpression
    VERIFICATION_AVAILABLE = True
except ImportError:
    VERIFICATION_AVAILABLE = False


class SymbolMapping:
    """
    Maps one symbol to another for use in Section arguments.

    This class represents a mapping between two symbols, typically used
    when a symbol needs to be renamed or reinterpreted within a section.

    Attributes:
        from_symbol: The source symbol.
        to_symbol: The target symbol.
    """

    def __init__(self, from_symbol: BaseSymbol, to_symbol: BaseSymbol) -> None:
        """
        Initialize a SymbolMapping between two symbols.

        Args:
            from_symbol: The source symbol.
            to_symbol: The target symbol.
        """
        self.from_symbol = from_symbol
        self.to_symbol = to_symbol


class Section(DocObject):
    """
    Represents a section of code with arguments, statements, and a return value.

    A Section organizes symbols into a logical unit, similar to a function or method.
    It tracks input arguments, internal statements, and an optional return value.
    Sections can be used to generate code and documentation, and can also include
    verification capabilities for proving mathematical properties.

    Attributes:
        name: The name of the section.
        description: Human-readable description of what the section does.
        statements: OrderedSet of ISymbol objects representing the statements in this section.
        returns: The symbol or data object returned by this section, if any.
        args: OrderedSet of symbols or symbol mappings representing the inputs to this section.
        data_objects: List of data objects used in this section.
        citation: Optional citation for the source of the code or algorithm.
        show_in_documentation: Whether this section should be included in generated documentation.
        assumptions: List of assumptions for this section (if verification is available).
        theorems: List of theorems for this section (if verification is available).
        proof_results: Dictionary mapping theorem descriptions to proof results (if verification is available).
    """

    def __init__(self,
                 name: str,
                 args: list[Union[BaseSymbol, SymbolMapping]] = None,
                 description: str = None,
                 statements: list[BaseSymbol] = None,
                 documentation_name: str = None,
                 citation: Citation = None,
                 show_in_documentation: bool = False
                 ) -> None:
        """
        Initialize a Section with the given attributes.

        Args:
            name: The name of the section.
            args: Optional list of input symbols or symbol mappings.
            description: Optional human-readable description of what the section does.
            statements: Optional list of symbols representing statements in this section.
            documentation_name: Optional name of the Documentation object this section belongs to.
            citation: Optional citation for the source of the code or algorithm.
            show_in_documentation: Whether this section should be included in generated documentation.
                                  Defaults to False.
        """
        super().__init__(documentation_name)
        self.name = name
        self.description = description
        self.statements: OrderedSet[BaseSymbol] = OrderedSet()
        self.returns = None
        # Initialize args with the provided args first
        self.args = OrderedSet([] if args is None else args)
        # Add statements after args are initialized
        self.add_statements(statements)
        # Now update args with any inferred from statements
        self.args = self.get_args(args)

        self.data_objects: list[Union[BaseSymbol, DataObject]] = []
        self.citation = citation
        self.show_in_documentation = show_in_documentation

        # Initialize verification attributes if verification is available
        if VERIFICATION_AVAILABLE:
            self.assumptions: List[Constraint] = []
            self.theorems: List[Constraint] = []
            self.proof_results: Dict[str, ProofResult] = {}

    def get_args(self, args: list[Union[BaseSymbol, SymbolMapping]] = None) -> OrderedSet[Union[BaseSymbol, SymbolMapping]]:
        """
        Get the arguments for this section.

        This method processes the provided arguments and combines them with any
        arguments inferred from the statements in this section. It filters out
        any arguments that are also statements in this section.

        Args:
            args: Optional list of input symbols or symbol mappings.

        Returns:
            OrderedSet of symbols or symbol mappings representing the inputs to this section.
        """
        symbol_args = OrderedSet()
        for arg in [] if args is None else args:
            if isinstance(arg, BaseSymbol):
                symbol_args.add(arg)
        
        # Only try to get statement args if we have statements
        statement_args = OrderedSet()
        if self.statements:
            statement_args = self.get_statement_args()
        
        return (
            symbol_args
            .union(
                statement_args
                .difference(
                    self.statements
                )
            )
        )

    def add_statements(self, statements: list[BaseSymbol] = None):
        """
        Add multiple statements to this section.

        This method adds the given statements to this section, handling dependencies
        and determining whether each statement should be treated as an argument or
        a statement. It recursively adds any dependencies of the statements.

        Args:
            statements: Optional list of symbols to add as statements.
                       If None, an empty list is used.
        """
        statements = [] if statements is None else statements
        for statement in statements:
            if statement.is_assigned() and statement not in self.args:
                # Find dependencies of this statement that aren't already in the section
                statement_deps = list(
                    filter(
                        lambda statement_dep: not statement_dep.is_global,
                        (
                            statement.get_dependencies()
                            .difference(self.statements)
                            .difference(self.args)
                        )
                    )
                )

                # Recursively add dependencies unless this is a return value from another section
                if not (statement.section and statement.section.returns == statement):
                    self.add_statements(statement_deps)

                # Add the statement and set it as the return value
                self.statements.add(statement)
                self.set_return(statement)
            else:
                # If the statement isn't assigned or is already an argument,
                # add it as an argument instead
                self.args.add(statement)

    def add_statement(self, statement: BaseSymbol):
        """
        Add a single statement to this section.

        This is a convenience method that calls add_statements with a single-item list.

        Args:
            statement: The symbol to add as a statement.
        """
        self.add_statements([statement])

    def get_statement_args(self):
        """
        Get arguments inferred from statements in this section.

        This method identifies symbols that are used as return values from other sections
        and collects their arguments as potential arguments for this section.

        Returns:
            Set of symbols that should be considered arguments for this section.
        """
        args = set()
        for statement in self.statements:
            # If this statement is assigned, comes from another section,
            # and is the return value of that section
            if (statement.is_assigned() and
                statement.section is not None and
                statement.section.name is not self.name and
                    statement.section.returns is statement):

                # Add the arguments of that section to our arguments
                statement_args = set(statement.section.args)
                args = args.union(statement_args)
        return args

    def set_return(self, returns: Union[BaseSymbol, DataObject]):
        """
        Set the return value for this section.

        This method sets the given symbol or data object as the return value
        for this section and updates the description accordingly.

        Args:
            returns: The symbol or data object to set as the return value.
        """
        self.returns = returns
        if isinstance(returns, DataObject):
            self.data_objects.append(returns)
        self.description = "calculates {description}".format(
            description=self.returns.description or ""
        )

    @staticmethod
    def from_symbol(symbol: BaseSymbol,
                    name: str = None,
                    args: list[BaseSymbol] = None,
                    statements: list[BaseSymbol] = None,
                    documentation_name: str = None,
                    citation: Citation = None,
                    show_in_documentation=False):
        """
        Create a Section from a symbol.

        This static method creates a new Section with the given symbol as its
        primary statement. The symbol is also set as the return value of the section.

        Args:
            symbol: The symbol to create a section for.
            name: Optional name for the section. If None, the symbol's name is used.
            args: Optional list of input symbols.
            statements: Optional list of additional statements to include.
            documentation_name: Optional name of the Documentation object this section belongs to.
            citation: Optional citation for the source of the code or algorithm.
            show_in_documentation: Whether this section should be included in generated documentation.
                                  Defaults to False.

        Returns:
            A new Section object with the given symbol as its primary statement.
        """
        section = Section(
            name or symbol.name,
            args=args,
            statements=([] if statements is None else statements) + [symbol],
            documentation_name=documentation_name,
            citation=citation,
            show_in_documentation=show_in_documentation
        )
        symbol.set_section(section)
        return section

    @staticmethod
    def from_data_object(data_object: DataObject,
                         name: str = None,
                         args: list[BaseSymbol] = None,
                         statements: list[BaseSymbol] = None,
                         show_in_documentation=False):
        """
        Create a Section from a data object.

        This static method creates a new Section with the given data object as its
        return value. The data object's attributes are added as statements.

        Args:
            data_object: The data object to create a section for.
            name: Optional name for the section. If None, the data object's name is used.
            args: Optional list of input symbols.
            statements: Optional list of additional statements to include.
            show_in_documentation: Whether this section should be included in generated documentation.
                                  Defaults to False.

        Returns:
            A new Section object with the given data object as its return value.
        """
        section = Section(
            name or data_object.name,
            args=args,
            statements=([] if statements is None else statements) +
            data_object.attributes,
            show_in_documentation=show_in_documentation
        )
        section.set_return(data_object)
        return section

    def __repr__(self) -> str:
        """
        Generate a string representation of the section including a diagram.
        
        Returns:
            A string representation of the section.
        """
        from theoris.diagram_generator import generate_diagram
        
        # Create block representation for this section
        block = {
            'name': self.name,
            'inputs': [arg.name if hasattr(arg, 'name') else str(arg) for arg in self.args],
            'outputs': [self.returns.name if hasattr(self.returns, 'name') else str(self.returns)] if self.returns else []
        }
        
        # Generate diagram
        generate_diagram([block])
        
        # Create text representation
        repr_text = f"Section: {self.name}\n"
        if self.description:
            repr_text += f"Description: {self.description}\n"
        repr_text += f"Arguments: {', '.join(block['inputs'])}\n"
        if self.returns:
            repr_text += f"Returns: {block['outputs'][0]}\n"
        if self.statements:
            repr_text += f"Statements: {len(self.statements)}\n"
        
        return repr_text

    # Verification methods - only available if verification components are imported
    if VERIFICATION_AVAILABLE:
        def add_assumption(self,
                           assumption_expr: SymbolicExpression,
                           description: str = "") -> Constraint:
            """
            Add an assumption to this section.

            Args:
                assumption_expr: The symbolic expression representing the assumption.
                description: Human-readable description of the assumption.

            Returns:
                The created Constraint object.
            """
            assumption = Constraint(
                expression=assumption_expr,
                description=description or f"Assumption in {self.name}",
            )
            self.assumptions.append(assumption)
            return assumption

        def add_theorem(self,
                        theorem_expr: SymbolicExpression,
                        description: str = "") -> Constraint:
            """
            Add a theorem to this section.

            Args:
                theorem_expr: The symbolic expression representing the theorem.
                description: Human-readable description of the theorem.

            Returns:
                The created Constraint object.
            """
            theorem = Constraint(
                expression=theorem_expr,
                description=description or f"Theorem in {self.name}",
                assumptions=[
                    assumption.expression for assumption in self.assumptions]
            )
            self.theorems.append(theorem)
            return theorem

        def add_implication_theorem(self,
                                    antecedent: SymbolicExpression,
                                    consequent: SymbolicExpression,
                                    description: str = "") -> ImplicationConstraint:
            """
            Add an implication theorem to this section.

            Args:
                antecedent: The antecedent property.
                consequent: The consequent property.
                description: Human-readable description of the theorem.

            Returns:
                The created ImplicationConstraint object.
            """
            theorem = ImplicationConstraint(
                antecedent=antecedent,
                consequent=consequent,
                description=description or f"Implication in {self.name}",
                assumptions=[
                    assumption.expression for assumption in self.assumptions]
            )
            self.theorems.append(theorem)
            return theorem

        def add_equivalence_theorem(self,
                                    expr1: SymbolicExpression,
                                    expr2: SymbolicExpression,
                                    description: str = "") -> EquivalenceConstraint:
            """
            Add an equivalence theorem to this section.

            Args:
                expr1: The first expression.
                expr2: The second expression.
                description: Human-readable description of the theorem.

            Returns:
                The created EquivalenceConstraint object.
            """
            theorem = EquivalenceConstraint(
                expr1=expr1,
                expr2=expr2,
                description=description or f"Equivalence in {self.name}",
                assumptions=[
                    assumption.expression for assumption in self.assumptions]
            )
            self.theorems.append(theorem)
            return theorem

        def verify_theorems(self) -> Dict[str, ProofResult]:
            """
            Verify all theorems in this section.

            Returns:
                Dictionary mapping theorem descriptions to proof results.
            """
            results = {}

            for theorem in self.theorems:
                result = theorem.verify()
                results[theorem.description] = result

            self.proof_results = results
            return results

        def get_proof_results(self) -> Dict[str, ProofResult]:
            """
            Get the proof results for this section.

            Returns:
                Dictionary mapping theorem descriptions to proof results.
            """
            return self.proof_results

        def __repr__(self) -> str:
            """
            Generate a string representation of the section including a diagram.
            
            Returns:
                A string representation of the section.
            """
            from theoris.diagram_generator import generate_diagram
            
            # Create block representation for this section
            block = {
                'name': self.name,
                'inputs': [arg.name if hasattr(arg, 'name') else str(arg) for arg in self.args],
                'outputs': [self.returns.name if hasattr(self.returns, 'name') else str(self.returns)] if self.returns else []
            }
            
            # Generate diagram
            generate_diagram([block])
            
            # Create text representation
            repr_text = f"Section: {self.name}\n"
            if self.description:
                repr_text += f"Description: {self.description}\n"
            repr_text += f"Arguments: {', '.join(block['inputs'])}\n"
            if self.returns:
                repr_text += f"Returns: {block['outputs'][0]}\n"
            if self.statements:
                repr_text += f"Statements: {len(self.statements)}\n"
            
            return repr_text

        def get_proof_summary(self) -> str:
            """
            Get a summary of the proof results for this section.

            Returns:
                String containing a summary of the proof results.
            """
            if not self.proof_results:
                return f"No proofs have been run for section {self.name}."

            summary = f"Proof results for section {self.name}:\n"

            # List assumptions
            if self.assumptions:
                summary += "\nAssumptions:\n"
                for i, assumption in enumerate(self.assumptions):
                    summary += f"  {i+1}. {assumption.description}\n"

            # List theorems and their results
            summary += "\nTheorems:\n"
            for i, (description, result) in enumerate(self.proof_results.items()):
                status = "SATISFIED" if result.is_satisfied else "VIOLATED"
                summary += f"  {i+1}. {description}: {status} ({result.proof_time:.3f}s)\n"
                if not result.is_satisfied and result.counterexample:
                    summary += "     Counterexample:\n"
                    for symbol, value in result.counterexample.items():
                        summary += f"       {symbol} = {value}\n"

            return summary

        def generate_proof_documentation(self) -> str:
            """
            Generate documentation for the proofs in this section.

            Returns:
                String containing LaTeX documentation for the proofs.
            """
            if not self.proof_results:
                return f"No proofs have been run for section {self.name}."

            doc = f"\\section{{Proofs for {self.name}}}\n\n"

            # List assumptions
            if self.assumptions:
                doc += "\\subsection{Assumptions}\n\n"
                doc += "\\begin{enumerate}\n"
                for assumption in self.assumptions:
                    doc += f"\\item {assumption.description}\n"
                doc += "\\end{enumerate}\n\n"

            # List theorems and their results
            doc += "\\subsection{Theorems}\n\n"
            doc += "\\begin{enumerate}\n"
            for description, result in self.proof_results.items():
                status = "Proved" if result.is_satisfied else "Disproved"
                doc += f"\\item {description}: {status} ({result.proof_time:.3f}s)\n"
                if not result.is_satisfied and result.counterexample:
                    doc += "\\begin{itemize}\n"
                    doc += "\\item Counterexample:\n"
                    doc += "\\begin{align}\n"
                    for symbol, value in result.counterexample.items():
                        doc += f"{symbol} &= {value} \\\\\n"
                    doc += "\\end{align}\n"
                    doc += "\\end{itemize}\n"
            doc += "\\end{enumerate}\n"

            return doc
