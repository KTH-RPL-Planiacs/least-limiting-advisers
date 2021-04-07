import pygame
import time
import pickle


class GridWorld:

    def __init__(self, grid, screen_x=500, screen_y=500, cell_margin=5):

        # define colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
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
        self.SPEED = 10     # frames per move
        self.frame_count = 0

        pygame.init()
        pygame.font.init()

        # set the width and height of the screen (width , height)
        self.size = (screen_x, screen_y)
        self.screen = pygame.display.set_mode(self.size)

        self.font = pygame.font.SysFont('arial', 20)
        pygame.display.set_caption("Grid world")

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
                if self.grid[row][col] == 1:
                    self.color = self.BLACK
                elif self.grid[row][col] == 2:
                    self.color = self.BLUE
                else:
                    self.color = self.WHITE
                pygame.draw.rect(self.screen,
                                 self.color,
                                 [(self.MARGIN + self.WIDTH) * col + self.MARGIN,
                                  (self.MARGIN + self.HEIGHT) * row + self.MARGIN,
                                  self.WIDTH,
                                  self.HEIGHT])
        # flip the renderer buffer
        pygame.display.flip()

    def idle(self, idle_time):
        pass

    def run_frame(self):
        self.frame_count += 1
        if self.frame_count >= self.SPEED:
            self.frame_count = 0
            if self.cell_count < len(self.grid):
                self.grid[self.cell_count][self.cell_count] = 2
            self.cell_count += 1
        self.render()

    def loop(self):
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
                self.run_frame()
                next_time = now_time + (1 / self.FPS)


if __name__ == '__main__':
    agents = pickle.load(open('../data/agents_converged_results.p', 'rb'))

    # build grid structure
    ex_grid = [[1 for col in range(5)] for row in range(5)]
    for i in range(5):
        ex_grid[2][i] = 0

    gridworld = GridWorld(grid=ex_grid, screen_x=500, screen_y=500)
    gridworld.loop()
