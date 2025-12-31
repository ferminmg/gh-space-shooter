"""Animator for generating GIF animations from game strategies."""

from typing import List

from PIL import Image

from ..github_client import ContributionData
from .game_state import GameState
from .renderer import Renderer
from .strategies.base_strategy import BaseStrategy


class Animator:
    """Generates animated GIFs from game strategies."""

    def __init__(
        self,
        contribution_data: ContributionData,
        strategy: BaseStrategy,
        frame_duration: int = 100,
    ):
        """
        Initialize animator.

        Args:
            contribution_data: The GitHub contribution data
            strategy: The strategy to use for clearing enemies
            frame_duration: Duration of each frame in milliseconds
        """
        self.contribution_data = contribution_data
        self.strategy = strategy
        self.frame_duration = frame_duration

    def generate_gif(self, output_path: str) -> None:
        """
        Generate animated GIF and save to file.

        Args:
            output_path: Path where GIF should be saved
        """
        # Initialize game state
        game_state = GameState(self.contribution_data)
        renderer = Renderer(game_state)

        frames = self._generate_frames(game_state, renderer)

        # Save as GIF
        if frames:
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=self.frame_duration,
                loop=0,  # Loop forever
                optimize=False,
            )

    def _generate_frames(
        self, game_state: GameState, renderer: Renderer
    ) -> List[Image.Image]:
        """
        Generate all animation frames.

        Args:
            game_state: The game state
            renderer: The renderer

        Returns:
            List of PIL Images representing animation frames
        """
        frames = []
        bullet_flight_steps = 5  # Number of frames for bullet to travel

        # Add initial frame (ship off-screen)
        frames.append(renderer.render_frame())

        # Process each action from the strategy
        for action in self.strategy.generate_actions(self.contribution_data):
            # Move ship to action position (only horizontal movement)
            game_state.ship.move_to(action.week)

            # If action is to shoot, fire bullet and animate it
            if action.shoot:
                bullet = game_state.shoot(action.week, action.day)

                # Animate bullet flying from ship to target
                for step in range(bullet_flight_steps):
                    bullet.progress = (step + 1) / bullet_flight_steps
                    frames.append(renderer.render_frame())

                # Hit the enemy when bullet reaches target
                game_state.hit_target(action.week, action.day)

                # Clear bullets for next action
                game_state.clear_bullets()
            else:
                # Just render ship movement (no shooting)
                frames.append(renderer.render_frame())

        # Add final frames showing completion
        frames.append(renderer.render_frame())
        frames.append(renderer.render_frame())  # Hold final frame longer

        return frames
