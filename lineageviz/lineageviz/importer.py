import csv
from .tree import Node

def load_tree_from_csv(filename):
    nodes = {}
    structure = []

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            parent = row['parent']
            left = row['left_child']
            right = row['right_child']
            time = float(row['time'])
            left_vol = float(row['left_volume'])
            right_vol = float(row['right_volume'])
            total_vol = left_vol + right_vol

            # Automatically calculate offset based on volume
            offset = right_vol / (left_vol + right_vol) if (left_vol + right_vol) > 0 else 0.5

            # Create child nodes with length = volume
            left_node = Node(name=left, length=left_vol, offset=0.5)
            right_node = Node(name=right, length=right_vol, offset=0.5)
            nodes[left] = left_node
            nodes[right] = right_node

            structure.append((parent, left_node, right_node, time, offset))

    # Build tree from bottom-up
    for parent, left, right, time, offset in reversed(structure):
        if parent in nodes:
            parent_node = nodes[parent]
        else:
            parent_node = Node(name=parent)
            nodes[parent] = parent_node

        parent_node.length = time
        parent_node.offset = offset
        parent_node.children = [left, right]

    return nodes[structure[0][0]]

import json
from .tree import Node

def load_tree_from_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    nodes = {}
    structure = []

    for row in data:
        parent = row['parent']
        left = row['left_child']
        right = row['right_child']
        time = float(row['time'])
        left_vol = float(row['left_volume'])
        right_vol = float(row['right_volume'])
        total_vol = left_vol + right_vol

        offset = right_vol / (left_vol + right_vol) if (left_vol + right_vol) > 0 else 0.5

        left_node = Node(name=left, length=left_vol, offset=0.5)
        right_node = Node(name=right, length=right_vol, offset=0.5)
        nodes[left] = left_node
        nodes[right] = right_node

        structure.append((parent, left_node, right_node, time, offset))

    for parent, left, right, time, offset in reversed(structure):
        if parent in nodes:
            parent_node = nodes[parent]
        else:
            parent_node = Node(name=parent)
            nodes[parent] = parent_node

        parent_node.length = time
        parent_node.offset = offset
        parent_node.children = [left, right]

    return nodes[structure[0][0]]