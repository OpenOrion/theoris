from theoris.doc_object import DocObject
from theoris.base_symbol import BaseSymbol
from theoris.section import Section
from theoris.utils.ordered_set import OrderedSet


class Documentation:
    """
    Manages a collection of documented objects (DocObjects).

    The Documentation class serves as a container for DocObjects such as Sections
    and ISymbols. It establishes bidirectional relationships with its contained
    objects and tracks external module dependencies.

    Attributes:
        name: The name of this documentation collection.
        file_path: The path to the file where this Documentation was created.
        exports: List of DocObjects contained in this Documentation.
        external_modules: Set of external module names required by the contained objects.
        directory: Directory where documentation output will be stored.
    """
    directory: str

    def __init__(
        self,
            name: str,
            exports: list[DocObject] = None
    ) -> None:
        """
        Initialize a Documentation object.

        Args:
            name: The name of this documentation collection.
            exports: Optional list of DocObjects to include in this Documentation.
                    If None, an empty list is used.
            file_path: Optional path to the file where this Documentation is defined.
                      If None, it will be determined automatically using traceback.

        Raises:
            ValueError: If any non-global ISymbol is included in exports.
        """
        self.name = name
        self.exports: list[DocObject] = [] if exports is None else exports
        self.external_modules: OrderedSet[str] = OrderedSet()

        # Set up bidirectional relationships and collect external modules
        for export in self.exports:
            export.set_documentation(self)

            if isinstance(export, Section):
                # Initialize all arguments and statements in the section
                # and collect their external module dependencies
                for arg in export.args:
                    arg.initialize()
                    self.external_modules = self.external_modules.union(
                        arg.external_modules)
                for statement in export.statements:
                    statement.initialize()
                    self.external_modules = self.external_modules.union(
                        statement.external_modules)

            if isinstance(export, BaseSymbol):
                # Only global symbols are allowed at the top level
                if not export.is_global:
                    raise ValueError(
                        "Only global symbols allowed in Documentation top-level")
                    
    def __repr__(self) -> str:
        """
        Generate a string representation of the documentation.
        
        Returns:
            A string representation showing the documentation structure.
        """
        repr_text = f"Documentation: {self.name}\n"
        
        # Show exports
        if self.exports:
            repr_text += "\nExports:\n"
            for export in self.exports:
                if isinstance(export, Section):
                    repr_text += f"  Section: {export.name}\n"
                    if export.description:
                        repr_text += f"    Description: {export.description}\n"
                    repr_text += f"    Arguments: {len(export.args)}\n"
                    repr_text += f"    Statements: {len(export.statements)}\n"
                    if export.returns:
                        repr_text += f"    Returns: {export.returns.name if hasattr(export.returns, 'name') else str(export.returns)}\n"
                elif isinstance(export, BaseSymbol):
                    repr_text += f"  Symbol: {export.name}\n"
                    if export.description:
                        repr_text += f"    Description: {export.description}\n"
                    if hasattr(export, 'units') and export.units:
                        repr_text += f"    Units: {export.units}\n"
                else:
                    repr_text += f"  {type(export).__name__}: {export}\n"
        
        # Show external module dependencies
        if self.external_modules:
            repr_text += "\nExternal Dependencies:\n"
            for module in self.external_modules:
                repr_text += f"  {module}\n"
        
        return repr_text
