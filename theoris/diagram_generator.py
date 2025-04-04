import matplotlib.pyplot as plt
import networkx as nx

def generate_diagram(blocks):
    """
    Generate a diagram from block inputs and outputs.

    :param blocks: A list of blocks, where each block is a dictionary with 'name', 'inputs', and 'outputs'.
    """
    G = nx.DiGraph()

    for block in blocks:
        G.add_node(block['name'])
        for input_block in block['inputs']:
            G.add_edge(input_block, block['name'])
        for output_block in block['outputs']:
            G.add_edge(block['name'], output_block)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold')
    plt.show()