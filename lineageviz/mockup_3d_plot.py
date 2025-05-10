# mockup_3d_plot.py
import plotly.graph_objects as go
import pandas as pd

def plot_3d_mockup(lineage_df, use_demo=False):
    coords = []

    if {'x', 'y', 'z'}.issubset(lineage_df.columns):
        # Use user-supplied 3D coordinates
        for _, row in lineage_df.iterrows():
            for cell in [row['left_child'], row['right_child']]:
                cell_row = lineage_df[(lineage_df['left_child'] == cell) | (lineage_df['right_child'] == cell)]
                if not cell_row.empty:
                    x = cell_row.iloc[0].get('x', 0)
                    y = cell_row.iloc[0].get('y', 0)
                    z = cell_row.iloc[0].get('z', 0)
                    coords.append((cell, x, y, z))

    elif use_demo:
        # Use placeholder 3D positions for demo
        positions = {
            "P0": (0, 0, 0),
            "AB": (-1, 1, 0),
            "P1": (1, -1, 0),
            "ABa": (-1.5, 1.5, 0.5), "ABp": (-0.5, 0.5, 0.5),
            "EMS": (0.5, -0.5, 0.5), "P2": (1.5, -1.5, 0.5),
            "ABal": (-1.8, 1.8, 1), "ABar": (-1.2, 1.2, 1),
            "ABpl": (-0.8, 0.8, 1), "ABpr": (-0.2, 0.2, 1),
            "MS": (0.3, -0.3, 1), "E": (0.7, -0.7, 1),
            "C": (1.3, -1.3, 1), "P3": (1.7, -1.7, 1)
        }

        for cell in lineage_df['left_child'].tolist() + lineage_df['right_child'].tolist():
            if cell in positions:
                x, y, z = positions[cell]
                coords.append((cell, x, y, z))

    else:
        return None  # No valid coordinates and no demo fallback

    df_coords = pd.DataFrame(coords, columns=['name', 'x', 'y', 'z'])

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=df_coords['x'], y=df_coords['y'], z=df_coords['z'],
        mode='markers+text',
        text=df_coords['name'],
        textposition="top center",
        marker=dict(size=6, color='lightblue', opacity=0.8),
        name="Cells"
    ))

    fig.update_layout(
        title="3D Cell Layout Mockup",
        scene=dict(
            xaxis_title='Anterior-Posterior',
            yaxis_title='Dorsal-Ventral',
            zaxis_title='Left-Right',
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=600
    )

    return fig
