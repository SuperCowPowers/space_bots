"""GameEngineAdapter: Class that handles display and sound stuff"""

# Note: This class should be refactored to handle additional backends at some point
#       Right now it's pygame specific, but later we'll have more options

import pygame

# Local imports
from space_bots.sound_player import SoundPlayer


class GameEngineAdapter:
    """GameEngineAdapter: Class that handles display and sound stuff"""

    def __init__(self, universe, width=1600, height=1000):
        """Initialize the GameEngineAdapter class"""
        pygame.init()
        screen = pygame.display.set_mode([width, height])
        pygame.display.set_caption('Space Bots')
        self.screen = screen
        self.width = width
        self.height = height
        self.running = True
        self.actors = []
        self.event_subscribers = []
        self.background_color = (20, 20, 30)
        self.collision_detection = None

        # Get a random font
        self.font = pygame.font.SysFont('calibri', 36, italic=True)

        # Sound Classes
        self.sound_player = SoundPlayer()

        # Clock
        self.clock = pygame.time.Clock()

        # Universe has 3 callbacks (communicate(), update() and draw()
        self.universe = universe

    def get_surface(self):
        """Return the drawable surface (display screen)"""
        return self.screen

    def play_background_music(self):
        """Play the background music mix"""
        self.sound_player.play_background_music()

    def play_sound_queue(self):
        """Play the sound with the given sound name"""
        self.sound_player.play_queue()

    def restricted_play_sound(self, sound_name):
        """This adds the sound to the current play queue"""
        self.sound_player.add_sound_to_queue(sound_name)

    def restricted_announce(self, sound_name, voice='random'):
        """Play the sound with the given sound name"""
        return self.sound_player.announce(sound_name, voice)

    def set_background_color(self, color):
        self.background_color = color

    def event_loop(self):
        """Main Event Loop for the Display"""
        while self.running:

            # 120 Frames/second
            self.clock.tick(120)

            # Check for application quit
            if self.check_for_quit():
                self.quit()

            # Draw the background
            self.draw_background()

            # Call the three callbacks
            self.universe.communicate()
            self.universe.update()
            self.universe.draw()

            # Flip the display
            pygame.display.flip()

    def draw_circle(self, color, center, radius, width=3):
        """Draw a Circle with the given parameters"""
        pygame.draw.circle(self.screen, color, center, radius, width)

    def draw_line(self, color, start, end, width=2):
        """Draw a Lince with the given parameters"""
        pygame.draw.line(self.screen, color, start, end, width)

    def draw_polygon(self, color, points, width=3):
        pygame.draw.polygon(self.screen, color, points, width)

    def draw_text(self, text, color=(140, 200, 140)):
        img = self.font.render(text, True, color)
        self.screen.blit(img, (450, self.height-80))

    @staticmethod
    def image_load(image_file, x_size=0, y_size=0):
        _image = pygame.image.load(image_file)
        if x_size:
            _image = pygame.transform.scale(_image, (x_size, y_size))
        return _image

    def draw_image(self, image, x, y, rotation=0):
        if rotation != 0:
            self.image_rotate_blit(image, x, y, rotation)
        else:
            self.screen.blit(image, (x, y))

    def draw_background(self):
        self.screen.fill(self.background_color)

    def check_for_quit(self):
        """Check if the user/application wants to quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def image_rotate_blit(self, image, x, y, angle):

        # FIXME: Optimize this
        # Get the image midpoint
        width, height = image.get_size()
        mid_x = width/2
        mid_y = height/2
        x += mid_x
        y += mid_y

        # offset from pivot to center
        image_rect = image.get_rect(topleft=(x - mid_x, y - mid_y))
        offset_center_to_pivot = pygame.math.Vector2((x, y)) - image_rect.center

        # rotated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-angle)

        # rotated image center
        rotated_image_center = (x - rotated_offset.x, y - rotated_offset.y)

        # get a rotated image and return it
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

        # rotate and blit the image
        self.screen.blit(rotated_image, rotated_image_rect)

    @staticmethod
    def quit():
        """Quit the main event loop/display"""
        pygame.quit()


# Simple test of the GameEngineAdapter functionality
def test():
    """Test for GameEngineAdapter Class"""
    from space_bots.universe import Universe

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Call the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
