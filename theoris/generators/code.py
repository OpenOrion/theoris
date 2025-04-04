from pathlib import Path
from typing import Union
from theoris.data_object import DataObject
from theoris.extensions.external_function import ExternalFunctionSymbol
from theoris.base_symbol import SymbolCodeCtx
from theoris import Symbol, Documentation, BaseSymbol, Section
from theoris.utils.symbols import get_code_name, is_symbol_constant
from theoris.utils.logging import logger

# String constants
newline = "\n"
comma = ","
comma_space = ", "
empty_str = ""


class CodeGenerator:
    def __init__(self,
                 package_path: Path | str,
                 header: str = None,
                 indent: str = " " * 4,
                 func_start_name: str = "calc") -> None:
        self.package_path = Path(package_path)
        self.header = header
        self.indent = indent
        self.func_start_name = func_start_name
        self.ctx = SymbolCodeCtx(func_start_name)

    def get_import_str(self, module_namespace: str, imports: list[str]):
        import_objects_str = comma_space.join(imports)
        return f"from {module_namespace} import {import_objects_str}"

    def get_imports_str(self, module_imports: dict[str, set]):
        return newline.join(
            [
                self.get_import_str(
                    module_namespace, module_imports[module_namespace])
                for module_namespace in module_imports
            ]
        )

    def get_instantiation_str(self, name: str, args: list[BaseSymbol]):
        # Use named parameters for BaseModel instantiation (param=value)
        # Add newlines and indent for readability when there are multiple arguments
        arg_strings = [f"{arg.name}={arg.name}" for arg in args]
        if len(arg_strings) <= 2:
            # For 1-2 args, keep them on the same line
            arg_names = comma_space.join(arg_strings)
            return f"{name}({arg_names})"
        else:
            # For 3+ args, put each on its own line with double indentation for parameters
            param_indent = self.indent * 2  # Double indent for parameters
            arg_lines = [param_indent + arg for arg in arg_strings]
            args_str = f",\n".join(arg_lines)
            # Single indent for closing paren
            return f"{name}(\n{args_str}\n{self.indent})"

    def get_class_name_str(self, class_name: str):
        return (
            f"class {class_name}(BaseModel):"
        )

    def get_class_attribute_str(self, attribute: BaseSymbol):
        type_str = attribute.type_hint
        # Include unit information in the description
        description = f"{attribute.description} ({attribute.units_str})"
        return f"{attribute.name}: {type_str} = Field(description=\"{description}\")"


    def get_parameter_str(self, parameter: BaseSymbol):
        return (
            "{name}: {_type}"
            .format(name=parameter.name, _type=parameter.type_hint)
        )

    def get_units_param_str(self, returns: BaseSymbol):
        return f"units = \"{returns.units_str}\""

    def get_parameters_str(self, args: list[BaseSymbol], returns: BaseSymbol = None):
        return_units_param = (
            [self.get_units_param_str(returns)] if returns and isinstance(returns, BaseSymbol)
            else []
        )

        return comma_space.join(
            [
                self.get_parameter_str(arg)
                for arg in args
            ] + return_units_param
        )

    # Pydantic models already have model_dump() method, so we don't need to_dict
    # They also have a good __str__ implementation

    def get_code_docs_str(self, args: list[BaseSymbol], description: str = None):
        return ("\n" + self.indent).join(
            [
                '"""' + (description if description else empty_str) + newline,
                "Parameters",
                "==========" + newline,
                ("\n" + self.indent).join(
                    [
                        ("\n" + self.indent).join(
                            [
                                self.get_parameter_str(arg),
                                f"{self.indent}{arg.description} ({arg.units_str})" +
                                newline,
                            ]
                        )
                        for arg in args
                    ]
                ),
                '"""'
            ]
        )

    def create_class_str(self, name: str, args: list[BaseSymbol], description=None):
        class_name_str = self.get_class_name_str(name)

        # For Pydantic models, we don't need a separate docstring as Field descriptions are used
        # But we'll add a class docstring if a description is provided
        class_docstring = f'    """{description}"""' if description else ""

        # For Pydantic models, fields should be at the same indentation level
        # Get each attribute string and ensure consistent indentation
        attributes = []
        for arg in args:
            attr_str = self.get_class_attribute_str(arg)
            attributes.append(attr_str)

        # Join with newlines and proper indentation
        class_attributes_str = "\n    ".join(attributes)

        # Pydantic models don't need __init__, to_dict, or __str__ methods
        if class_docstring:
            return f"{class_name_str}\n{class_docstring}\n    {class_attributes_str}"
        else:
            return f"{class_name_str}\n    {class_attributes_str}"

    def get_unit_validator_parameter_str(self, arg: BaseSymbol):
        return f"{arg.name}=\"{arg.units_str}\""

    def get_unit_validator_parameters_str(self, args: list[BaseSymbol]):
        return comma_space.join(
            [
                self.get_unit_validator_parameter_str(arg) for arg in args
            ]
        )

    def get_unit_validator_decorator_str(self, args: list[BaseSymbol], returns: Union[BaseSymbol, DataObject]):
        parameters_str = self.get_unit_validator_parameters_str(args)
        if isinstance(returns, BaseSymbol):
            return f"@validate_units({parameters_str}, returns=\"{returns.units_str}\")"
        else:
            return f"@validate_units({parameters_str})"

    def get_func_definition_str(self, name: str, args: list[BaseSymbol], func_start_name: str = None, include_self=False, returns: BaseSymbol = None):
        section_func_name = get_code_name(name, func_start_name)
        parameters_str = ("self" + comma if include_self else empty_str) + \
            self.get_parameters_str(args, returns)
        return f"def {section_func_name}({parameters_str}):"

    def get_statement_comment_str(self, statement: BaseSymbol):
        return f"# {statement.description} ({statement.units_str})"

    def get_inline_statement_str(self, statement: BaseSymbol):
        return statement._repr_code_(self.ctx)

    def get_reference_statement_code_str(self, statement: BaseSymbol):
        func_args = statement.section.args
        func_name = get_code_name(
            statement.section.name, self.func_start_name)
        func_instantiation = self.get_instantiation_str(
            func_name, func_args)
        return f"{statement.name} = {func_instantiation}"

    def get_statement_str(self, statement: BaseSymbol, section: Section = None):
        if section is None or statement.section is None or statement.section.name is section.name:
            return self.get_inline_statement_str(statement)
        else:
            return self.get_reference_statement_code_str(statement)

    def get_statement_with_operation_str(self, statement: BaseSymbol, section: Section):
        statement_code_str = self.get_statement_str(statement, section)
        statement_operation = statement.statement_operation
        return f"({statement_code_str}){statement_operation}"

    def get_func_statement_str(self, statement: BaseSymbol, section: Section):
        statement_comment_str = self.get_statement_comment_str(statement)
        statement_code_str = self.get_statement_str(statement, section)
        return ("\n" + self.indent).join(
            [
                statement_comment_str,
                statement_code_str
            ]
        )

    def get_func_return_str(self, section: Section):
        returns = section.returns
        return_object_str = None
        if isinstance(returns, DataObject):
            return_object_str = self.get_instantiation_str(
                returns.name, returns.attributes)
        elif isinstance(returns, Symbol) and (is_symbol_constant(returns) or returns.is_magnitude):
            return_object_str = f"{returns} * ureg.Quantity(1, \"{returns.units_str}\")"
        else:
            return_object_str = f"{returns}"

        return f"return {return_object_str}"

    def load_module_imports(self, section: Section, module_imports: dict[str, set]):
        for statement in section.statements:
            if statement.is_assigned():
                statement_module_section = statement.get_module_section()
                if statement_module_section is not None:
                    statement_documentation = statement_module_section.documentation
                    statement_documentation_namespace = self.get_documentation_namespace(
                        statement_documentation)

                    if (module_imports is not None and
                            statement_documentation.name is not section.documentation.name):
                        statement_func_name = get_code_name(
                            statement_module_section.name, self.func_start_name)
                        if statement_documentation_namespace not in module_imports:
                            module_imports[statement_documentation_namespace] = set(
                            )
                        module_imports[statement_documentation_namespace].add(
                            statement_func_name)

    def get_section_code_str(self, section: Section):
        func_elements = [
            newline.join(
                [
                    self.get_unit_validator_decorator_str(
                        section.args, section.returns),
                    self.get_func_definition_str(
                        section.name, section.args, self.func_start_name, returns=section.returns),
                ]
            ),
            self.get_code_docs_str(section.args, section.description)
        ]

        for statement in section.statements:
            if statement.is_assigned():
                func_elements.append(
                    self.get_func_statement_str(statement, section)
                )

        func_elements.append(
            self.get_func_return_str(section)
        )

        return ("\n\n" + self.indent).join(
            func_elements
        )

    def get_documentation_code_str(self, documentation: Documentation):
        module_imports:  dict[str, set] = dict()

        import_strings = [
            "import numpy as np",  # TODO: make this dynamically added
            "from theoris.utils.units import ureg, validate_units",
            "from pint import Quantity",
            "from pydantic import BaseModel, Field",
        ] + list(documentation.external_modules)

        root_import = newline.join(
            import_strings
        )
        code_objects = []

        if self.header is not None:
            code_objects.append(self.header)

        for code_object in documentation.exports:
            if isinstance(code_object, Section):
                if not isinstance(code_object.returns, ExternalFunctionSymbol):
                    for data_object in code_object.data_objects:
                        code_objects.append(
                            self.create_class_str(
                                data_object.name, data_object.attributes)
                        )
                    code_objects.append(
                        self.get_section_code_str(code_object)
                    )
                    self.load_module_imports(code_object, module_imports)

            elif isinstance(code_object, DataObject):
                code_objects.append(
                    self.create_class_str(
                        code_object.name, code_object.attributes)
                )
            elif isinstance(code_object, BaseSymbol):
                code_objects.append(
                    self.get_statement_str(code_object)
                )
        imports_str = self.get_imports_str(module_imports)
        return ("\n" * 2).join(
            [

                newline.join(
                    [root_import, imports_str]
                ),
                *code_objects
            ],
        )

    def get_generated_file_path(self, documentation: Documentation):
        # Use the package_path instead of documentation.file_path
        # This ensures the lib directory is in the same parent directory as the doc directory
        lib_dir = self.package_path / "lib"

        # Create subdirectory based on documentation name
        # Replace spaces with slashes to create proper subdirectory structure
        # Example: "Compressor Thermodynamics" -> "compressor/thermodynamics.py"
        doc_name = documentation.name

        # Convert to lowercase and replace spaces with slashes
        # subdirectory_path = doc_name.lower().replace(" ", "/")

        # Split the path to get the directory and filename parts
        path_parts = [get_code_name(part)
                      for part in doc_name.lower().split("/")]

        if len(path_parts) > 1:
            # Create subdirectories
            # All parts except the last one
            subdirectory = "/".join(path_parts[:-1])
            component_dir = lib_dir / subdirectory
            component_dir.mkdir(parents=True, exist_ok=True)

            # Use the last part as the filename
            filename = path_parts[-1] + ".py"
            generated_path = component_dir / filename
        else:
            # If there's only one part, use it as the filename
            filename = path_parts[0] + ".py"
            generated_path = lib_dir / filename

        return Path(generated_path).resolve()

    def get_documentation_namespace(self, documentation: Documentation):
        doc_path = self.get_generated_file_path(documentation)
        package_relative_path = Path(f"{doc_path}".replace(
            f"{self.package_path}", self.package_path.stem))

        # Convert the path to a namespace
        # This will include the subdirectory structure in the namespace
        # Example: jetengine/lib/compressor/thermodynamics.py -> jetengine.lib.compressor.thermodynamics
        namespace = ".".join(
            package_relative_path.parts).replace(".py", empty_str)

        return namespace

    def generate_code(self, documentation: Documentation):
        generated_file_path = self.get_generated_file_path(documentation)
        generated_directory_path = generated_file_path.parent
        generated_directory_path.mkdir(parents=True, exist_ok=True)
        documentation_code_str = self.get_documentation_code_str(documentation)
        with open(generated_file_path, "+w", encoding="utf-8") as f:
            f.write(documentation_code_str)
        logger.info(f"Finished writing to {generated_file_path}")
