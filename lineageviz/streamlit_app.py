# Complete streamlit_app.py with full lineage editing and 3D geometry inference

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from lineageviz.layout import layout_tree
from lineageviz.plot import draw_tree
from lineageviz.tree import Node
from geometry_engine import plot_geometry_scene
from spatial_infer import position_tree

st.set_page_config(layout="wide")
st.title("🧬 Lineage Tree Visualizer")

DEFAULT_COLUMNS = [
    "parent", "left_child", "right_child", "time",
    "left_volume", "right_volume", "fate", "division_type", "division_angle"
]

if "lineage_data" not in st.session_state:
    st.session_state.lineage_data = pd.DataFrame(columns=DEFAULT_COLUMNS)

# === Sidebar display options ===
st.sidebar.header("Display Options")
show_sizes = st.sidebar.checkbox("Show Size Labels", value=True)
show_times = st.sidebar.checkbox("Show Division Times", value=True)
show_axis = st.sidebar.checkbox("Show Time Axis", value=True)
color_by_lineage = st.sidebar.checkbox("Color Code Lineages", value=True)
show_fates = st.sidebar.checkbox("Show Fate Labels", value=True)
search_cell = st.sidebar.text_input("Highlight Cell")
time_limit = st.sidebar.slider("Show Tree Up To Time (min)", 0, 200, 200, step=10)
show_geometry = st.sidebar.checkbox("Show geometry scene")
show_vectors = st.sidebar.checkbox("Show division vectors", value=True)
show_planes = st.sidebar.checkbox("Show division planes", value=True)
show_shapes = st.sidebar.checkbox("Show cell volumes", value=True)
show_angles = st.sidebar.checkbox("Show Division Angles", value=True)

# === Upload lineage CSV ===
st.subheader("📁 Upload Lineage CSV")
uploaded_file = st.file_uploader("Choose a lineage CSV file", type=["csv"], key="lineage")
if uploaded_file:
    try:
        st.session_state.lineage_data = pd.read_csv(uploaded_file)
        st.success("Lineage CSV file loaded.")
    except Exception as e:
        st.error(f"Failed to load lineage file: {e}")

# === Add Division Form ===
st.subheader("➕ Add New Division")
with st.form(key="add_division_form"):
    cols = st.columns(9)
    parent = cols[0].text_input("Parent")
    left = cols[1].text_input("Left Daughter")
    right = cols[2].text_input("Right Daughter")
    time = cols[3].number_input("Time", min_value=0.0, step=10.0)
    lv = cols[4].number_input("Left Volume", min_value=0.0, step=0.1, value=0.5)
    rv = cols[5].number_input("Right Volume", min_value=0.0, step=0.1, value=0.5)
    fate = cols[6].text_input("Fate (optional)")
    divtype = cols[7].selectbox("Division Type", ["", "symmetric", "asymmetric"])
    angle = cols[8].number_input("Division Angle (°)", min_value=0.0, max_value=180.0, step=5.0, value=90.0)
    submitted = st.form_submit_button("Add Division")

    if submitted:
        if all([parent, left, right]) and lv > 0 and rv > 0:
            new_row = pd.DataFrame([{
                "parent": parent, "left_child": left, "right_child": right, "time": time,
                "left_volume": lv, "right_volume": rv, "fate": fate,
                "division_type": divtype, "division_angle": angle
            }])
            st.session_state.lineage_data = pd.concat([st.session_state.lineage_data, new_row], ignore_index=True)
            st.success(f"Added division: {parent} → {left}, {right}")
        else:
            st.warning("Please fill all fields with valid values.")

# === Editable Table ===
st.subheader("🧾 Current Divisions")
st.session_state.lineage_data.index.name = "row"
edited_df = st.data_editor(
    st.session_state.lineage_data,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True
)
st.session_state.lineage_data = edited_df

# === Tree Rendering ===
st.subheader("🌳 Lineage Tree Preview")
rows = st.session_state.lineage_data.to_dict(orient="records")
nodes = {}
structure = []
cell_fates = {}
LINEAGE_COLORS = {
    "AB": "#1f77b4", "P1": "#ff7f0e", "MS": "#2ca02c", "E": "#d62728",
    "C": "#9467bd", "D": "#8c564b", "P4": "#e377c2", "others": "gray"
}

for row in rows:
    try:
        parent = row['parent']
        left = row['left_child']
        right = row['right_child']
        time = float(row['time'])
        lv = float(row['left_volume'])
        rv = float(row['right_volume'])
        fate = row.get('fate', '')
        if not all([parent, left, right]) or lv <= 0 or rv <= 0 or time > time_limit:
            continue
        total = lv + rv
        offset = rv / total if total > 0 else 0.5
        left_node = Node(name=left, length=lv, offset=0.5)
        right_node = Node(name=right, length=rv, offset=0.5)
        nodes[left] = left_node
        nodes[right] = right_node
        if fate:
            cell_fates[left] = fate
            cell_fates[right] = fate
        structure.append((parent, left_node, right_node, time, offset))
    except Exception:
        continue

if not structure:
    st.info("Waiting for complete division rows within selected time...")
else:
    for parent, left, right, time, offset in reversed(structure):
        pnode = nodes[parent] if parent in nodes else Node(name=parent)
        pnode.length = time
        pnode.offset = offset
        pnode.children = [left, right]
        nodes[parent] = pnode
    root = nodes[structure[0][0]]
    layout_tree(root, level_height=2)
    fig, ax = plt.subplots(figsize=(14, 6))
    angle_labels = {row["parent"]: row["division_angle"] for _, row in edited_df.iterrows()}
    draw_tree(root, ax,
              show_sizes=show_sizes,
              show_times=show_times,
              show_time_axis=show_axis,
              angle_labels=angle_labels if show_angles else None,
              color_map=LINEAGE_COLORS if color_by_lineage else None,
              search_target=search_cell,
              fate_labels=cell_fates if show_fates else None)
    ax.get_yaxis().set_visible(False)
    st.pyplot(fig)

# === Geometry Inference ===
def build_cell_data_with_inference(lineage_df, time_cutoff):
    tree = {}
    birth_times = {"P0": 0.0}
    death_times = {}
    for _, row in lineage_df.iterrows():
        p = row['parent']
        l = row['left_child']
        r = row['right_child']
        div_time = row['time']
        angle = row.get('division_angle', 90)
        tree[p] = {
            "daughters": [l, r],
            "left_volume": row['left_volume'],
            "right_volume": row['right_volume'],
            "division_angle": angle
        }
        birth_times[l] = div_time
        birth_times[r] = div_time
        death_times[p] = div_time

    positions = position_tree(tree, root_name='P0', parent_pos=(0, 0, 0))
    visible = []
    for name, coord in positions.items():
        birth = birth_times.get(name, 0)
        death = death_times.get(name, float('inf'))
        if birth <= time_cutoff < death:
            visible.append(name)

    cell_data = []
    for name in visible:
        coord = positions[name]
        volume = 0.5
        for _, row in lineage_df.iterrows():
            if row['left_child'] == name:
                volume = row['left_volume']
            elif row['right_child'] == name:
                volume = row['right_volume']
        cell_data.append({"name": name, "x": coord[0], "y": coord[1], "z": coord[2], "volume": volume})

    return pd.DataFrame(cell_data)

# === Geometry Scene ===
if show_geometry:
    cell_data = build_cell_data_with_inference(st.session_state.lineage_data, time_limit)
    fig_geo = plot_geometry_scene(cell_data, show_vectors, show_planes, show_shapes)
    st.plotly_chart(fig_geo, use_container_width=True)

# === Export ===
st.subheader("📤 Download Current Tree as CSV")
csv_buffer = StringIO()
st.session_state.lineage_data.to_csv(csv_buffer, index=False)
st.download_button("Download Lineage CSV", data=csv_buffer.getvalue(), file_name="lineage.csv", mime="text/csv")
