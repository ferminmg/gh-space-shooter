"""Game state management for tracking enemies, ship, and bullets."""

from abc import ABC, abstractmethod
from typing import List, Tuple

from PIL import ImageDraw

from ..constants import NUM_DAYS, NUM_WEEKS
from ..github_client import ContributionData

class Drawable(ABC):
    """Interface for objects that can be animated and drawn."""

    @abstractmethod
    def animate(self) -> None:
        """Update the object's state for the next animation frame."""
        pass

    @abstractmethod
    def draw(self, draw: ImageDraw.ImageDraw, context: dict) -> None:
        """
        Draw the object on the image.

        Args:
            draw: PIL ImageDraw object
            context: Rendering context with helper functions and constants
        """
        pass


class Enemy(Drawable):
    """Represents an enemy at a specific position."""

    def __init__(self, week: int, day: int, health: int):
        """
        Initialize an enemy.

        Args:
            week: Week position (0-51)
            day: Day position (0-6)
            health: Initial health/lives (1-4)
        """
        self.week = week
        self.day = day
        self.health = health
        self.max_health = health

    def take_damage(self) -> bool:
        """
        Enemy takes 1 damage.

        Returns:
            True if enemy is destroyed (health <= 0), False otherwise
        """
        self.health -= 1
        return self.health <= 0

    def is_alive(self) -> bool:
        """Check if enemy is still alive."""
        return self.health > 0

    def animate(self) -> None:
        """Update enemy state for next frame (enemies don't animate currently)."""
        pass

    def draw(self, draw: ImageDraw.ImageDraw, context: dict) -> None:
        """Draw the enemy at its position."""
        if not self.is_alive():
            return

        # Get position from context helper
        get_cell_position = context["get_cell_position"]
        x, y = get_cell_position(self.week, self.day)

        # Get color based on current health
        color_map = context["enemy_colors"]
        cell_size = context["cell_size"]
        color = color_map.get(self.health, color_map[1])

        draw.rectangle(
            [x, y, x + cell_size, y + cell_size],
            fill=color,
        )


class Bullet(Drawable):
    """Represents a bullet fired by the ship."""

    def __init__(self, week: int, target_day: int, progress: float = 0.0):
        """
        Initialize a bullet.

        Args:
            week: Current week position
            target_day: Target day position (enemy position)
            progress: Animation progress from ship to target (0.0 to 1.0)
        """
        self.week = week
        self.target_day = target_day
        self.progress = progress  # 0.0 = at ship, 1.0 = at target

    def animate(self) -> None:
        """Update bullet position for next frame (controlled externally)."""
        pass

    def draw(self, draw: ImageDraw.ImageDraw, context: dict) -> None:
        """Draw the bullet at its animated position."""
        get_cell_position = context["get_cell_position"]
        cell_size = context["cell_size"]
        cell_spacing = context["cell_spacing"]
        padding = context["padding"]
        bullet_color = context["bullet_color"]

        # Get horizontal position (week)
        x, _ = get_cell_position(self.week, 0)
        x += cell_size // 2  # Center of cell

        # Calculate vertical position based on progress
        # Start from ship position (below grid)
        ship_y = padding + NUM_DAYS * (cell_size + cell_spacing) + 10

        # End at target enemy position
        _, target_y = get_cell_position(self.week, self.target_day)
        target_y += cell_size // 2  # Center of cell

        # Interpolate based on progress
        y = ship_y + (target_y - ship_y) * self.progress

        # Draw bullet as small circle
        radius = 3
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            fill=bullet_color,
        )


class Ship(Drawable):
    """Represents the player's ship."""

    def __init__(self):
        """Initialize the ship at starting position."""
        self.week = -1  # Start off-screen to the left
        # Ship stays below the grid

    def move_to(self, week: int):
        """
        Move ship to a new week position.

        Args:
            week: Target week
        """
        self.week = week

    def animate(self) -> None:
        """Update ship state for next frame (controlled externally)."""
        pass

    def draw(self, draw: ImageDraw.ImageDraw, context: dict) -> None:
        """Draw the ship below the grid."""
        get_cell_position = context["get_cell_position"]
        cell_size = context["cell_size"]
        cell_spacing = context["cell_spacing"]
        padding = context["padding"]
        ship_color = context["ship_color"]

        # Ship stays below the grid at a fixed vertical position
        if self.week >= 0:
            x, _ = get_cell_position(self.week, 0)
        else:
            # Ship off-screen to the left
            x = padding - 20

        # Position ship below the grid
        ship_y = padding + NUM_DAYS * (cell_size + cell_spacing) + 10

        # Draw simple ship shape (triangle pointing up)
        draw.polygon(
            [
                (x + cell_size // 2, ship_y),  # Top point (front)
                (x, ship_y + cell_size),  # Bottom left
                (x + cell_size, ship_y + cell_size),  # Bottom right
            ],
            fill=ship_color,
        )


class GameState(Drawable):
    """Manages the current state of the game."""

    def __init__(self, contribution_data: ContributionData):
        """
        Initialize game state from contribution data.

        Args:
            contribution_data: The GitHub contribution data
        """
        self.contribution_data = contribution_data
        self.ship = Ship()
        self.enemies: List[Enemy] = []
        self.bullets: List[Bullet] = []

        # Initialize enemies from contribution data
        self._initialize_enemies()

    def _initialize_enemies(self):
        """Create enemies based on contribution levels."""
        weeks = self.contribution_data["weeks"]
        for week_idx, week in enumerate(weeks):
            for day_idx, day in enumerate(week["days"]):
                level = day["level"]
                if level > 0:  # Only create enemy if there are contributions
                    enemy = Enemy(week=week_idx, day=day_idx, health=level)
                    self.enemies.append(enemy)

    def get_enemy_at(self, week: int, day: int) -> Enemy | None:
        """
        Get enemy at a specific position.

        Args:
            week: Week position
            day: Day position

        Returns:
            Enemy if one exists at that position, None otherwise
        """
        for enemy in self.enemies:
            if enemy.week == week and enemy.day == day and enemy.is_alive():
                return enemy
        return None

    def shoot(self, week: int, day: int) -> Bullet:
        """
        Ship shoots a bullet at target position.

        Args:
            week: Target week
            day: Target day

        Returns:
            The created bullet
        """
        # Create bullet starting at ship position (progress = 0.0)
        bullet = Bullet(week=week, target_day=day, progress=0.0)
        self.bullets.append(bullet)
        return bullet

    def hit_target(self, week: int, day: int):
        """
        Hit enemy at target position (when bullet reaches it).

        Args:
            week: Target week
            day: Target day
        """
        enemy = self.get_enemy_at(week, day)
        if enemy:
            enemy.take_damage()

    def clear_bullets(self):
        """Clear all bullets from the screen."""
        self.bullets.clear()

    def get_alive_enemies(self) -> List[Enemy]:
        """Get list of all alive enemies."""
        return [enemy for enemy in self.enemies if enemy.is_alive()]

    def is_complete(self) -> bool:
        """Check if game is complete (all enemies destroyed)."""
        return len(self.get_alive_enemies()) == 0

    def animate(self) -> None:
        """Update all game objects for next frame."""
        self.ship.animate()
        for enemy in self.get_alive_enemies():
            enemy.animate()
        for bullet in self.bullets:
            bullet.animate()

    def draw(self, draw: ImageDraw.ImageDraw, context: dict) -> None:
        """Draw all game objects including the grid."""
        # Draw grid background first
        self._draw_grid(draw, context)

        # Draw enemies
        for enemy in self.get_alive_enemies():
            enemy.draw(draw, context)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(draw, context)

        # Draw ship (on top)
        self.ship.draw(draw, context)

    def _draw_grid(self, draw: ImageDraw.ImageDraw, context: dict) -> None:
        """Draw the empty grid cells."""
        get_cell_position = context["get_cell_position"]
        cell_size = context["cell_size"]
        grid_color = context["grid_color"]

        for week in range(NUM_WEEKS):
            for day in range(NUM_DAYS):
                x, y = get_cell_position(week, day)
                draw.rectangle(
                    [x, y, x + cell_size, y + cell_size],
                    fill=grid_color,
                )
