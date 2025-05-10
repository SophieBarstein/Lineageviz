import matplotlib.pyplot as plt
from .plot import draw_tree
from .layout import layout_tree

def save_tree_image(tree, filename="tree.png", figsize=(12, 6), dpi=300, **kwargs):
    """
    Save a lineage tree to an image file.

    Parameters:
    - tree: the root Node object
    - filename: output file path (e.g., 'tree.png', 'tree.svg')
    - figsize: size of the figure in inches
    - dpi: resolution (for raster formats like PNG)
    - kwargs: passed to draw_tree (e.g., show_sizes=True)
    """
    layout_tree(tree, level_height=2)

    fig, ax = plt.subplots(figsize=figsize)
    draw_tree(tree, ax, **kwargs)
    ax.get_yaxis().set_visible(False)
    ax.set_title("Lineage Tree", fontsize=12)
    plt.tight_layout()
    plt.savefig(filename, dpi=dpi)
    plt.close()