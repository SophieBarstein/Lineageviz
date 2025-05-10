# geometry_engine.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- Geometry Builders ---

def compute_vector(p1, p2):
    return np.array(p2) - np.array(p1)

def unit_vector(v):
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v

def compute_centroid(pts):
    return np.mean(pts, axis=0)

def compute_angle(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    dot = np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)
    return np.degrees(np.arccos(dot))

# --- 3D Plotting Functions ---

def plot_geometry_scene(cell_data, show_vectors=True, show_planes=True, show_spheres=True):
    fig = go.Figure()

    for _, row in cell_data.iterrows():
        name = row['name']
        x, y, z = row['x'], row['y'], row['z']
        volume = row.get('volume', 1.0)

        # Draw sphere for cell body
        if show_spheres:
            fig.add_trace(go.Scatter3d(
                x=[x], y=[y], z=[z],
                mode='markers+text',
                text=[name],
                textposition="top center",
                marker=dict(size=5 + volume * 10, color='lightblue', opacity=0.8),
                name=name
            ))

        # Draw division vector and plane if daughters exist
        daughters = row.get('daughters', [])
        if show_vectors and len(daughters) == 2:
            d1 = cell_data[cell_data['name'] == daughters[0]]
            d2 = cell_data[cell_data['name'] == daughters[1]]
            if not d1.empty and not d2.empty:
                x1, y1, z1 = d1.iloc[0][['x', 'y', 'z']]
                x2, y2, z2 = d2.iloc[0][['x', 'y', 'z']]
                cx, cy, cz = compute_centroid([(x1, y1, z1), (x2, y2, z2)])

                # Vector from parent to centroid
                fig.add_trace(go.Scatter3d(
                    x=[x, cx], y=[y, cy], z=[z, cz],
                    mode='lines',
                    line=dict(color='red', width=3),
                    name=f"Vector {name}"
                ))

                # Division plane (as transparent triangle)
                if show_planes:
                    fig.add_trace(go.Mesh3d(
                        x=[x1, x2, x],
                        y=[y1, y2, y],
                        z=[z1, z2, z],
                        color='gray',
                        opacity=0.2,
                        showscale=False,
                        name=f"Plane {name}"
                    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='AP',
            yaxis_title='DV',
            zaxis_title='LR'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=600,
        title="Cell Geometry Scene"
    )

    return fig

# --- Analysis ---

def compute_angle_table(cell_data):
    angles = []
    for _, row in cell_data.iterrows():
        daughters = row.get('daughters', [])
        if len(daughters) == 2:
            d1 = cell_data[cell_data['name'] == daughters[0]]
            d2 = cell_data[cell_data['name'] == daughters[1]]
            if not d1.empty and not d2.empty:
                p = np.array([row['x'], row['y'], row['z']])
                v1 = compute_vector(p, d1.iloc[0][['x', 'y', 'z']])
                v2 = compute_vector(p, d2.iloc[0][['x', 'y', 'z']])
                angle = compute_angle(v1, v2)
                angles.append({"parent": row['name'], "angle": angle})
    return pd.DataFrame(angles)

# --- Export ---
def export_to_ply(cell_data, filename="embryo.ply"):
    with open(filename, 'w') as f:
        f.write("ply\nformat ascii 1.0\nelement vertex %d\n" % len(cell_data))
        f.write("property float x\nproperty float y\nproperty float z\nend_header\n")
        for _, row in cell_data.iterrows():
            f.write(f"{row['x']} {row['y']} {row['z']}\n")
