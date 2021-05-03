import pygame
import time
import pickle
import random
from advisers import AdviserType

from agent_synth_game import sog_fits_to_guard


class RobotView(pygame.sprite.Sprite):

    def __init__(self, name, robot_id, width, height):
        super().__init__()
        self.robot_id = robot_id
        self.image = pygame.image.load('data/robot%i.png' % (robot_id+1)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(width), int(height)))
        self.rect = self.image.get_rect()
        # self.image.set_colorkey((255, 255, 255))
        self.name = name


class GridWorld:

    def __init__(self, grid, robots, screen_x=500, screen_y=500, cell_margin=5):

        # define colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 150, 150)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)

        # cell dimensions
        self.WIDTH = int((screen_x / len(grid[0])) - cell_margin)
        self.HEIGHT = int((screen_y / len(grid)) - cell_margin)
        self.MARGIN = cell_margin
        self.color = self.WHITE

        # grid info
        self.grid = grid
        self.cell_count = 0

        # simulation speed
        self.FPS = 60       # frames per second
        self.SPEED = 60     # frames per move
        self.frame_count = 0

        pygame.init()
        pygame.font.init()

        # set the width and height of the screen (width , height)
        self.size = (screen_x, screen_y)
        self.screen = pygame.display.set_mode(self.size)

        self.font = pygame.font.SysFont('arial', 20)
        pygame.display.set_caption("Grid world")

        # agents
        self.robots = robots
        self.robot_views = []
        self.sprites_list = pygame.sprite.Group()
        for robot_id, robot in enumerate(self.robots):
            robot_view = RobotView(robot.name, robot_id, self.WIDTH * 0.6, self.HEIGHT * 0.6)
            self.robot_views.append(robot_view)
            self.sprites_list.add(robot_view)

    def text_objects(self, text, font):
        text_surface = font.render(text, True, self.BLACK)
        return text_surface, text_surface.get_rect()

    def draw_cell(self, nodes):
        for node in nodes:
            row = node[1][0]
            column = node[1][1]
            value = node[0]
            pygame.draw.rect(self.screen,
                             self.BLUE,
                             [(self.MARGIN + self.WIDTH) * column + self.MARGIN,
                              (self.MARGIN + self.HEIGHT) * row + self.MARGIN,
                              self.WIDTH,
                              self.HEIGHT])
            text_surf, text_rect = self.text_objects(str(value), self.font)
            text_rect.center = ((self.MARGIN + self.WIDTH) * column + 4 * self.MARGIN,
                                (self.MARGIN + self.HEIGHT) * row + 4 * self.MARGIN)
            self.screen.blit(text_surf, text_rect)

    def render(self):
        # black the whole screen
        self.screen.fill(self.BLACK)

        # draw the grid
        for row in range(len(self.grid)):
            for col in range(len(self.grid[0])):
                if self.grid[row][col] == 0:
                    self.color = self.BLACK
                elif self.grid[row][col] == 1:
                    self.color = self.WHITE
                elif self.grid[row][col] == 2:
                    self.color = self.RED
                else:
                    self.color = self.BLUE

                pygame.draw.rect(self.screen,
                                 self.color,
                                 [(self.MARGIN + self.WIDTH) * col + self.MARGIN,
                                  (self.MARGIN + self.HEIGHT) * row + self.MARGIN,
                                  self.WIDTH,
                                  self.HEIGHT])

        # walls
        pygame.draw.rect(self.screen,
                         self.BLACK,
                         [(self.MARGIN + self.WIDTH) * 0 + self.MARGIN,
                          (self.MARGIN + self.HEIGHT) * 4 + self.MARGIN,
                          (self.MARGIN + self.WIDTH) * 2, self.MARGIN * 2])
        pygame.draw.rect(self.screen,
                         self.BLACK,
                         [(self.MARGIN + self.WIDTH) * 3 + self.MARGIN,
                          (self.MARGIN + self.HEIGHT) * 4 + self.MARGIN,
                          (self.MARGIN + self.WIDTH) * 4, self.MARGIN * 2])
        pygame.draw.rect(self.screen,
                         self.BLACK,
                         [(self.MARGIN + self.WIDTH) * 8 + self.MARGIN,
                          (self.MARGIN + self.HEIGHT) * 4 + self.MARGIN,
                          (self.MARGIN + self.WIDTH) * 2, self.MARGIN * 2])

        pygame.draw.rect(self.screen,
                         self.BLACK,
                         [(self.MARGIN + self.WIDTH) * 0 + self.MARGIN,
                          (self.MARGIN + self.HEIGHT) * 6 + self.MARGIN,
                          (self.MARGIN + self.WIDTH) * 2, self.MARGIN * 2])
        pygame.draw.rect(self.screen,
                         self.BLACK,
                         [(self.MARGIN + self.WIDTH) * 3 + self.MARGIN,
                          (self.MARGIN + self.HEIGHT) * 6 + self.MARGIN,
                          (self.MARGIN + self.WIDTH) * 4, self.MARGIN * 2])
        pygame.draw.rect(self.screen,
                         self.BLACK,
                         [(self.MARGIN + self.WIDTH) * 8 + self.MARGIN,
                          (self.MARGIN + self.HEIGHT) * 6 + self.MARGIN,
                          (self.MARGIN + self.WIDTH) * 2, self.MARGIN * 2])
        pygame.draw.rect(self.screen,
                         self.BLACK,
                         [(self.MARGIN + self.WIDTH) * 5 + self.MARGIN,
                          (self.MARGIN + self.HEIGHT) * 0,
                          self.MARGIN * 2, (self.MARGIN + self.HEIGHT) * 4])
        pygame.draw.rect(self.screen,
                         self.BLACK,
                         [(self.MARGIN + self.WIDTH) * 5 + self.MARGIN,
                          (self.MARGIN + self.HEIGHT) * 6,
                          self.MARGIN * 2, (self.MARGIN + self.HEIGHT) * 4])

        # display the robots
        self.sprites_list.draw(self.screen)

        # flip the renderer buffer
        pygame.display.flip()

    def idle(self, idle_time):
        pass

    def run_step(self, states_dict):
        self.frame_count += 1
        if self.frame_count >= self.SPEED:
            for robot in self.robots:
                robot.current_state = robot.next_state

            self.frame_count = 0
            self.compute_next_step()

        # update robot views
        for robot_id, robot in enumerate(self.robots):
            robot_view = self.robot_views[robot_id]
            if isinstance(robot.current_state[0], tuple):
                current_coords = states_dict[robot.current_state[0][0]]
            else:
                current_coords = states_dict[robot.current_state[0]]
            if isinstance(robot.next_state[0], tuple):
                next_coords = states_dict[robot.next_state[0][0]]
            else:
                next_coords = states_dict[robot.next_state[0]]

            displace_x = ((self.WIDTH + self.MARGIN)/2) - (robot_view.rect.width / 2)
            displace_y = ((self.HEIGHT + self.MARGIN) / 2) - (robot_view.rect.height / 2)
            current_posx = current_coords[1] * (self.WIDTH + self.MARGIN) + displace_x
            current_posy = current_coords[0] * (self.HEIGHT + self.MARGIN) + displace_y
            next_posx = next_coords[1] * (self.WIDTH + self.MARGIN) + displace_x
            next_posy = next_coords[0] * (self.HEIGHT + self.MARGIN) + displace_y

            t = self.frame_count / self.SPEED
            t = t * t * (3 - 2 * t)

            robot_view.rect.x = int(current_posx * (1 - t) + next_posx * t)
            robot_view.rect.y = int(current_posy * (1 - t) + next_posy * t)

        # render the results
        self.render()

    def compute_next_step(self):
        next_obs = ''
        next_ap = []
        for robot in self.robots:
            # start in a player-1 state
            if isinstance(robot.current_state[0], tuple):
                # its a promise node
                mpd_state = robot.current_state[0][0]
            else:
                mpd_state = robot.current_state[0]
            action = robot.strategy[robot.current_state]
            prob_state = None
            for succ in robot.mdp.successors(mpd_state):
                if robot.mdp.edges[mpd_state, succ]['act'] == action:
                    prob_state = succ
                    break

            # compute probabilistic outcome of mdp action
            outcomes = []
            probs = []
            for succ in robot.mdp.successors(prob_state):
                outcomes.append(succ)
                probs.append(robot.mdp.edges[prob_state, succ]['prob'])
            choice = random.choices(outcomes, probs)[0]
            robot.mdp_choice = choice

            next_obs += robot.mdp.nodes[choice]['ap'][0]
            next_ap.extend(robot.mdp.graph['ap'])

        # now we have player-2 choices, now move the synth game
        for robot in self.robots:
            action = robot.strategy[robot.current_state]
            p2_state = None
            for succ in robot.synth.successors(robot.current_state):
                if robot.synth.edges[robot.current_state, succ]['act'] == action:
                    p2_state = succ
                    break
            # find the p2 action that matches the next_obs, next_ap
            # first, skip fairness nodes
            if len(p2_state) == 3 and p2_state[2] == 'fair':
                p2_state = (p2_state[0], p2_state[1])
            prob_state = None
            for succ in robot.synth.successors(p2_state):
                sog = robot.synth.edges[p2_state, succ]['guards']
                matched_guards = sog_fits_to_guard(next_obs, sog, next_ap, robot.synth.graph['env_ap'])
                if len(matched_guards) > 0:
                    prob_state = succ
                    break
            # make the choice decided probabilistically earlier in mdp
            for succ in robot.synth.successors(prob_state):
                if succ[1] == 'promise' and succ[0][0] == robot.mdp_choice:
                    # check probabilistically if we need to fulfill a promise
                    promise_state = succ
                    outcomes = []
                    probs = []
                    for succsucc in robot.synth.successors(promise_state):
                        edge_data = robot.synth.edges[promise_state, succsucc]
                        if 'pre' in edge_data.keys():
                            fits = sog_fits_to_guard(next_obs, [edge_data['pre'][0]], next_ap, edge_data['pre'][1])
                            if len(fits) > 0:
                                outcomes.append(succsucc)
                        else:
                            outcomes.append(succsucc)
                    robot.next_state = random.choice(outcomes)

                elif succ[0] == robot.mdp_choice:
                    robot.next_state = succ
                    break

    def simulate_agents(self, states_dict):
        next_time = time.time()

        running = True
        simulate = False
        while running:
            # handle all events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:            # hit a key
                    if event.key == pygame.K_ESCAPE:        # ESC key
                        running = False
                    if event.key == pygame.K_SPACE:
                        simulate = True
                elif event.type == pygame.QUIT:             # press X in window
                    running = False
            # handle game state
            now_time = time.time()
            self.idle(max(0., next_time - now_time))
            if now_time >= next_time:
                if simulate:
                    self.run_step(states_dict)
                next_time = now_time + (1 / self.FPS)


if __name__ == '__main__':
    # pickled_agents = pickle.load(open('data/agents_converged_results_symmetric_corridor.p', 'rb'))
    #
    # # mdp player-1-states to coords
    # mdp_states_dict = {
    #     'crit':                 (2, 2),
    #     'end_top':              (0, 2),
    #     'corridor_top':         (1, 2),
    #     'corridor_top_no_turn': (1, 2),
    #     'corridor_bot':         (3, 2),
    #     'corridor_bot_no_turn': (3, 2),
    #     'end_bot':              (4, 2),
    #     'end_left':             (2, 0),
    #     'corridor_left':        (2, 1),
    #     'corridor_left_no_turn': (2, 1),
    #     'end_right':              (2, 4),
    #     'corridor_right':         (2, 3),
    #     'corridor_right_no_turn': (2, 3)
    # }

    # # build grid structure
    # ex_grid = [[0 for col in range(5)] for row in range(5)]
    # for i in range(5):
    #     ex_grid[2][i] = 1
    #     ex_grid[i][2] = 1
    # ex_grid[2][2] = 2

    pickled_agents = pickle.load(open('data/agents_results_office_roomtest.p', 'rb'))
    mdp_states_dict = {}
    for x in range(10):
        for y in range(10):
            mdp_states_dict["%i,%i" % (x,y)] = (x,y)

    # build grid structure
    ex_grid = [[1 for col in range(10)] for row in range(10)]

    # set current state of agents
    for agent in pickled_agents:
        agent.current_state = agent.synth.graph['init']

    # safety print
    for agent in pickled_agents:
        print('Safety Advisers for Agent %s:' % agent.name)
        for adviser in agent.own_advisers:
            if not adviser.adv_type == AdviserType.SAFETY:
                continue

            adviser.print_advice()
        print('')
    # fairness print
    for agent in pickled_agents:
        print('Fairness Advisers for Agent %s:' % agent.name)
        for adviser in agent.own_advisers:
            if not adviser.adv_type == AdviserType.FAIRNESS:
                continue
            adviser.print_advice()
        print('')

    gridworld = GridWorld(grid=ex_grid, robots=pickled_agents, screen_x=1000, screen_y=1000)
    gridworld.compute_next_step()
    gridworld.simulate_agents(mdp_states_dict)
