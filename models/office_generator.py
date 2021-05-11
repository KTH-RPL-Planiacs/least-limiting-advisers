import networkx as nx


def grid_directions_mdp(width, height):
    m = nx.DiGraph()

    # create grid nodes, staying and turning
    # (0,0) is upper left
    for x in range(width):
        for y in range(height):
            pos = '%i,%i' % (x, y)
            directions = ['_fu', '_fr', '_fd', '_fl']

            for i, d in enumerate(directions):
                m.add_node(pos + d, player=1)

            for i, d in enumerate(directions):
                # staying
                m.add_node(pos + d + '_s', player=0)
                m.add_edge(pos + d, pos + d + '_s', act='stay')
                m.add_edge(pos + d + '_s', pos + d, prob=1.0)
                # turn left
                m.add_node(pos + d + '_tl', player=0)
                m.add_edge(pos + d, pos + d + '_tl', act='turn_left')
                left_d = directions[(i - 1) % 4]
                m.add_edge(pos + d + '_tl', pos + left_d, prob=1.0)
                # turn right
                m.add_node(pos + d + '_tr', player=0)
                m.add_edge(pos + d, pos + d + '_tr', act='turn_right')
                right_d = directions[(i + 1) % 4]
                m.add_edge(pos + d + '_tr', pos + right_d, prob=1.0)

    # create and connect nodes for moving forward
    for x in range(width):
        for y in range(height):
            pos = '%i,%i' % (x, y)
            # moving up
            if y > 0:
                new_pos = '%i,%i' % (x, y-1)
                m.add_node(pos + '_fu_m', player=0)
                m.add_edge(pos + '_fu', pos + '_fu_m', act='move')
                m.add_edge(pos + '_fu_m', new_pos + '_fu', prob=1.0)
            if y < height-1:
                new_pos = '%i,%i' % (x, y+1)
                m.add_node(pos + '_fd_m', player=0)
                m.add_edge(pos + '_fd', pos + '_fd_m', act='move')
                m.add_edge(pos + '_fd_m', new_pos + '_fd', prob=1.0)
            if x > 0:
                new_pos = '%i,%i' % (x-1, y)
                m.add_node(pos + '_fl_m', player=0)
                m.add_edge(pos + '_fl', pos + '_fl_m', act='move')
                m.add_edge(pos + '_fl_m', new_pos + '_fl', prob=1.0)
            if x < width-1:
                new_pos = '%i,%i' % (x+1, y)
                m.add_node(pos + '_fr_m', player=0)
                m.add_edge(pos + '_fr', pos + '_fr_m', act='move')
                m.add_edge(pos + '_fr_m', new_pos + '_fr', prob=1.0)

    return m


def office_5x10_directions(r_id):
    m = grid_directions_mdp(10, 5)
    m.graph['ap'] = ['BIN' + r_id]

    # labelling
    attrs = {}
    for x in range(10):
        for y in range(5):
            pos = '%i,%i' % (x, y)
            directions = ['_fu', '_fr', '_fd', '_fl']

            for d in directions:
                if x == 4 and y == 2:
                    attrs[pos + d] = ['1']
                else:
                    attrs[pos + d] = ['0']

    nx.set_node_attributes(m, attrs, 'ap')
    return m


if __name__ == '__main__':
    mdp = office_5x10_directions('A')
