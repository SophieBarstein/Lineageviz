def layout_tree(node, level_height=1.5):
    y_counter = [0]  # mutable so it can increment across recursion

    def recurse(n, x_start):
        if not n.children:
            n.x = x_start + n.length
            n.y = y_counter[0] * level_height
            y_counter[0] += 1
            return n.y, n.y, n.x

        child_positions = []
        max_x = x_start + n.length
        for child in n.children:
            y_top, y_bot, child_x = recurse(child, x_start + n.length)
            center_y = (y_top + y_bot) / 2
            child_positions.append(center_y)
            max_x = max(max_x, child_x)

        y_top = max(child_positions)
        y_bot = min(child_positions)
        n.x = x_start
        n.y = (1 - n.offset) * y_top + n.offset * y_bot

        return y_top, y_bot, max_x

    recurse(node, 0)