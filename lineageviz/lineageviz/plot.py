import matplotlib.pyplot as plt
import pandas as pd

def draw_tree(node, ax, show_sizes=True, show_times=True, show_time_axis=True,
              color_map=None, search_target=None, fate_labels=None, angle_labels=None):
    times = []

    def recurse(n):
        split_x = n.x + n.length
        times.append(split_x)

        color = 'black'
        if color_map:
            lineage_root = n.name[:2] if n.name else 'others'
            for root_name in color_map:
                if n.name and n.name.startswith(root_name):
                    color = color_map[root_name]
                    break

        if n.children:
            for child in n.children:
                recurse(child)
                ax.plot([split_x, child.x], [n.y, child.y], color=color)

            child_ys = [child.y for child in n.children]
            ax.plot([split_x, split_x], [min(child_ys), max(child_ys)], color=color)

            if show_sizes and len(n.children) == 2:
                c1, c2 = n.children
                total = c1.length + c2.length
                if total > 0:
                    p1 = int((c1.length / total) * 100)
                    p2 = 100 - p1
                    ax.text(split_x + 1, c1.y + 0.5, f"{p1}%", ha='center', fontsize=7)
                    ax.text(split_x + 1, c2.y - 0.5, f"{p2}%", ha='center', fontsize=7)

            if angle_labels and n.name in angle_labels:
                ax.text(split_x, n.y + 0.8, f"{angle_labels[n.name]:.1f}°", ha='center', fontsize=7, color='gray')

            if show_times:
                ax.text(split_x, n.y + 1.5, f"{int(n.length)} min", ha='center', fontsize=7)

        ax.plot([n.x, split_x], [n.y, n.y], color=color)

        if n.name and not pd.isna(n.name):
            label_color = 'red' if n.name == search_target else 'black'
            ax.text(n.x - 1.5, n.y, n.name, va='center', ha='right', fontsize=8, color=label_color)
            if fate_labels and n.name in fate_labels:
                ax.text(split_x + 1, n.y, fate_labels[n.name], va='center', ha='left', fontsize=7, style='italic', color='gray')

    recurse(node)

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
