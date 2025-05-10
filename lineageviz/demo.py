from lineageviz.parser import parse_newick_plusplus
from lineageviz.layout import layout_tree
from lineageviz.plot import draw_tree
import matplotlib.pyplot as plt

# Accurate tree for C. elegans (first 4 cleavages, 16 cells)
tree_str = (
    "((((ABala:0.3@0.5,ABalp:0.3@0.5)ABal:40@0.5,"
    "(ABara:0.3@0.5,ABarp:0.3@0.5)ABar:40@0.5)ABa:40@0.5,"
    "((ABpla:0.3@0.5,ABplp:0.3@0.5)ABpl:40@0.5,"
    "(ABpra:0.3@0.5,ABprp:0.3@0.5)ABpr:40@0.5)ABp:40@0.5)AB:40@0.6,"
    "(((MSa:0.15@0.5,MSp:0.15@0.5)MS:40@0.5,"
    "(Ea:0.15@0.5,Ep:0.15@0.5)E:40@0.5)EMS:40@0.5,"
    "((Ca:0.125@0.5,Cp:0.125@0.5)C:40@0.5,"
    "(D:0.25@0.5,P4:0.25@0.5)D_P4:40@0.5)P3:40@0.5)P1:40@0.4)P0:40@0.5;"
)

# Parse and lay out the tree
tree = parse_newick_plusplus(tree_str)
layout_tree(tree, level_height=2)

# Plot it
fig, ax = plt.subplots(figsize=(16, 10))
draw_tree(tree, ax, show_times=True, show_sizes=True, show_time_axis=True)
ax.set_title("C. elegans Lineage Tree (First 4 Cleavages)", fontsize=16)
#ax.axis('off')
plt.tight_layout()
plt.show()
