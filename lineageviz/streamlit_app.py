
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO
from lineageviz.layout import layout_tree
from lineageviz.plot import draw_tree
from lineageviz.tree import Node
from geometry_engine import plot_geometry_scene
from spatial_infer import position_tree

st.set_page_config(layout="wide")
st.title("🧬 Lineage Tree Visualizer")

API_BASE = "https://cleavage-api.onrender.com"
try:
    response = requests.get(f"{API_BASE}/species")
    response.raise_for_status()
    species_list = response.json()
except Exception as e:
    st.sidebar.warning("⚠️ Could not load species from API.")
    species_list = []

species_choice = st.sidebar.selectbox("📚 Load Preset Species", ["None"] + species_list)

DEFAULT_COLUMNS = [
    "parent", "left_child", "right_child", "time",
    "left_volume", "right_volume", "fate", "division_angle",
    "shape", "elongation_axis"
]

if "lineage_data" not in st.session_state:
    st.session_state.lineage_data = pd.DataFrame(columns=DEFAULT_COLUMNS)

# === Sidebar ===
st.sidebar.header("Display Options")
max_time = int(st.session_state.lineage_data["time"].max()) if not st.session_state.lineage_data.empty else 200
time_limit = st.sidebar.slider("Show Tree Up To Time (min)", 0, max_time, max_time, step=10)
show_sizes = st.sidebar.checkbox("Show Size Labels", value=True)
show_times = st.sidebar.checkbox("Show Division Times", value=True)
show_axis = st.sidebar.checkbox("Show Time Axis", value=True)
color_by_lineage = st.sidebar.checkbox("Color Code Lineages", value=True)
show_fates = st.sidebar.checkbox("Show Fate Labels", value=True)
show_angles = st.sidebar.checkbox("Show Division Angles", value=True)
search_cell = st.sidebar.text_input("Highlight Cell")
show_geometry = st.sidebar.checkbox("Show geometry scene")
show_vectors = st.sidebar.checkbox("Show division vectors", value=True)
show_planes = st.sidebar.checkbox("Show division planes", value=True)
show_shapes = st.sidebar.checkbox("Show cell volumes", value=True)

if species_choice != "None":
    try:
        response = requests.get(f"{API_BASE}/species/{species_choice}")
        if response.status_code == 200:
            api_df = pd.DataFrame(response.json())
            st.session_state.lineage_data = api_df
            st.success(f"Loaded {species_choice} from API")
        else:
            st.error("Failed to load species data")
    except Exception as e:
        st.error("Error connecting to API")

# === Input Help + Template ===
with st.sidebar.expander("📄 Input Format Instructions"):
    st.markdown("""
    Your CSV must include:
    - `parent`, `left_child`, `right_child`
    - `time`, `left_volume`, `right_volume`
    - Optional: `fate`, `division_angle`, `shape`, `elongation_axis`

    Example shapes: `sphere`, `elongated`, `compressed`
    Example axes: `AP`, `DV`, `LR`
    """)
    sample_csv = pd.DataFrame([{
        "parent": "P0", "left_child": "AB", "right_child": "P1", "time": 40,
        "left_volume": 0.6, "right_volume": 0.4, "fate": "", "division_angle": 90,
        "shape": "elongated", "elongation_axis": "AP"
    }])
    csv_buf = StringIO()
    sample_csv.to_csv(csv_buf, index=False)
    st.download_button("📥 Download CSV Template", data=csv_buf.getvalue(), file_name="lineage_template.csv")

# === Upload Input ===
st.subheader("📁 Upload Lineage File")
uploaded_file = st.file_uploader("Upload a unified lineage CSV", type=["csv"])
if uploaded_file:
    try:
        st.session_state.lineage_data = pd.read_csv(uploaded_file)
        st.success("File loaded successfully.")
    except Exception as e:
        st.error(f"Upload failed: {e}")

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

# === Add Division Form ===
st.subheader("➕ Add New Division")
with st.form("add_division"):
    cols = st.columns(10)
    inputs = {
        "parent": cols[0].text_input("Parent"),
        "left_child": cols[1].text_input("Left Daughter"),
        "right_child": cols[2].text_input("Right Daughter"),
        "time": cols[3].number_input("Time", min_value=0.0, step=10.0),
        "left_volume": cols[4].number_input("Left Vol", min_value=0.0, step=0.1, value=0.5),
        "right_volume": cols[5].number_input("Right Vol", min_value=0.0, step=0.1, value=0.5),
        "fate": cols[6].text_input("Fate (opt)"),
        "division_angle": cols[7].number_input("Angle (opt)", min_value=0.0, max_value=180.0, step=5.0, value=90.0),
        "shape": cols[8].text_input("Shape (opt)"),
        "elongation_axis": cols[9].text_input("Axis (opt)")
    }
    if st.form_submit_button("Add"):
        if all([inputs["parent"], inputs["left_child"], inputs["right_child"]]):
            st.session_state.lineage_data = pd.concat([
                st.session_state.lineage_data, pd.DataFrame([inputs])
            ], ignore_index=True)
            st.success(f"Added: {inputs['parent']} → {inputs['left_child']}, {inputs['right_child']}")
        else:
            st.warning("Missing parent or daughter cell names.")

# === Tree Rendering ===
st.subheader("🌳 Lineage Tree Preview")
rows = st.session_state.lineage_data.to_dict(orient="records")
nodes, structure, cell_fates = {}, [], {}
LINEAGE_COLORS = {
    "AB": "#0066cc", "P1": "#cc3300", "MS": "#009966", "E": "#ffcc00",
    "C": "#9933cc", "D": "#666666", "P4": "#cc6699", "others": "gray"
}
for row in rows:
    try:
        parent, left, right = row['parent'], row['left_child'], row['right_child']
        time = float(row['time'])
        lv, rv = float(row['left_volume']), float(row['right_volume'])
        fate = row.get('fate', '')
        if not all([parent, left, right]) or lv <= 0 or rv <= 0 or time > time_limit:
            continue
        offset = rv / (lv + rv) if (lv + rv) > 0 else 0.5
        nodes[left] = Node(name=left, length=lv, offset=0.5)
        nodes[right] = Node(name=right, length=rv, offset=0.5)
        if fate:
            cell_fates[left] = fate
            cell_fates[right] = fate
        structure.append((parent, nodes[left], nodes[right], time, offset))
    except Exception:
        continue
if structure:
    for parent, left, right, time, offset in reversed(structure):
        p = nodes.get(parent, Node(name=parent))
        p.length = time
        p.offset = offset
        p.children = [left, right]
        nodes[parent] = p
    root = nodes[structure[0][0]]
    root.name = structure[0][0]
    layout_tree(root, level_height=2)
    fig, ax = plt.subplots(figsize=(14, 6))
    angle_labels = {row["parent"]: row["division_angle"] for row in rows if "division_angle" in row and pd.notna(row["division_angle"])}
    draw_tree(root, ax,
              show_sizes=show_sizes,
              show_times=show_times,
              show_time_axis=show_axis,
              color_map=LINEAGE_COLORS if color_by_lineage else None,
              search_target=search_cell,
              fate_labels=cell_fates if show_fates else None,
              angle_labels=angle_labels if show_angles else None)
    ax.get_yaxis().set_visible(False)
    st.pyplot(fig)

# === Geometry Scene ===
def build_cell_data_with_inference(lineage_df, time_cutoff):
    tree = {}
    birth_times = {"P0": 0.0}
    death_times = {}
    for _, row in lineage_df.iterrows():
        p, l, r = row['parent'], row['left_child'], row['right_child']
        div_time = row['time']
        angle = row.get('division_angle', 90)
        tree[p] = {
            "daughters": [l, r],
            "left_volume": row['left_volume'],
            "right_volume": row['right_volume'],
            "division_angle": angle,
            "shape": row.get('shape', None),
            "elongation_axis": row.get('elongation_axis', None)
        }
        birth_times[l], birth_times[r] = div_time, div_time
        death_times[p] = div_time
    positions = position_tree(tree, root_name='P0', parent_pos=(0, 0, 0))
    visible = [name for name in positions if birth_times.get(name, 0) <= time_cutoff < death_times.get(name, float('inf'))]
    return pd.DataFrame([{ "name": name, "x": x, "y": y, "z": z, "volume": tree.get(name, {}).get("left_volume", 0.5) } for name, (x, y, z) in positions.items() if name in visible])

if show_geometry:
    cell_data = build_cell_data_with_inference(st.session_state.lineage_data, time_limit)
    fig_geo = plot_geometry_scene(cell_data, show_vectors, show_planes, show_shapes)
    st.plotly_chart(fig_geo, use_container_width=True)

# === Export ===
st.subheader("📤 Download Current Tree as CSV")
csv_buffer = StringIO()
st.session_state.lineage_data.to_csv(csv_buffer, index=False)
st.download_button("Download Lineage CSV", data=csv_buffer.getvalue(), file_name="lineage.csv", mime="text/csv")
