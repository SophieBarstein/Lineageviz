import matplotlib.pyplot as plt
import pandas as pd

def draw_tree(node, ax, show_sizes=True, show_times=True, show_time_axis=True,
              color_map=None, search_target=None, fate_labels=None, angle_labels=None):
    times = []

    def recurse(n, current_time):
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
                recurse(child, current_time + n.length)
                ax.plot([split_x, child.x], [n.y, child.y], color=color)

            # Vertical connector
            child_ys = [child.y for child in n.children]
            ax.plot([split_x, split_x], [min(child_ys), max(child_ys)], color=color)

            # Size ratio labels
            if show_sizes and len(n.children) == 2:
                c1, c2 = n.children
                total = c1.length + c2.length
                if total > 0:
                    p1 = int((c1.length / total) * 100)
                    p2 = 100 - p1
                    ax.text(split_x + 1, c1.y + 0.5, f"{p1}%", ha='center', fontsize=7)
                    ax.text(split_x + 1, c2.y - 0.5, f"{p2}%", ha='center', fontsize=7)

            # Division angle label
            if angle_labels and n.name in angle_labels:
                ax.text(split_x, n.y + 0.8, f"{angle_labels[n.name]:.1f}°", ha='center', fontsize=7, color='gray')

            # Division time label
            if show_times:
                ax.text(split_x, n.y + 1.5, f"{int(current_time + n.length)} min", ha='center', fontsize=7)

        # Horizontal lifespan line
        ax.plot([n.x, split_x], [n.y, n.y], color=color)

        # Label
        if n.name and not pd.isna(n.name):
            label_color = 'red' if n.name == search_target else 'black'
            ax.text(n.x - 1.5, n.y, n.name, va='center', ha='right', fontsize=8, color=label_color)

            # Optional fate label
            if fate_labels and n.name in fate_labels:
                ax.text(split_x + 1, n.y, fate_labels[n.name], va='center', ha='left', fontsize=7, style='italic', color='gray')

    recurse(node, 0)

    if show_time_axis:
        max_time = max(times) if times else 0
        ax.set_xlim(left=0, right=max_time + 10)
        ticks = list(range(0, int(max_time) + 41, 40))
        minor_ticks = list(range(0, int(max_time) + 10, 10))
        ax.set_xticks(ticks)
        ax.set_xticks(minor_ticks, minor=True)
        ax.set_xticklabels([f"{t}" for t in ticks], fontsize=8)
        ax.tick_params(axis='x', which='major', length=5, direction='out')
        ax.tick_params(axis='x', which='minor', length=2, direction='out')
        ax.grid(True, axis='x', which='major', linestyle=':', linewidth=0.4, color='gray')
        ax.set_xlabel("Minutes Post-Fertilization", fontsize=10)
        ax.xaxis.set_label_position('bottom')
        ax.xaxis.tick_bottom()
