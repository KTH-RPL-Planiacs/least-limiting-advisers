import networkx as nx
import random


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
                new_pos = '%i,%i' % (x, y - 1)
                m.add_node(pos + '_fu_m', player=0)
                m.add_edge(pos + '_fu', pos + '_fu_m', act='move')
                m.add_edge(pos + '_fu_m', new_pos + '_fu', prob=1.0)
            if y < height - 1:
                new_pos = '%i,%i' % (x, y + 1)
                m.add_node(pos + '_fd_m', player=0)
                m.add_edge(pos + '_fd', pos + '_fd_m', act='move')
                m.add_edge(pos + '_fd_m', new_pos + '_fd', prob=1.0)
            if x > 0:
                new_pos = '%i,%i' % (x - 1, y)
                m.add_node(pos + '_fl_m', player=0)
                m.add_edge(pos + '_fl', pos + '_fl_m', act='move')
                m.add_edge(pos + '_fl_m', new_pos + '_fl', prob=1.0)
            if x < width - 1:
                new_pos = '%i,%i' % (x + 1, y)
                m.add_node(pos + '_fr_m', player=0)
                m.add_edge(pos + '_fr', pos + '_fr_m', act='move')
                m.add_edge(pos + '_fr_m', new_pos + '_fr', prob=1.0)

    return m


def office_5x10_mdp(r_id, n_bins=1):
    m = grid_directions_mdp(10, 5)

    m.graph['name'] = 'robot' + r_id
    m.graph['init'] = '%i,%i_fu' % (random.randint(0, 9), random.randint(0, 4))
    m.graph['ap'] = []
    for n in range(n_bins):
        m.graph['ap'].append('BIN%i' % n + r_id)

    # walls
    doors_up = [1, 4, 8]
    doors_down = [1, 3, 5, 7, 9]
    for x in range(10):
        if x not in doors_up:
            m.remove_node('%i,2_fu_m' % x)
            m.remove_node('%i,1_fd_m' % x)
        if x not in doors_down:
            m.remove_node('%i,2_fd_m' % x)
            m.remove_node('%i,3_fu_m' % x)

    upper_walls = [2, 6]
    lower_walls = [1, 3, 5, 7]
    for w in upper_walls:
        m.remove_node('%i,0_fr_m' % w)
        m.remove_node('%i,1_fr_m' % w)
        m.remove_node('%i,0_fl_m' % (w + 1))
        m.remove_node('%i,1_fl_m' % (w + 1))

    for w in lower_walls:
        m.remove_node('%i,3_fr_m' % w)
        m.remove_node('%i,4_fr_m' % w)
        m.remove_node('%i,3_fl_m' % (w + 1))
        m.remove_node('%i,4_fl_m' % (w + 1))

    # labelling
    attrs = {}
    bin_coords = []

    for n in range(n_bins):
        bin_x = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        bin_y = random.choice([0, 1, 3, 4])                     # skip the corridor
        bin_coords.append((bin_x, bin_y))

    for x in range(10):
        for y in range(5):
            pos = '%i,%i' % (x, y)
            directions = ['_fu', '_fr', '_fd', '_fl']

            for d in directions:
                bit_str = ''
                for n in range(n_bins):
                    if x == bin_coords[n][0] and y == bin_coords[n][1]:
                        bit_str += '1'
                    else:
                        bit_str += '0'
                attrs[pos + d] = [bit_str]

    nx.set_node_attributes(m, attrs, 'ap')
    return m


def office_spillage_5x10_mdp(r_id, is_bin, n_bins, n_cleaners):
    m = grid_directions_mdp(10, 5)

    m.graph['name'] = 'robot' + r_id
    m.graph['init'] = '%i,%i_fu' % (random.randint(0, 9), random.randint(0, 4))
    m.graph['ap'] = []
    for n in range(n_cleaners):
        m.graph['ap'].append('OFF%i' % n + r_id)
    if is_bin:
        for n in range(n_bins):
            m.graph['ap'].append('BIN%i' % n + r_id)

    # walls
    doors_up = [1, 4, 8]
    doors_down = [1, 3, 5, 7, 9]
    for x in range(10):
        if x not in doors_up:
            m.remove_node('%i,2_fu_m' % x)
            m.remove_node('%i,1_fd_m' % x)
        if x not in doors_down:
            m.remove_node('%i,2_fd_m' % x)
            m.remove_node('%i,3_fu_m' % x)

    upper_walls = [2, 6]
    lower_walls = [1, 3, 5, 7]
    for w in upper_walls:
        m.remove_node('%i,0_fr_m' % w)
        m.remove_node('%i,1_fr_m' % w)
        m.remove_node('%i,0_fl_m' % (w + 1))
        m.remove_node('%i,1_fl_m' % (w + 1))

    for w in lower_walls:
        m.remove_node('%i,3_fr_m' % w)
        m.remove_node('%i,4_fr_m' % w)
        m.remove_node('%i,3_fl_m' % (w + 1))
        m.remove_node('%i,4_fl_m' % (w + 1))

    # labelling
    attrs = {}
    bin_coords = []

    for n in range(n_bins):
        bin_x = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        bin_y = random.choice([0, 1])                     # skip the corridor and lower offices
        bin_coords.append((bin_x, bin_y))

    for x in range(10):
        for y in range(5):
            pos = '%i,%i' % (x, y)
            directions = ['_fu', '_fr', '_fd', '_fl']
            for d in directions:
                bit_str = ''
                for o in range(n_cleaners):          # lower offices
                    if y > 2 and 2*o <= x <= 2*o + 1:
                        bit_str += '1'
                    else:
                        bit_str += '0'
                if is_bin:
                    for n in range(n_bins):     # bins
                        if x == bin_coords[n][0] and y == bin_coords[n][1]:
                            bit_str += '1'
                        else:
                            bit_str += '0'
                attrs[pos + d] = [bit_str]

    nx.set_node_attributes(m, attrs, 'ap')
    return m


def office_critical_doors_5x10_mdp(r_id, n_doors=1):
    assert n_doors <= 8, 'current office layout only allows for 8 doors max.'
    m = grid_directions_mdp(10, 5)

    m.graph['name'] = 'robot' + r_id
    m.graph['init'] = '%i,%i_fu' % (random.randint(0, 9), random.randint(0, 4))
    m.graph['ap'] = ['BIN' + r_id]
    for n in range(n_doors):
        m.graph['ap'].append('DOOR%i' % n + r_id)
    for n in range(n_doors):
        m.graph['ap'].append('FD%i' % n + r_id)

    attrs = {}

    # walls
    crit_sections = 0
    doors_up = [1, 4, 8]
    doors_down = [1, 3, 5, 7, 9]
    for x in range(10):
        if x in doors_up:
            if crit_sections < n_doors:
                facing_door_ap = '0' * ((2 * n_doors) + 1)
                facing_door_ap = replace_char_in_string(facing_door_ap, n_doors + 1 + crit_sections, '1')
                attrs['%i,2_fu' % x] = [facing_door_ap]
                attrs['%i,1_fd' % x] = [facing_door_ap]
                m.remove_edge('%i,2_fu_m' % x, '%i,1_fu' % x)
                m.remove_edge('%i,1_fd_m' % x, '%i,2_fd' % x)
                m.add_node('crit%i_fu' % crit_sections, player=1)
                m.add_node('crit%i_fd' % crit_sections, player=1)
                m.add_edge('%i,2_fu_m' % x, 'crit%i_fu' % crit_sections, prob=1.0)
                m.add_edge('%i,1_fd_m' % x, 'crit%i_fd' % crit_sections, prob=1.0)
                m.add_node('crit%i_fu_m' % crit_sections, player=0)
                m.add_node('crit%i_fd_m' % crit_sections, player=0)
                m.add_edge('crit%i_fu' % crit_sections, 'crit%i_fu_m' % crit_sections, act='move')
                m.add_edge('crit%i_fd' % crit_sections, 'crit%i_fd_m' % crit_sections, act='move')
                m.add_edge('crit%i_fu_m' % crit_sections, '%i,1_fu' % x, prob=1.0)
                m.add_edge('crit%i_fd_m' % crit_sections, '%i,2_fd' % x, prob=1.0)
                crit_sections += 1
        else:
            m.remove_node('%i,2_fu_m' % x)
            m.remove_node('%i,1_fd_m' % x)
        if x in doors_down:
            if crit_sections < n_doors:
                facing_door_ap = '0' * ((2 * n_doors) + 1)
                facing_door_ap = replace_char_in_string(facing_door_ap, n_doors + 1 + crit_sections, '1')
                attrs['%i,2_fd' % x] = [facing_door_ap]
                attrs['%i,3_fu' % x] = [facing_door_ap]
                m.remove_edge('%i,2_fd_m' % x, '%i,3_fd' % x)
                m.remove_edge('%i,3_fu_m' % x, '%i,2_fu' % x)
                m.add_node('crit%i_fu' % crit_sections, player=1)
                m.add_node('crit%i_fd' % crit_sections, player=1)
                m.add_edge('%i,2_fd_m' % x, 'crit%i_fd' % crit_sections, prob=1.0)
                m.add_edge('%i,3_fu_m' % x, 'crit%i_fu' % crit_sections, prob=1.0)
                m.add_node('crit%i_fu_m' % crit_sections, player=0)
                m.add_node('crit%i_fd_m' % crit_sections, player=0)
                m.add_edge('crit%i_fu' % crit_sections, 'crit%i_fu_m' % crit_sections, act='move')
                m.add_edge('crit%i_fd' % crit_sections, 'crit%i_fd_m' % crit_sections, act='move')
                m.add_edge('crit%i_fu_m' % crit_sections, '%i,2_fu' % x, prob=1.0)
                m.add_edge('crit%i_fd_m' % crit_sections, '%i,3_fd' % x, prob=1.0)
                crit_sections += 1
        else:
            m.remove_node('%i,2_fd_m' % x)
            m.remove_node('%i,3_fu_m' % x)

    upper_walls = [2, 6]
    lower_walls = [1, 3, 5, 7]
    for w in upper_walls:
        m.remove_node('%i,0_fr_m' % w)
        m.remove_node('%i,1_fr_m' % w)
        m.remove_node('%i,0_fl_m' % (w + 1))
        m.remove_node('%i,1_fl_m' % (w + 1))

    for w in lower_walls:
        m.remove_node('%i,3_fr_m' % w)
        m.remove_node('%i,4_fr_m' % w)
        m.remove_node('%i,3_fl_m' % (w + 1))
        m.remove_node('%i,4_fl_m' % (w + 1))

    # labelling
    bin_x = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    bin_y = random.choice([0, 1, 3, 4])                     # skip the corridor
    for x in range(10):
        for y in range(5):
            pos = '%i,%i' % (x, y)
            directions = ['_fu', '_fr', '_fd', '_fl']

            for d in directions:
                bit_str = '0' * ((2 * n_doors) + 1)

                if (pos + d) in attrs.keys():
                    bit_str = attrs[pos + d][0]

                if x == bin_x and y == bin_y:
                    bit_str = replace_char_in_string(bit_str, 0, '1')
                attrs[pos + d] = [bit_str]

    for n in range(n_doors):
        bit_str = '0' * ((2 * n_doors) + 1)
        bit_str = replace_char_in_string(bit_str, n+1, '1')
        attrs['crit%i_fu' % n] = [bit_str]
        attrs['crit%i_fd' % n] = [bit_str]

    nx.set_node_attributes(m, attrs, 'ap')

    return m


def office_critical_doors_5x5_mdp(r_id, n_doors):
    assert n_doors <= 4, 'current office layout only allows for 4 doors max.'
    m = grid_directions_mdp(5, 5)

    m.graph['name'] = 'robot' + r_id
    m.graph['init'] = '%i,%i_fu' % (random.randint(0, 4), random.randint(0, 4))
    m.graph['ap'] = ['BIN' + r_id]
    for n in range(n_doors):
        m.graph['ap'].append('DOOR%i' % n + r_id)
    for n in range(n_doors):
        m.graph['ap'].append('FD%i' % n + r_id)

    attrs = {}

    # walls
    crit_sections = 0
    doors_up = [1, 4]
    doors_down = [1, 3]
    for x in range(5):
        if x in doors_up:
            if crit_sections < n_doors:
                facing_door_ap = '0' * ((2 * n_doors) + 1)
                facing_door_ap = replace_char_in_string(facing_door_ap, n_doors + 1 + crit_sections, '1')
                attrs['%i,2_fu' % x] = [facing_door_ap]
                attrs['%i,1_fd' % x] = [facing_door_ap]
                m.remove_edge('%i,2_fu_m' % x, '%i,1_fu' % x)
                m.remove_edge('%i,1_fd_m' % x, '%i,2_fd' % x)
                m.add_node('crit%i_fu' % crit_sections, player=1)
                m.add_node('crit%i_fd' % crit_sections, player=1)
                m.add_edge('%i,2_fu_m' % x, 'crit%i_fu' % crit_sections, prob=1.0)
                m.add_edge('%i,1_fd_m' % x, 'crit%i_fd' % crit_sections, prob=1.0)
                m.add_node('crit%i_fu_m' % crit_sections, player=0)
                m.add_node('crit%i_fd_m' % crit_sections, player=0)
                m.add_edge('crit%i_fu' % crit_sections, 'crit%i_fu_m' % crit_sections, act='move')
                m.add_edge('crit%i_fd' % crit_sections, 'crit%i_fd_m' % crit_sections, act='move')
                m.add_edge('crit%i_fu_m' % crit_sections, '%i,1_fu' % x, prob=1.0)
                m.add_edge('crit%i_fd_m' % crit_sections, '%i,2_fd' % x, prob=1.0)
                crit_sections += 1
        else:
            m.remove_node('%i,2_fu_m' % x)
            m.remove_node('%i,1_fd_m' % x)
        if x in doors_down:
            if crit_sections < n_doors:
                facing_door_ap = '0' * ((2 * n_doors) + 1)
                facing_door_ap = replace_char_in_string(facing_door_ap, n_doors + 1 + crit_sections, '1')
                attrs['%i,2_fd' % x] = [facing_door_ap]
                attrs['%i,3_fu' % x] = [facing_door_ap]
                m.remove_edge('%i,2_fd_m' % x, '%i,3_fd' % x)
                m.remove_edge('%i,3_fu_m' % x, '%i,2_fu' % x)
                m.add_node('crit%i_fu' % crit_sections, player=1)
                m.add_node('crit%i_fd' % crit_sections, player=1)
                m.add_edge('%i,2_fd_m' % x, 'crit%i_fd' % crit_sections, prob=1.0)
                m.add_edge('%i,3_fu_m' % x, 'crit%i_fu' % crit_sections, prob=1.0)
                m.add_node('crit%i_fu_m' % crit_sections, player=0)
                m.add_node('crit%i_fd_m' % crit_sections, player=0)
                m.add_edge('crit%i_fu' % crit_sections, 'crit%i_fu_m' % crit_sections, act='move')
                m.add_edge('crit%i_fd' % crit_sections, 'crit%i_fd_m' % crit_sections, act='move')
                m.add_edge('crit%i_fu_m' % crit_sections, '%i,2_fu' % x, prob=1.0)
                m.add_edge('crit%i_fd_m' % crit_sections, '%i,3_fd' % x, prob=1.0)
                crit_sections += 1
        else:
            m.remove_node('%i,2_fd_m' % x)
            m.remove_node('%i,3_fu_m' % x)

    upper_walls = [2]
    lower_walls = [1]
    for w in upper_walls:
        m.remove_node('%i,0_fr_m' % w)
        m.remove_node('%i,1_fr_m' % w)
        m.remove_node('%i,0_fl_m' % (w + 1))
        m.remove_node('%i,1_fl_m' % (w + 1))

    for w in lower_walls:
        m.remove_node('%i,3_fr_m' % w)
        m.remove_node('%i,4_fr_m' % w)
        m.remove_node('%i,3_fl_m' % (w + 1))
        m.remove_node('%i,4_fl_m' % (w + 1))

    # labelling
    bin_x = random.choice([0, 1, 2, 3, 4])
    bin_y = random.choice([0, 1, 3, 4])                     # skip the corridor
    for x in range(10):
        for y in range(5):
            pos = '%i,%i' % (x, y)
            directions = ['_fu', '_fr', '_fd', '_fl']

            for d in directions:
                bit_str = '0' * ((2 * n_doors) + 1)

                if (pos + d) in attrs.keys():
                    bit_str = attrs[pos + d][0]

                if x == bin_x and y == bin_y:
                    bit_str = replace_char_in_string(bit_str, 0, '1')
                attrs[pos + d] = [bit_str]

    for n in range(n_doors):
        bit_str = '0' * ((2 * n_doors) + 1)
        bit_str = replace_char_in_string(bit_str, n+1, '1')
        attrs['crit%i_fu' % n] = [bit_str]
        attrs['crit%i_fd' % n] = [bit_str]

    nx.set_node_attributes(m, attrs, 'ap')

    return m


def replace_char_in_string(string, pos, c):
    new_str = list(string)
    new_str[pos] = c
    new_str = ''.join(new_str)
    return new_str
