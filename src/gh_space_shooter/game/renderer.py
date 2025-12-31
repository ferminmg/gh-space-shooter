"""Renderer for drawing game frames using Pillow."""

from PIL import Image, ImageDraw

from .game_state import GameState
from ..constants import NUM_DAYS, NUM_WEEKS

class Renderer:
    """Renders game state as PIL Images."""

    # Cell size in pixels
    CELL_SIZE = 12
    CELL_SPACING = 2

    # Colors (RGB tuples)
    COLOR_BACKGROUND = (13, 17, 23)  # GitHub dark background
    COLOR_EMPTY = (22, 27, 34)  # Empty cell
    COLOR_SHIP = (88, 166, 255)  # Blue for ship
    COLOR_BULLET = (255, 223, 0)  # Yellow for bullets

    # Enemy colors based on health (GitHub green shades)
    COLOR_ENEMY = {
        1: (0, 109, 50),  # Level 1 - light green
        2: (38, 166, 65),  # Level 2 - medium green
        3: (57, 211, 83),  # Level 3 - bright green
        4: (87, 242, 135),  # Level 4 - very bright green
    }

    def __init__(self, game_state: GameState):
        """
        Initialize renderer.

        Args:
            game_state: The game state to render
        """
        self.game_state = game_state

        # Calculate image dimensions
        self.grid_width = NUM_WEEKS * (self.CELL_SIZE + self.CELL_SPACING)
        self.grid_height = NUM_DAYS * (self.CELL_SIZE + self.CELL_SPACING)

        # Add padding for ship movement
        self.padding = 40
        self.width = self.grid_width + 2 * self.padding
        self.height = self.grid_height + 2 * self.padding

    def render_frame(self) -> Image.Image:
        """
        Render the current game state as an image.

        Returns:
            PIL Image of the current frame
        """
        # Create image with background color
        img = Image.new("RGB", (self.width, self.height), self.COLOR_BACKGROUND)
        draw = ImageDraw.Draw(img)

        # Create rendering context
        context = self._create_context()

        # Draw all game objects (including grid) using their draw() methods
        self.game_state.draw(draw, context)

        return img

    def _create_context(self) -> dict:
        """Create rendering context for drawable objects."""
        return {
            "get_cell_position": self._get_cell_position,
            "cell_size": self.CELL_SIZE,
            "cell_spacing": self.CELL_SPACING,
            "padding": self.padding,
            "grid_color": self.COLOR_EMPTY,
            "enemy_colors": self.COLOR_ENEMY,
            "ship_color": self.COLOR_SHIP,
            "bullet_color": self.COLOR_BULLET,
        }

    def _get_cell_position(self, week: int, day: int) -> tuple[int, int]:
        """
        Get the pixel position (x, y) of a cell.

        Args:
            week: Week index
            day: Day index

        Returns:
            Tuple of (x, y) pixel coordinates
        """
        x = self.padding + week * (self.CELL_SIZE + self.CELL_SPACING)
        y = self.padding + day * (self.CELL_SIZE + self.CELL_SPACING)
        return (x, y)
