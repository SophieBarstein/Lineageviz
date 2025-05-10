class Node:
    def __init__(self, name=None, length=0.0, offset=0.5, children=None):
        self.name = name
        self.length = length
        self.offset = offset
        self.children = children if children else []
        self.x = None  # for plotting
        self.y = None  # for plotting

    def __repr__(self):
        return f"Node(name={self.name}, length={self.length}, offset={self.offset}, children={len(self.children)})"