from pathlib import Path
from typing import Literal
from theoris import CodeGenerator, DocumentationGenerator, Documentation


def get_generate_function(documentation: Documentation):
    def generate(package_path: Path, generation_option: Literal["all", "code", "docs"]):
        package_path = Path(package_path)
        cgen = CodeGenerator(package_path)
        dgen = DocumentationGenerator(package_path)

        if (generation_option == "code" or generation_option == "all"):
            print(f"Generating code for {documentation.name}...")
            cgen.generate_code(documentation)
        if (generation_option == "docs" or generation_option == "all"):
            print(f"Generating documentation for {documentation.name}...")
            dgen.generate_documentation(documentation)

    return generate


def generate(documentation: Documentation, package_path: Path, generation_option: Literal["all", "code", "docs"]):
    generate_function = get_generate_function(documentation)
    generate_function(package_path, generation_option)
