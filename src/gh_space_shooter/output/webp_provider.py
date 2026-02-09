"""WebP output provider."""

from io import BytesIO
from typing import Iterator
from PIL import Image
from .base import OutputProvider


class WebPOutputProvider(OutputProvider):
    """Output provider for WebP format."""

    def encode(self, frames: Iterator[Image.Image], frame_duration: int) -> bytes:
        """
        Encode frames as animated WebP.

        Args:
            frames: Iterator of PIL Images

        Returns:
            WebP-encoded bytes
        """
        frame_list = list(frames)
        buffer = BytesIO()

        if frame_list:
            frame_list[0].save(
                buffer,
                format="webp",
                save_all=True,
                append_images=frame_list[1:],
                duration=frame_duration,
                loop=0,
            )

        return buffer.getvalue()
