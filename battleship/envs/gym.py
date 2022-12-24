import gym
from gym import spaces
from battleship.battleship import Game, Player, Ship
import numpy as np
import copy


class MyEnv(gym.Env):
    def __init__(self):
        self.action_space = spaces.Discrete(100)
        # observation space is a 10x10 grid of
        # 0: unknown
        # 1: miss
        # 2: hit

        self.observation_space = spaces.Box(low=0, high=2, shape=(10, 10), dtype=np.int8)
        self.game = Game()
        self.screen = None
        self.clock = None
        self.score = 0

    def step(self, action):
        if self.game.victory != -1:
            return self.game.players[0].guesses, 0, True, {}
        x, y = action // 10, action % 10
        # if it is an illegal move, the reward is -10
        if not self.game.check_legal(x, y, 0):
            self.score -= 10
            self.game.step += 1
            return self.game.players[0].guesses, -10, False, {}
        self.game.turn(x, y)
        # miss has a reward of -1,
        # hit has a reward of 1
        # sink has a reward of 2 * ship size
        reward = 0
        if self.game.players[0].guesses[x][y] == 2:
            # if the ship has sunk, reward the player with 2 * ship size
            for ship in self.game.players[1].ships:
                if (x, y) in ship.squares:
                    if ship.size == 0:
                        reward = 3 * len(ship.squares)
            else:
                reward = 1
        else:
            reward = -1
        done = self.game.victory != -1
        if done:
            reward = 10
        self.score += reward
        return self.game.players[0].guesses, reward, done, {}

    def reset(self):
        p = Player(ships=[
            Ship(4, [(0, 0), (0, 1), (0, 2), (0, 3)]),
            Ship(3, [(2, 0), (2, 1), (2, 2)]),
            Ship(3, [(4, 0), (4, 1), (4, 2)]),
            Ship(2, [(6, 0), (6, 1)]),
            Ship(2, [(8, 0), (8, 1)]),
            Ship(2, [(0, 6), (0, 7)]),
            Ship(1, [(2, 6)]),
            Ship(1, [(4, 6)]),
            Ship(1, [(6, 6)]),
            Ship(1, [(8, 6)])
        ]
        )
        # p.random_place_ships()

        b = copy.deepcopy(p)
        self.game = Game([p, b])
        self.score = 0
        return self.game.players[0].guesses

    def render(self, mode='human'):
        import pygame
        from pygame import gfxdraw
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((1100, 600))
        self.surf = pygame.Surface((1100, 600))
        self.surf.fill((255, 255, 255))
        if self.clock is None:
            self.clock = pygame.time.Clock()
        # render text in white in the middle of the screen under the grids with the steps taken
        # the text must be cleared, so that the previous text is not visible
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont("monospace", 25)
        label = font.render("Step: " + str(self.game.step), 1, (255, 255, 255))
        self.screen.blit(label, (550 - label.get_width() // 2, 500))
        label = font.render("Score: " + str(self.score), 1, (255, 255, 255))
        self.screen.blit(label, (550 - label.get_width() // 2, 550))

        for x in range(10):
            for y in range(10):
                # draw the hits of the opponent in red
                if self.game.players[1].guesses[x][y] == 2:
                    gfxdraw.box(self.screen, (x * 40 + 50, y * 40 + 50, 40, 40), (255, 0, 0))
                # draw the misses of the opponent in dark grey
                elif self.game.players[1].guesses[x][y] == 1:
                    gfxdraw.box(self.screen, (x * 40 + 50, y * 40 + 50, 40, 40), (64, 64, 64))
                # draw our ships in blue
                elif any((x, y) in ship.squares for ship in self.game.players[0].ships):
                    gfxdraw.box(self.screen, (x * 40 + 50, y * 40 + 50, 40, 40), (0, 0, 255))
                else:
                    gfxdraw.box(self.screen, (x * 40 + 50, y * 40 + 50, 40, 40), (128, 128, 128))

        for x in range(10):
            for y in range(10):
                if self.game.players[0].guesses[x][y] == 1:
                    gfxdraw.box(self.screen, (x * 40 + 50 + 600, y * 40 + 50, 40, 40), (64, 64, 64))
                elif self.game.players[0].guesses[x][y] == 2:
                    gfxdraw.box(self.screen, (x * 40 + 50 + 600, y * 40 + 50, 40, 40), (255, 0, 0))
                else:
                    gfxdraw.box(self.screen, (x * 40 + 50 + 600, y * 40 + 50, 40, 40), (128, 128, 128))

        for i in range(10):
            pygame.draw.line(self.screen, (0, 0, 0), (50 + i * 40, 50), (50 + i * 40, 450), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (50 + i * 40 + 600, 50), (50 + i * 40 + 600, 450), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (50, 50 + i * 40), (450, 50 + i * 40), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (50 + 600, 50 + i * 40), (450 + 600, 50 + i * 40), 2)

        pygame.draw.line(self.screen, (0, 0, 0), (50, 50), (450, 50), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (50, 450), (450, 450), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (50, 50), (50, 450), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (450, 50), (450, 450), 2)

        pygame.draw.line(self.screen, (0, 0, 0), (50 + 600, 50), (450 + 600, 50), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (50 + 600, 450), (450 + 600, 450), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (50 + 600, 50), (50 + 600, 450), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (450 + 600, 50), (450 + 600, 450), 2)

        pygame.draw.line(self.screen, (0, 0, 0), (50, 50), (50 + 600, 50), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (50, 450), (50 + 600, 450), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (50, 50), (50, 450), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (450, 50), (450, 450), 2)

        pygame.draw.line(self.screen, (0, 0, 0), (50 + 600, 50), (50 + 600, 450), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (450 + 600, 50), (450 + 600, 450), 2)

        # now we need to pump the event queue, so the window doesn't freeze
        pygame.event.pump()
        pygame.display.flip()
        self.clock.tick(60)

    def close(self):
        if self.screen is not None:
            import pygame
            self.screen = None
            pygame.display.quit()
            pygame.quit()
