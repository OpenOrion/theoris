from theoris import BaseSymbol, DocObject


class DataObject(DocObject):

    def __init__(self, name: str, attributes: list[BaseSymbol], description: str = None) -> None:
        self.name = name
        self.attributes = attributes
        self.description = description
