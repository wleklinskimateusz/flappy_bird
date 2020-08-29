from library.setup import *

class Game:

    WIN_WIDTH = 500
    WIN_HEIGHT = 800
    BG_IMG = load_file("bg")

    STAT_FONT = pygame.font.SysFont("comicsans", 50)
    MID_FONT = pygame.font.SysFont("comicsans", 75)
    LARGE_FONT = pygame.font.SysFont("comicsans", 100)

    POINT = pygame.mixer.Sound('effects/point.wav')
    DIE = pygame.mixer.Sound('effects/die.wav')
    HIT = pygame.mixer.Sound("effects/hit.wav")
    WING = pygame.mixer.Sound('effects/wing.wav')

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
        self.pause = False
        self.run_loop = False
        self.menu = True
        self.player = None
        self.over = False
        self.player_choosing = False
        self.folder_name = "players"
        self.players = []
        self.data_files = []
        self.AI = None
        self.initial_population = 0
        self.board = False


### VIEWS ###
    def intro(self):
        """
        Main Menu
        """
        self.player_choosing = False

        self.setup()
        self.menu = True
        if self.player:
            self.player.save_data()
        self.player = None
        self.get_players()

        while self.menu:
            self.check_events()
            self.win.blit(self.BG_IMG, (0, 0))
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
            self.button("let me play", 150, 500, 200, 50, (100, 100, 250), (100, 100, 200), self.choose_player)
            self.button("leaderboard", 150, 550, 200, 50, (150, 200, 100), (200, 180, 200), self.leaderboard)
            self.button("Quit", 150, 600, 100, 50, (250, 0, 0), (200, 0, 0), self.end)

            pygame.display.update()
            self.clock.tick(15)

    def choose_player(self):
        """
        Lets users choose their players
        """
        self.player_choosing = True
        self.player = None
        frame = 0
        action = None
        colors = []
        for player in self.players:
            color = [random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)]
            colors.append(color)

        while self.player_choosing:
            frame += 1
            self.clock.tick(30)
            self.check_events()
            self.win.blit(self.BG_IMG, (0, 0))
            # largeText = pygame.font.Font('freesansbold.tff', 115)
            TextSurf, TextRect = text_objects("Choose your player", self.MID_FONT)
            TextRect.center = (self.WIN_WIDTH/2, self.WIN_HEIGHT/2)
            self.win.blit(TextSurf, TextRect)

            mouse = pygame.mouse.get_pos()

            if 150+100 > mouse[0] > 150 and 450+50 > mouse[1] > 450:
                pygame.draw.rect(self.win, (0, 150, 0), (150, 450, 100, 50))
            else:
                pygame.draw.rect(self.win, (0, 255, 0), (150, 450, 100, 50))



            for i, player in enumerate(self.players):
                if frame > 5:
                    action = lambda: self.play(i)
                if player.nick != "AI":
                    self.button(f"{player}",
                                150, 450 + 50 * i, 250, 50,
                                (colors[i][0], colors[i][1], colors[i][2]),
                                (colors[i][0]+50, colors[i][1]+50, colors[i][2]+50),
                                action) #

            pygame.display.update()

    def leaderboard(self):
        """
        A View to display players and theirs score
        """
        self.setup()
        self.board = True

        while self.board:
            self.clock.tick(30)
            self.check_events()
            self.win.blit(self.BG_IMG, (0, 0))
            # largeText = pygame.font.Font('freesansbold.tff', 115)
            TextSurf, TextRect = text_objects("Leader Board", self.MID_FONT)
            TextRect.center = (self.WIN_WIDTH/2, self.WIN_HEIGHT/4)
            self.win.blit(TextSurf, TextRect)

            for i, player in enumerate(self.sort_players()):
                TextSurf, TextRect = text_objects(f"player: {player}, score: {player.sum_score}", self.STAT_FONT)
                TextRect.center = (self.WIN_WIDTH/2, self.WIN_HEIGHT/4 + 100 +50 * i)
                self.win.blit(TextSurf, TextRect)

            self.button("Menu",150,500,200,50,(200, 200, 255), (100, 100, 150),self.intro)

            pygame.display.update()




    def play(self, x):
        """
        When user plays
        """
        self.player = self.players[x]
        self.run_loop = True
        self.main()

    def run(self):
        """
        When AI plays the game
        """
        self.generation = 0
        for pl in self.players:
            if pl.nick == "AI":
                self.AI = pl
        self.AI.reset()


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


    def paused(self):
        """
        View of a pause
        """
        TextSurf, TextRect = text_objects("Paused", self.LARGE_FONT)
        TextRect.center = ((self.WIN_WIDTH/2),(self.WIN_HEIGHT/2))
        self.win.blit(TextSurf, TextRect)

        while self.pause:
            self.check_events()

            self.button("Continue",150,450,200,50,(0, 100, 255), (0, 100, 200),self.unpause)
            self.button("Menu",150,500,200,50,(200, 200, 255), (100, 100, 150),self.intro)
            self.button("Quit", 150,550,100,50, (255, 0, 0), (200, 0, 0), self.end)

            pygame.display.update()
            self.clock.tick(15)

    def main(self, genome=None, config=None):
        """
        Main Loop
        """
        self.setup(genome)
        self.run_loop = True

        while self.run_loop:
            self.clock.tick(30)
            self.add_pipe = False
            self.removed = []

            self.check_events()

            self.handle_jumps()

            self.check_for_colisions()

            self.handle_pipe_moving()
            self.base.move(self.vel)
            self.speed_up()

            self.check_for_bird_death()
            if len(self.birds) == 0:
                self.run_loop = False


            self.draw_window()

        if self.player:
            self.game_over()
        else:
            if self.score > self.AI.best_score:
                self.AI.best_score = self.score
            self.AI.games += self.initial_population
            self.AI.save_data()



    def game_over(self):
        """
        Lost Game View
        """
        self.DIE.play()
        self.player.games += 1
        if self.score > self.player.best_score:
            self.player.best_score = self.score
        self.over = True
        self.run_loop = False

        TextSurf, TextRect = text_objects("GAME OVER", self.LARGE_FONT)
        TextRect.center = ((self.WIN_WIDTH/2),(self.WIN_HEIGHT/2))
        self.win.blit(TextSurf, TextRect)

        textSurf, textRect = text_objects(f"games played: {self.player.games}", self.STAT_FONT)
        textRect.center = ((self.WIN_WIDTH/2), (self.WIN_HEIGHT/2 - 50))
        self.win.blit(textSurf, textRect)

        textSurf, textRect = text_objects(f"score overall: {self.player.sum_score}", self.STAT_FONT)
        textRect.center = ((self.WIN_WIDTH/2), (self.WIN_HEIGHT/2 - 100))
        self.win.blit(textSurf, textRect)

        while self.over:
            self.check_events()

            self.button("Try Again",150,450,200,50,(0, 100, 255), (0, 100, 200),lambda: self.play(self.players.index(self.player)))
            self.button("Menu",150,500,200,50,(200, 200, 255), (100, 100, 150),self.intro)
            self.button("Quit", 150,550,100,50, (255, 0, 0), (200, 0, 0), self.end)

            pygame.display.update()
            self.clock.tick(15)

    def end(self):
        """
        ends program
        """
        pygame.quit()
        quit()

    def unpause(self):
        """
        pretty straight-forward don't you think?
        """
        self.pause = False

### RESTART ###
    def setup(self, genomes=None):
        """Restarts a game"""
        self.initial_population = 0
        self.nets =[]
        self.ge =[]
        self.birds = []
        self.menu = False
        self.over = False
        self.player_choosing = False
        self.board = False
        self.run_loop = False

        if self.player:
            self.generation += 1
            self.birds.append(Bird(230, 350))

        # gets neural network
        if genomes:
            self.generation += 1
            self.menu = False
            for _, g in genomes:
                net = neat.nn.FeedForwardNetwork.create(g, self.config)
                self.nets.append(net)
                self.birds.append(Bird(230, 350))
                g.fitness = 0
                self.ge.append(g)

        self.initial_population = len(self.birds)
        self.base = Base(730)
        self.pipes = [Pipe(600)]
        self.score = 0
        self.vel = 5
        self.win = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        gameIcon = pygame.image.load('imgs/bird1.png')
        pygame.display.set_icon(gameIcon)
        pygame.display.set_caption('Flappy Bird')
        self.clock = pygame.time.Clock()
        self.last = 0



### CHECKS ###

    def check_events(self):
        """
        Checks for key pressing and closing window events
        """
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.run_loop = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if not self.menu:
                    if event.key == pygame.K_ESCAPE:
                        if not self.pause:
                            self.pause = True
                            self.paused()
                        else:
                            self.pause = False
                            self.unpause()
                    if self.player and not (self.over or self.menu):
                        if event.key == pygame.K_SPACE:
                            self.birds[0].jump()
                            self.WING.play()

    def check_for_colisions(self):
        """
        Colisions with pipes
        """
        for pipe in self.pipes:
            for x, bird in enumerate(self.birds):
                if pipe.collide(bird):
                    self.birds.pop(x)
                    self.HIT.play()
                    if not self.player:
                        self.ge[x].fitness -= 1 # encourages birds not to hit the pipe
                        self.nets.pop(x)
                        self.ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    self.add_pipe = True

    def check_for_bird_death(self):
        """
        Checks if bird isnt to Low or to High like Ikar
        """
        for x, bird in enumerate(self.birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                self.birds.pop(x)
                if not self.player:
                    self.nets.pop(x)
                    self.ge.pop(x)


### HANDLERS ###

    def handle_pipe_moving(self):
        """
        Pipes move to the left
        """
        for pipe in self.pipes:
            pipe.move(self.vel)

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                self.removed.append(pipe)

        if self.add_pipe:
            self.score += 1
            if self.player:
                self.player.sum_score += 1
                self.POINT.play()
            else:
                self.AI.sum_score += len(self.birds)
                self.POINT.play()
            for g in self.ge:
                g.fitness += 5
            self.pipes.append(Pipe(600))

        for pipe in self.removed:
            self.pipes.remove(pipe)

    def speed_up(self):
        """
        Game gets faster every 5 points
        """
        if self.score == self.last + 5:
            self.vel += 1
            self.last = self.score

    def handle_jumps(self):
        """
        allows birds to jump
        """
        for x, bird in enumerate(self.birds):
            bird.move()
            if not self.player:
                self.ge[x].fitness += 0.1
                self.decide_for_jump(bird, x)

    def distinguish_pipes(self):
        """
        distinguishes closer pipe from further
        """
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
        """
        AI has to decide whether to jump or not
        """

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


### OTHERS ###

    def draw_window(self):
        """
        Here everything gets drawn
        """
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

    def button(self, msg, x, y, w, h, ic, ac, action=None):
        """
        helps to create buttons on the screen
        """
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


### PLAYERS ###

    def create_player(self):
        pass

    def sort_players(self):
        players_sorted = []
        scores = []
        for player in self.players:
            scores.append(player.sum_score)
        scores.sort()
        for score in scores:
            for player in self.players:
                if player.sum_score == score and player not in players_sorted:
                    players_sorted.append(player)
                    break
        return reversed(players_sorted)




    def get_players(self):

        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)
            with open("players/AI.score", "w") as file:
                file.write("0\n0\n0\n0\n")

        files = os.listdir("players/")
        for file in files:
            if file not in self.data_files:
                if file[-6:] == ".score":
                    self.data_files.append(file)
                    pl = Player()
                    pl.nick = file[:-6]
                    pl.filename = f"players/{file}"
                    pl.get_data()
                    self.players.append(pl)
