"""Animator for generating GIF animations from game strategies."""

from io import BytesIO
from typing import Iterator

from PIL import Image

from ..github_client import ContributionData
from .game_state import GameState
from .renderer import Renderer
from .strategies.base_strategy import BaseStrategy
from .render_context import RenderContext


class Animator:
    """Generates animated GIFs from game strategies."""

    def __init__(
        self,
        contribution_data: ContributionData,
        strategy: BaseStrategy,
        fps: int,
        watermark: bool = False,
    ):
        """
        Initialize animator.

        Args:
            contribution_data: The GitHub contribution data
            strategy: The strategy to use for clearing enemies
            fps: Frames per second for the animation
            watermark: Whether to add watermark to the GIF
        """
        self.contribution_data = contribution_data
        self.strategy = strategy
        self.fps = fps
        self.watermark = watermark
        self.frame_duration = 1000 // fps
        # Delta time in seconds per frame
        # Used to scale all speeds (cells/second) to per-frame movement
        self.delta_time = 1.0 / fps

    def generate_frames(self, max_frames: int | None = None) -> Iterator[Image.Image]:
        """
        Generate all animation frames.

        Returns:
            Iterator of PIL Images representing animation frames
        """
        game_state = GameState(self.contribution_data)
        renderer = Renderer(game_state, RenderContext.darkmode(), watermark=self.watermark)
        
        if max_frames is not None:
            gen = self._generate_frames(game_state, renderer)
            while max_frames > 0:
                max_frames -= 1
                yield next(gen)
        else:
            yield from self._generate_frames(game_state, renderer)
        

    def _generate_frames(
        self, game_state: GameState, renderer: Renderer
    ) -> Iterator[Image.Image]:
        """
        Generate all animation frames.

        Args:
            game_state: The game state
            renderer: The renderer

        Returns:
            List of PIL Images representing animation frames
        """

        # Add initial frame showing starting state
        yield renderer.render_frame()

        # Process each action from the strategy
        for action in self.strategy.generate_actions(game_state):
            game_state.ship.move_to(action.x)
            while game_state.can_take_action() is False:
                game_state.animate(self.delta_time)
                yield renderer.render_frame()

            if action.shoot:
                game_state.shoot()
                game_state.animate(self.delta_time)
                yield renderer.render_frame()

        force_kill_countdown = 100
        # Add final frames showing completion
        while not game_state.is_complete():
            game_state.animate(self.delta_time)
            yield renderer.render_frame()
            
            force_kill_countdown -= 1
            if force_kill_countdown <= 0:
                break
            
        for _ in range(5):
            yield renderer.render_frame()
