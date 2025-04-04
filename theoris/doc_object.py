from typing import Any


class DocObject:
    """
    Base class for objects that can be documented.

    DocObject serves as a base class for elements that can be included in a Documentation
    object, such as Sections and ISymbols. It maintains a reference to its parent
    Documentation object, creating a bidirectional relationship where Documentation
    contains DocObjects and DocObjects reference their Documentation.

    Attributes:
        documentation: Reference to the Documentation object this object belongs to.
                      Imported as Any to avoid circular imports.
    """
    # from theoris.documentation import Documentation
    documentation: Any

    def __init__(self, documentation: Any):
        """
        Initialize a DocObject with a reference to its Documentation.

        Args:
            documentation: The Documentation object this DocObject belongs to.
                          Can be None initially and set later.
        """
        self.documentation = documentation

    def set_documentation(self, documentation: Any):
        """
        Update the Documentation reference for this object.

        This method is called by the Documentation class when this object
        is added to its exports list.

        Args:
            documentation: The Documentation object this DocObject belongs to.
        """
        self.documentation = documentation
