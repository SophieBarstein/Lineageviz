import re
from .tree import Node

def parse_newick_plusplus(s):
    tokens = re.findall(r'[\(\),;]|[^\(\),;]+', s.strip())

    def parse_node(index):
        if tokens[index] == '(':
            index += 1
            children = []
            while tokens[index] != ')':
                child, index = parse_node(index)
                children.append(child)
                if tokens[index] == ',':
                    index += 1
            index += 1  # skip ')'
            if index < len(tokens) and tokens[index] not in [',', ')', ';']:
                label, index = parse_label(tokens[index], index)
            else:
                label = (None, 0.0, 0.5)
            return Node(name=label[0], length=label[1], offset=label[2], children=children), index
        else:
            label, index = parse_label(tokens[index], index)
            return Node(name=label[0], length=label[1], offset=label[2]), index

    def parse_label(token, index):
        match_full = re.match(r'([^:]+):([\d\.]+)@([\d\.]+)', token)
        match_unnamed = re.match(r':([\d\.]+)@([\d\.]+)', token)
        match_name_only = re.match(r'^[^:]+$', token)

        if match_full:
            return (match_full.group(1), float(match_full.group(2)), float(match_full.group(3))), index + 1
        elif match_unnamed:
            return (None, float(match_unnamed.group(1)), float(match_unnamed.group(2))), index + 1
        elif match_name_only:
            return (token, 0.0, 0.5), index + 1
        else:
            raise ValueError(f"Invalid label at token {index}: {token}")

    tree, _ = parse_node(0)
    return tree