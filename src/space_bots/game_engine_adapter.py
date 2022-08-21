"""GameEngineAdapter: Class that handles display stuff"""

# Note: This class should be refactored to handle additional backends at some point
#       Right now it's pygame specific, but later we'll have more options

import pygame


class GameEngineAdapter():
    """GameEngineAdapter: Class that contains all the stuff"""

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

        # Universe has 3 callbacks (communicate(), update() and draw()
        self.universe = universe

    def get_surface(self):
        """Return the drawable surface (display screen)"""
        return self.screen

    def set_background_color(self, color):
        self.background_color = color

    def event_loop(self):
        """Main Event Loop for the Display"""
        while self.running:

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

    @staticmethod
    def image_load(image_file, x_size=0, y_size=0):
        _image = pygame.image.load(image_file)
        if x_size:
            _image = pygame.transform.scale(_image, (x_size, y_size))
        return _image

    def draw_image(self, image, x, y):
        self.screen.blit(image, (x, y))

    def draw_background(self):
        self.screen.fill(self.background_color)

    def check_for_quit(self):
        """Check if the user/application wants to quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

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
