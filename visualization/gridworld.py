import pygame
import time
import pickle
import random


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
            robot_view = RobotView(robot.name, robot_id, self.WIDTH * 0.5, self.HEIGHT * 0.5)
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

        # display the robots
        self.sprites_list.draw(self.screen)

        # flip the renderer buffer
        pygame.display.flip()

    def idle(self, idle_time):
        pass

    def run_step(self, states_dict):
        self.frame_count += 1
        if self.frame_count >= self.SPEED:
            self.frame_count = 0
            self.simulate_step()

        # update robot views
        for robot_id, robot in enumerate(self.robots):
            robot_view = self.robot_views[robot_id]
            current_coords = states_dict[robot.current_state[0]]
            displace_x = ((self.WIDTH + self.MARGIN)/2) - (robot_view.rect.width / 2)
            displace_y = ((self.HEIGHT + self.MARGIN) / 2) - (robot_view.rect.height / 2)
            robot_view.rect.x = current_coords[1] * (self.WIDTH + self.MARGIN) + displace_x
            robot_view.rect.y = current_coords[0] * (self.HEIGHT + self.MARGIN) + displace_y

        # render the results
        self.render()

    def simulate_step(self):
        next_obs = ''
        next_ap = []
        for robot in self.robots:
            # start in a player-1 state
            mpd_state = robot.current_state[0]
            action = robot.strategy[robot.current_state]
            prob_state = None
            for succ in robot.mdp.successors(mpd_state):
                if robot.mdp.edges[mpd_state, succ]['act'] == action:
                    prob_state = succ

            # compute probabilistic outcome of mdp action
            outcomes = []
            probs = []
            for succ in robot.mdp.successors(prob_state):
                outcomes.append(succ)
                probs.append(robot.mdp.edges[prob_state, succ]['prob'])
            choice = random.choices(outcomes, probs)[0]
            next_obs += robot.mdp.nodes[choice]['ap'][0]
            next_ap.extend(robot.mdp.graph['ap'])

        # now we have player-2 choices

    def simulate_agents(self, states_dict):
        next_time = time.time()

        running = True
        while running:
            # handle all events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:            # hit a key
                    if event.key == pygame.K_ESCAPE:        # ESC key
                        running = False
                elif event.type == pygame.QUIT:             # press X in window
                    running = False
            # handle game state
            now_time = time.time()
            self.idle(max(0., next_time - now_time))
            if now_time >= next_time:
                self.run_step(states_dict)
                next_time = now_time + (1 / self.FPS)


if __name__ == '__main__':
    pickled_agents = pickle.load(open('data/agents_converged_results.p', 'rb'))

    # mdp player-1-states to coords
    mdp_states_dict = {'end_top':               (2, 0),
                       'corridor_top':          (2, 1),
                       'corridor_top_no_turn':  (2, 1),
                       'crit':                  (2, 2),
                       'corridor_bot':          (2, 3),
                       'corridor_bot_no_turn':  (2, 3),
                       'end_bot':               (2, 4)}

    # build grid structure
    ex_grid = [[0 for col in range(5)] for row in range(5)]
    for i in range(5):
        ex_grid[2][i] = 1
    ex_grid[2][2] = 2

    # set current state of agents
    for agent in pickled_agents:
        agent.current_state = agent.synth.graph['init']

    gridworld = GridWorld(grid=ex_grid, robots=pickled_agents, screen_x=500, screen_y=500)
    gridworld.simulate_agents(mdp_states_dict)
