import pygame, random

# Pre-settings
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 810
screen_height = 780

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Font
score_font = pygame.font.SysFont('Bauhaus 93', 60)

# Color
text_color = (255, 255, 255)

# Define game variables
ground_scroll = 0
scroll_speed = 4
start_the_game = False
game_over = False
pipe_gap = 150
pipe_frequency = 1200 # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
pass_left = False
score = 0

# Load images
background = pygame.image.load('img/bg.png')
ground = pygame.image.load('img/ground.png')
button = pygame.image.load('img/restart.png')

# Show the score
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Class for creating and animating the bird
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.count = 0
        for i in range(1, 4):
            self.images.append(pygame.image.load(f'img/bird{i}.png'))
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.trigger = False

    def update(self):
        global game_over

        # Check if the bird touched the ground
        if self.rect.bottom >= 640:
            game_over = True

        # The bird animation
        if self.count > 7:
            self.count = 0
            self.index += 1
            if self.index >= 3:
                self.index = 0
        self.image = self.images[self.index]

        # Gravity
        if start_the_game:
            self.count += 1
            self.vel += 0.5
            if self.vel > 10:
                self.vel = 10
            if self.rect.bottom < 640:
                self.rect.bottom += int(self.vel)

        # Jumping
        if not game_over:
                if pygame.mouse.get_pressed()[0] and not self.trigger:
                    self.trigger = True
                    self.vel = -10
                if not pygame.mouse.get_pressed()[0]:
                    self.trigger = False
                if self.rect.top < 0:
                    game_over = True

                # Rotate the bird
                self.image = pygame.transform.rotate(self.images[self.index], -2.5 * self.vel)

        else:
            # Rotate the bird all the way down if it's game over
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipes(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()

        # Position 1 for the top pipe, position 0 for the bottom pipe
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap//2]
        else:
            self.rect.topleft = [x, y + pipe_gap//2]

    def update(self):
        global game_over

        if not game_over:
            self.rect.left -= scroll_speed
            # If the pipe got out of the screen, delete it.
            if self.rect.right < 0:
                self.kill()


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        # Check if the restart button is clicked
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

# Set the bird and pipes
bird_group = pygame.sprite.Group()
pipes_group = pygame.sprite.Group()
flappy = Bird(100, screen_height//2)
bird_group.add(flappy)

# Create button instance
button = Button(screen_width//2 - 50, screen_height//2 - 50, button)

run = True
while run:

    # Draw the background
    screen.blit(background, (0, 0))

    # Draw the pipes
    pipes_group.draw(screen)
    pipes_group.update()

    # Collisions
    if pygame.sprite.groupcollide(bird_group, pipes_group, False, False):
        game_over = True

    if not game_over and start_the_game:
        # Creating the pipes
        random_height_parameter = random.randint(-100, 100)
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            btm_pipe = Pipes(screen_width, screen_height // 2 + random_height_parameter, -1)
            top_pipe = Pipes(screen_width, screen_height // 2 + random_height_parameter, 1)
            pipes_group.add(btm_pipe)
            pipes_group.add(top_pipe)
            last_pipe = time_now

        # Scroll the ground
        ground_scroll -= scroll_speed
        if ground_scroll < -35:
            ground_scroll = 0

    # Draw the bird
    bird_group.draw(screen)
    bird_group.update()

    # Draw the ground
    screen.blit(ground, (ground_scroll, 640))

    # Check and display the score
    if pipes_group.sprites() and bird_group.sprites()[0].rect.left > pipes_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipes_group.sprites()[0].rect.right and not pass_left:
        pass_left = True

    if pipes_group.sprites() and pass_left and bird_group.sprites()[0].rect.left > pipes_group.sprites()\
            [0].rect.right:
        score += 1
        pass_left = False

    draw_text(str(score), score_font, text_color, screen_width//2, 100)

    # check if the game is over and reset
    if game_over:
        if button.draw():
            game_over = False
            pipes_group.empty()
            flappy.rect.x = 100
            flappy.rect.y = screen_height//2
            score = 0

    # Setting the fps
    clock.tick(fps)

    # General settings
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            start_the_game = True

    # Updating the display
    pygame.display.update()

pygame.quit()