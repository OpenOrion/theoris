import os
from pathlib import Path
import nbformat as nbf
import matplotlib.pyplot as plt
import networkx as nx
from theoris import Documentation, BaseSymbol
from theoris.section import Section
from theoris.symbol import Symbol
from theoris.utils.logging import logger

# String constants
newline = "\n"
empty_str = ""

TMP_DOCS_PATH = Path("/tmp/codegen/notebooks")
# Changed from "docs" to "doc" to match "lib" convention
DOCS_DEFAULT_DIRECTORY = "doc"


class DocumentationGenerator:

    def __init__(self, package_path: Path) -> None:
        self.package_path = package_path
        self.docs_path = DocumentationGenerator.get_docs_directory(
            package_path)

    def get_section_str(self, section: Section):
        section_statement = "<br/>".join(
            [
                f"{statement.latex_str} - {statement.description or empty_str} ({statement.units_str}) <br/>"
                for statement in section.statements
            ]
        )

        return newline.join(
            [
                f"## {section.name} <br/>",
                f"{section.description} <br/><br/>",
                section_statement
            ]
        )

    def get_nomenclature_str(self, symbols: list[Symbol]):
        return newline.join(
            ["## Nomencalture"] +
            [f"${symbol.latex}$ - {symbol.description} <br/>" for symbol in symbols]
        )

    def get_globals_str(self, symbols: list[Symbol]):
        return newline.join(
            ["## Globals"] +
            [f"{symbol.latex_str} - {symbol.description}<br/>" for symbol in symbols]
        )

    def generate_section_io_diagram(self, section: Section) -> str:
        """
        Generate a diagram visualizing the inputs and outputs of a section.

        Args:
            section: The section to generate a diagram for.

        Returns:
            The path to the generated diagram image, or None if generation failed.
        """
        try:
            # Create a directed graph
            G = nx.DiGraph()

            # Add a node for the section itself
            G.add_node("section", label=section.name, type="section")

            # Add nodes for inputs (arguments)
            for i, arg in enumerate(section.args):
                if isinstance(arg, BaseSymbol):
                    node_id = f"input_{i}"
                    label = arg.name
                    description = arg.description if hasattr(
                        arg, 'description') else ""
                    G.add_node(node_id, label=label,
                               description=description, type="input")
                    G.add_edge(node_id, "section")

            # Add a node for the output (return value)
            if section.returns:
                G.add_node("output", label=section.returns.name,
                           description=section.returns.description if hasattr(
                               section.returns, 'description') else "",
                           type="output")
                G.add_edge("section", "output")

            # Create the figure with a clean, white background
            plt.figure(figsize=(12, 6), facecolor='white')
            plt.title(
                f"Inputs and Outputs: {section.name}", fontsize=16, fontweight='bold')

            # Use a left-to-right layout
            pos = {}

            # Position inputs on the left
            input_nodes = [n for n, d in G.nodes(
                data=True) if d.get('type') == 'input']
            if input_nodes:
                input_y_step = 0.8 / (len(input_nodes) + 1)
                for i, node in enumerate(input_nodes):
                    pos[node] = (0.2, 0.1 + (i + 1) * input_y_step)

            # Position section in the middle
            pos["section"] = (0.5, 0.5)

            # Position output on the right
            if "output" in G:
                pos["output"] = (0.8, 0.5)

            # Draw input nodes
            nx.draw_networkx_nodes(G, pos, nodelist=input_nodes,
                                   node_color='#4285F4', node_size=2500,
                                   alpha=0.9, node_shape='o', edgecolors='#2C5AA0')

            # Draw section node
            nx.draw_networkx_nodes(G, pos, nodelist=["section"],
                                   node_color='#FBBC05', node_size=3500,
                                   alpha=0.9, node_shape='s', edgecolors='#E37400')

            # Draw output node if it exists
            if "output" in G:
                nx.draw_networkx_nodes(G, pos, nodelist=["output"],
                                       node_color='#34A853', node_size=2500,
                                       alpha=0.9, node_shape='o', edgecolors='#0F8C3B')

            # Draw edges
            nx.draw_networkx_edges(G, pos, width=2.0, alpha=0.7,
                                   edge_color='#5F6368', arrowsize=20,
                                   connectionstyle='arc3,rad=0.1')

            # Draw labels
            labels = {}
            for n, d in G.nodes(data=True):
                labels[n] = d.get('label', n)

            nx.draw_networkx_labels(G, pos, labels=labels,
                                    font_size=12, font_weight='bold',
                                    font_family='sans-serif')

            # Add descriptions as annotations
            for n, d in G.nodes(data=True):
                if d.get('description') and n in pos:
                    x, y = pos[n]
                    if d.get('type') == 'input':
                        plt.annotate(d.get('description'), xy=(x, y), xytext=(x-0.15, y),
                                     arrowprops=dict(
                                         arrowstyle='->', color='gray'),
                                     bbox=dict(boxstyle='round,pad=0.5',
                                               fc='#E8F0FE', ec='gray', alpha=0.8),
                                     fontsize=10, ha='right')
                    elif d.get('type') == 'output':
                        plt.annotate(d.get('description'), xy=(x, y), xytext=(x+0.15, y),
                                     arrowprops=dict(
                                         arrowstyle='->', color='gray'),
                                     bbox=dict(boxstyle='round,pad=0.5',
                                               fc='#E6F4EA', ec='gray', alpha=0.8),
                                     fontsize=10, ha='left')

            # Add a legend
            from matplotlib.lines import Line2D
            from matplotlib.patches import Patch
            legend_elements = [
                Line2D([0], [0], marker='o', color='w',
                       markerfacecolor='#4285F4', markersize=15, label='Input'),
                Patch(facecolor='#FBBC05', edgecolor='#E37400', label='Section'),
                Line2D([0], [0], marker='o', color='w',
                       markerfacecolor='#34A853', markersize=15, label='Output')
            ]
            plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                       ncol=3, fontsize=12)

            # Remove axis
            plt.axis('off')

            # Save the figure
            diagram_dir = Path(self.docs_path, "diagrams")
            diagram_dir.mkdir(parents=True, exist_ok=True)

            # Create a filename for the diagram
            diagram_filename = f"{section.name.lower().replace(' ', '_')}_io.png"
            diagram_path = diagram_dir / diagram_filename

            # Save the diagram
            plt.savefig(diagram_path, format="PNG",
                        dpi=150, bbox_inches='tight')
            plt.close()

            # Log the diagram creation
            logger.info(f"Generated I/O diagram at {diagram_path}")

            # Return the relative path to the diagram for inclusion in the notebook
            return f"diagrams/{diagram_filename}"
        except Exception as e:
            logger.warning(
                f"Failed to generate I/O diagram for section {section.name}: {e}")
            return None

    def generate_verification_diagram(self, section: Section) -> str:
        """
        Generate a diagram visualizing the verification relationships in a section.

        Args:
            section: The section to generate a diagram for.

        Returns:
            The path to the generated diagram image, or None if generation failed.
        """
        try:
            # Create a directed graph
            G = nx.DiGraph()

            # Add nodes for assumptions
            for i, assumption in enumerate(section.assumptions):
                node_id = f"A{i}"
                label = assumption.description or f"Assumption {i+1}"
                G.add_node(node_id, label=label, type="assumption")

            # Add nodes for theorems
            for i, theorem in enumerate(section.theorems):
                node_id = f"T{i}"
                label = theorem.description or f"Theorem {i+1}"
                status = "SATISFIED" if theorem.description in section.proof_results and section.proof_results[
                    theorem.description].is_satisfied else "VIOLATED"
                G.add_node(node_id, label=label, type="theorem", status=status)

                # Add edges from assumptions to theorems
                for j, assumption in enumerate(section.assumptions):
                    G.add_edge(f"A{j}", node_id)

            # Create the figure with a clean, white background
            plt.figure(figsize=(12, 8), facecolor='white')
            plt.title(
                f"Verification Diagram: {section.name}", fontsize=16, fontweight='bold')

            # Use a hierarchical layout for better structure
            # This places assumptions at the top and theorems at the bottom
            pos = {}

            # Position assumptions in a row at the top
            assumption_nodes = [n for n, d in G.nodes(
                data=True) if d.get('type') == 'assumption']
            theorem_nodes = [n for n, d in G.nodes(
                data=True) if d.get('type') == 'theorem']

            # Calculate positions
            if assumption_nodes:
                assumption_x_step = 1.0 / (len(assumption_nodes) + 1)
                for i, node in enumerate(assumption_nodes):
                    pos[node] = ((i + 1) * assumption_x_step, 0.8)

            if theorem_nodes:
                theorem_x_step = 1.0 / (len(theorem_nodes) + 1)
                for i, node in enumerate(theorem_nodes):
                    pos[node] = ((i + 1) * theorem_x_step, 0.2)

            # Draw assumption nodes with a professional blue color
            nx.draw_networkx_nodes(G, pos, nodelist=assumption_nodes,
                                   node_color='#4285F4', node_size=3000,
                                   alpha=0.9, node_shape='o', edgecolors='#2C5AA0')

            # Draw theorem nodes with different colors based on status
            satisfied_nodes = [n for n, d in G.nodes(data=True) if d.get(
                'type') == 'theorem' and d.get('status') == 'SATISFIED']
            violated_nodes = [n for n, d in G.nodes(data=True) if d.get(
                'type') == 'theorem' and d.get('status') == 'VIOLATED']

            # Use a professional green for satisfied theorems
            nx.draw_networkx_nodes(G, pos, nodelist=satisfied_nodes,
                                   node_color='#34A853', node_size=3000,
                                   alpha=0.9, node_shape='o', edgecolors='#0F8C3B')

            # Use a professional red for violated theorems
            nx.draw_networkx_nodes(G, pos, nodelist=violated_nodes,
                                   node_color='#EA4335', node_size=3000,
                                   alpha=0.9, node_shape='o', edgecolors='#C62828')

            # Draw edges with a cleaner style
            nx.draw_networkx_edges(G, pos, width=2.0, alpha=0.7,
                                   edge_color='#5F6368', arrowsize=20,
                                   connectionstyle='arc3,rad=0.1')

            # Draw labels with better formatting
            labels = {n: d.get('label') for n, d in G.nodes(data=True)}
            nx.draw_networkx_labels(G, pos, labels=labels,
                                    font_size=11, font_weight='bold',
                                    font_family='sans-serif')

            # Add a legend
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], marker='o', color='w',
                       markerfacecolor='#4285F4', markersize=15, label='Assumption'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='#34A853',
                       markersize=15, label='Satisfied Theorem'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='#EA4335',
                       markersize=15, label='Violated Theorem')
            ]
            plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                       ncol=3, fontsize=12)

            # Remove axis
            plt.axis('off')

            # Save the figure
            # Create diagrams directory in the docs path
            diagram_dir = Path(self.docs_path, "diagrams")
            diagram_dir.mkdir(parents=True, exist_ok=True)

            # Create a filename for the diagram
            diagram_filename = f"{section.name.lower().replace(' ', '_')}_verification.png"
            diagram_path = diagram_dir / diagram_filename

            # Save the diagram
            plt.savefig(diagram_path, format="PNG",
                        dpi=150, bbox_inches='tight')
            plt.close()

            # Log the diagram creation
            logger.info(f"Generated verification diagram at {diagram_path}")

            # Return the relative path to the diagram for inclusion in the notebook
            return f"diagrams/{diagram_filename}"
        except Exception as e:
            logger.warning(
                f"Failed to generate verification diagram for section {section.name}: {e}")
            return None

    def generate_documentation(self, documentation: Documentation):
        TMP_DOCS_PATH.mkdir(parents=True, exist_ok=True)

        nomenclature_symbols: list[BaseSymbol] = []
        global_symbols: list[BaseSymbol] = []

        nb = nbf.v4.new_notebook()
        documentation_cells: list[nbf.NotebookNode] = []

        for code_object in documentation.exports:
            if isinstance(code_object, Section):
                if code_object.show_in_documentation:
                    for arg in code_object.args:
                        if arg not in nomenclature_symbols:
                            nomenclature_symbols.append(arg)
                    section_str = self.get_section_str(code_object)
                    documentation_cells.append(
                        nbf.v4.new_markdown_cell(section_str)
                    )

                    # Add I/O diagram for the section
                    io_diagram_path = self.generate_section_io_diagram(
                        code_object)
                    if io_diagram_path:
                        io_diagram_cell = nbf.v4.new_markdown_cell(
                            f"### Inputs and Outputs\n\n"
                            f"![Inputs and Outputs Diagram]({io_diagram_path})"
                        )
                        documentation_cells.append(io_diagram_cell)

                    # Add verification diagram if the section has verification capabilities
                    if hasattr(code_object, 'theorems') and code_object.theorems:
                        diagram_path = self.generate_verification_diagram(
                            code_object)
                        if diagram_path:
                            diagram_cell = nbf.v4.new_markdown_cell(
                                f"### Verification Diagram\n\n"
                                f"![Verification Diagram]({diagram_path})"
                            )
                            documentation_cells.append(diagram_cell)

                            # Add proof summary if available
                            if hasattr(code_object, 'get_proof_summary') and code_object.proof_results:
                                proof_summary = code_object.get_proof_summary()
                                proof_summary_cell = nbf.v4.new_markdown_cell(
                                    f"### Proof Results\n\n```\n{proof_summary}\n```"
                                )
                                documentation_cells.append(proof_summary_cell)
            elif isinstance(code_object, BaseSymbol):
                global_symbols.append(code_object)

        title_cell = nbf.v4.new_markdown_cell(f"# {documentation.name}")
        nomenclature_str = self.get_nomenclature_str(nomenclature_symbols)
        nomenclature_cell = nbf.v4.new_markdown_cell(nomenclature_str)
        nb['cells'] = [title_cell, nomenclature_cell]

        if len(global_symbols) > 0:
            globals_str = self.get_globals_str(global_symbols)
            globals_cell = nbf.v4.new_markdown_cell(globals_str)
            nb['cells'].append(globals_cell)

        file_name = f"{documentation.name.replace(' ', '_')}.ipynb"
        nb['cells'] = nb['cells'] + documentation_cells

        # Print debug information
        print(f"\nDocumentationGenerator debug information:")
        print(f"Documentation name: {documentation.name}")
        print(f"File name: {file_name}")

        notebook_path = Path(TMP_DOCS_PATH, file_name)
        print(f"Notebook path: {notebook_path}")
        print(f"Docs path: {self.docs_path}")
        print(f"Package path: {self.package_path}")

        # Create the notebook file
        DocumentationGenerator.save_notebook(nb, notebook_path, self.docs_path)

    @staticmethod
    def save_notebook(nb: nbf.NotebookNode, notebook_path: Path, output_path: Path):
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        # Create diagrams directory inside output path
        diagrams_dir = output_path / "diagrams"
        diagrams_dir.mkdir(parents=True, exist_ok=True)

        # Write notebook to temporary location
        with open(notebook_path, 'w', encoding="utf-8") as f:
            nbf.write(nb, f)

        # Convert notebook to HTML
        try:
            cmd = f"jupyter nbconvert --to html --output-dir='{output_path}' '{notebook_path}'"
            print(f"Running command: {cmd}")
            result = os.system(cmd)
            print(f"Command result: {result}")
            logger.info(f"Generated HTML documentation at {output_path}")

            # Also copy the notebook to the output directory
            import shutil
            notebook_dest = output_path / notebook_path.name
            shutil.copy2(notebook_path, notebook_dest)
            logger.info(f"Copied notebook to {notebook_dest}")
        except Exception as e:
            logger.error(f"Failed to convert notebook to HTML: {e}")

    @staticmethod
    def generate_table_of_contents(title: str, docs: list[Documentation], output_path: Path):
        TMP_DOCS_PATH.mkdir(parents=True, exist_ok=True)
        nb = nbf.v4.new_notebook()
        title_cell = nbf.v4.new_markdown_cell(f"# {title}")
        table_of_contents_cell = nbf.v4.new_markdown_cell(
            "## Table of Contents")
        nb['cells'] = [title_cell, table_of_contents_cell]

        for doc in docs:
            mardown_cell = nbf.v4.new_markdown_cell(
                f"### <a href=\"./{doc.name.replace(' ', '_')}.html\">{doc.name}</a>")
            nb['cells'].append(mardown_cell)

        DocumentationGenerator.save_notebook(
            nb, f"{TMP_DOCS_PATH}/index.ipynb", output_path
        )

    @staticmethod
    def get_docs_directory(package_path: Path):
        # Use the package_path directly instead of its parent
        return Path(package_path, DOCS_DEFAULT_DIRECTORY)
