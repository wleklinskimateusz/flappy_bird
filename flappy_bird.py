import pygame
import neat
import time
import os
import random
pygame.font.init()

def load_file(name):
    return pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", name + ".png")))

def distance(x1, y1, x2, y2):
    d = ((x2-x1)**2 + (y2-y1)**2) ** 0.5
    return d

def text_objects(text, font):
    textSurface = font.render(text, True, (0, 0, 0))
    return textSurface, textSurface.get_rect()

class Bird:
    IMGS = [
        load_file("bird1"),
        load_file("bird2"),
        load_file('bird3'),
        ]
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5 # negative means that it goes upwards
        self.tick_count = 0
        self.height = self = self.y

    def move(self):
        self.tick_count += 1

        displacement = self.vel*self.tick_count + 1.5*self.tick_count**2 # vertical displacement

        if displacement >= 16:
            displacement = abs(displacement)/displacement * 16
        if displacement < 0:
            displacement -= 2

        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4+1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt >- -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION * 2

        self.blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def blitRotateCenter(self, surf, image, topleft, angle):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

        surf.blit(rotated_image, new_rect.topleft)

class Pipe:
    GAP = 200
    PIPE_IMG = load_file("pipe")

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(self.PIPE_IMG, False, True)
        self.PIPE_BOTTOM = self.PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self, vel):
        self.x -= vel

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    IMG = load_file("base")
    WIDTH = IMG.get_width()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self, vel):
        self.x1 -= vel
        self.x2 -= vel

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


class Game:

    WIN_WIDTH = 500
    WIN_HEIGHT = 800
    BG_IMG = load_file("bg")

    STAT_FONT = pygame.font.SysFont("comicsans", 50)
    LARGE_FONT = pygame.font.SysFont("comicsans", 100)

    def __init__(self):
        self.nets =[]
        self.ge =[]
        self.birds = []
        self.base = None
        self.pipes = []
        self.win = None
        self.clock = None
        self.vel = None
        self.generation = 0
        self.config = None



    def run(self):

        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config-feedforward.txt")

        self.config = neat.config.Config(
                                neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

        p = neat.Population(self.config)
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        self.winner = p.run(self.main,50)


    def setup(self, genomes=None):

        self.nets =[]
        self.ge =[]
        self.birds = []

        # gets neural network
        if genomes:
            self.generation += 1
            for _, g in genomes:
                net = neat.nn.FeedForwardNetwork.create(g, self.config)
                self.nets.append(net)
                self.birds.append(Bird(230, 350))
                g.fitness = 0
                self.ge.append(g)

        self.base = Base(730)
        self.pipes = [Pipe(600)]
        self.score = 0
        self.vel = 5
        self.win = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.last = 0

        self.run_loop = True

    def check_if_closed(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run_loop = False
                pygame.quit()
                quit()

    def check_for_colisions(self):
        for pipe in self.pipes:
            for x, bird in enumerate(self.birds):
                if pipe.collide(bird):
                    self.ge[x].fitness -= 1 # encourages birds not to hit the pipe
                    self.birds.pop(x)
                    self.nets.pop(x)
                    self.ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    self.add_pipe = True

    def check_for_bird_death(self):
        for x, bird in enumerate(self.birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                self.birds.pop(x)
                self.nets.pop(x)
                self.ge.pop(x)

    def handle_pipe_moving(self):
        for pipe in self.pipes:
            pipe.move(self.vel)

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                self.removed.append(pipe)

        if self.add_pipe:
            self.score += 1
            for g in self.ge:
                g.fitness += 5
            self.pipes.append(Pipe(600))

        for pipe in self.removed:
            self.pipes.remove(pipe)

    def speed_up(self):
        if self.score == self.last + 5:
            self.vel += 1
            self.last = self.score

    def handle_jumps(self):
        for x, bird in enumerate(self.birds):
            bird.move()
            self.ge[x].fitness += 0.1
            self.decide_for_jump(bird, x)

    def draw_window(self):
        self.win.blit(self.BG_IMG, (0, 0))
        for pipe in self.pipes:
            pipe.draw(self.win)

        text = self.STAT_FONT.render("Score: " + str(self.score), 1, (255, 255, 255))
        self.win.blit(text, (self.WIN_WIDTH - 10 - text.get_width(), 10))

        text = self.STAT_FONT.render("Gen: " + str(self.generation), 1, (255, 255, 255))
        self.win.blit(text, (10, 10))

        text = self.STAT_FONT.render("Speed: " + str(self.vel), 1, (255, 255, 255))
        self.win.blit(text, (10, 50))

        self.base.draw(self.win)

        for bird in self.birds:
            bird.draw(self.win)

        pygame.display.update()

    def distinguish_pipes(self):
        pipe_ind = 0
        other_pipe = 0
        if len(self.pipes) > 1:
            other_pipe = 1
        if len(self.birds) > 0:
            if len(self.pipes) > 1 and self.birds[0].x > self.pipes[0].x + self.pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
                other_pipe = 0

        return (pipe_ind, other_pipe)

    def decide_for_jump(self, bird, x):

        (closer_pipe, further_pipe) = self.distinguish_pipes()

        output = self.nets[x].activate((bird.y,
                                    distance(
                                        bird.x, bird.y,
                                        self.pipes[closer_pipe].x, self.pipes[closer_pipe].height
                                    ),
                                    distance(
                                        bird.x, bird.y,
                                        self.pipes[closer_pipe].x, self.pipes[closer_pipe].bottom),
                                    distance(
                                        bird.x, bird.y,
                                        self.pipes[further_pipe].x, self.pipes[further_pipe].height
                                    ),
                                    distance(
                                        bird.x, bird.y,
                                        self.pipes[further_pipe].x, self.pipes[further_pipe].bottom)
                                    ))

        if output[0] > 0.5:
            bird.jump()


    def button(self, msg, x, y, w, h, ic, ac, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pygame.draw.rect(self.win, ac,(x,y,w,h))
            if click[0] == 1 and action != None:
                action()

        else:
            pygame.draw.rect(self.win, ic,(x,y,w,h))
        textSurf, textRect = text_objects(msg, self.STAT_FONT)
        textRect.center = ( (x+(w/2)), (y+(h/2)) )
        self.win.blit(textSurf, textRect)

    def end(self):
        pygame.quit()
        quit()

    def intro(self):
        self.setup()

        while self.intro:
            self.check_if_closed()
            self.win.fill((255, 255, 255))
            # largeText = pygame.font.Font('freesansbold.tff', 115)
            TextSurf, TextRect = text_objects("Flappy Bird", self.LARGE_FONT)
            TextRect.center = (self.WIN_WIDTH/2, self.WIN_HEIGHT/2)
            self.win.blit(TextSurf, TextRect)

            mouse = pygame.mouse.get_pos()

            if 150+100 > mouse[0] > 150 and 450+50 > mouse[1] > 450:
                pygame.draw.rect(self.win, (0, 150, 0), (150, 450, 100, 50))
            else:
                pygame.draw.rect(self.win, (0, 255, 0), (150, 450, 100, 50))



            self.button("let the AI play", 150, 450, 250, 50, (0, 250, 0), (0, 200, 0), self.run)
            self.button("let me play", 150, 500, 200, 50, (100, 100, 250), (100, 100, 200), None)
            self.button("Quit", 150, 550, 100, 50, (250, 0, 0), (200, 0, 0), self.end)

            pygame.display.update()
            self.clock.tick(15)


    def main(self, genome, config):
        self.setup(genome)

        while self.run_loop:
            self.clock.tick(30)
            self.add_pipe = False
            self.removed = []

            self.check_if_closed()

            self.handle_jumps()

            self.check_for_colisions()

            self.handle_pipe_moving()
            self.base.move(self.vel)
            self.speed_up()

            self.check_for_bird_death()
            if len(self.birds) == 0:
                self.run_loop = False


            self.draw_window()
