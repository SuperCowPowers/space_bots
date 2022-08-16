"""DisplayAdapter: Class that handles display stuff"""

# Note: This class should be refactored to handle additional backends at some point
#       Right now it's pygame specific, but later we'll have more options

import pygame


class DisplayAdapter():
    """DisplayAdapter: Class that contains all the stuff"""

    def __init__(self, width=1600, height=1000):
        """Initialize the DisplayAdapter class"""
        pygame.init()
        screen = pygame.display.set_mode([width, height])
        pygame.display.set_caption('Space Bots')
        self.screen = screen
        self.width = width
        self.height = height
        self.running = True
        self.actors = []
        self.background_color = (20, 20, 30)

    def register_actor(self, actor):
        """Register a new Actor"""
        self.actors.append(actor)

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

            # Update the Registered Actors (in order)
            for actor in self.actors:
                actor.update()

            # Draw the Registered Actors (in order)
            for actor in self.actors:
                actor.draw()

            # Flip the display
            pygame.display.flip()

    def draw_circle(self, color, center, radius, width=3):
        """Draw a Circle with the given parameters"""
        pygame.draw.circle(self.screen, color, center, radius, width)

    def draw_polygon(self, color, points, width=3):
        pygame.draw.polygon(self.screen, color, points, width)

    def draw_background(self):
        self.screen.fill(self.background_color)

    def check_for_quit(self):
        """Check if the user/application wants to quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def quit(self):
        """Quit the main event loop/display"""
        pygame.quit()


# Simple test of the DisplayAdapter functionality
def test():
    """Test for DisplayAdapter Class"""
    from space_bots import actor

    # Create the DisplayAdapter
    my_display_adapter = DisplayAdapter()

    # Create an example Actor Class (needs update() and draw() methods)
    class SimpleActor(actor.Actor):
        def update(self):
            pass

        def draw(self):
            self.display.draw_circle((255, 255, 255), (250, 250), 25)
    simple_actor = SimpleActor(my_display_adapter)

    # Register the Actor with the Display Adapter
    my_display_adapter.register_actor(simple_actor)
    my_display_adapter.event_loop()


if __name__ == "__main__":
    test()
