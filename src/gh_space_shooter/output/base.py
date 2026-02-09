"""Base class for output format providers."""

from abc import ABC, abstractmethod
from typing import Iterator
from PIL import Image


class OutputProvider(ABC):
    """Abstract base class for output format providers."""

    @abstractmethod
    def encode(self, frames: Iterator[Image.Image], frame_duration: int) -> bytes:
        """
        Encode frames into the output format.

        Args:
            frames: Iterator of PIL Images

        Returns:
            Encoded output as bytes
        """
        pass
