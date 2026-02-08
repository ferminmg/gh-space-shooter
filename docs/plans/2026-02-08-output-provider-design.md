# Output Provider Design

## Overview

Refactor the output layer to support multiple formats (GIF, WebP, future formats) using an extensible provider pattern. The format is inferred from the output file extension.

## Architecture

```
src/gh_space_shooter/
├── output/
│   ├── __init__.py          # exports resolve_output_provider
│   ├── base.py              # OutputProvider ABC
│   ├── gif_provider.py      # GifOutputProvider
│   └── webp_provider.py     # WebPOutputProvider
└── game/
    └── animator.py          # Refactored with generate_frames()
```

## Components

### OutputProvider Base Class

Abstract base defining the contract for all output formats:

```python
class OutputProvider(ABC):
    def __init__(self, fps: int, watermark: bool = False):
        self.fps = fps
        self.watermark = watermark
        self.frame_duration = 1000 // fps

    @abstractmethod
    def encode(self, frames: Iterator[Image.Image]) -> bytes:
        """Encode frames into the output format."""
        pass
```

### GifOutputProvider

Moves existing GIF encoding logic from Animator.

### WebPOutputProvider

New provider for WebP format.

## Resolution Logic

```python
def resolve_output_provider(
    file_path: str,
    fps: int,
    watermark: bool = False,
) -> OutputProvider:
    """Resolve provider based on file extension."""
    ext = Path(file_path).suffix.lower()
    if ext not in _PROVIDER_MAP:
        raise ValueError(f"Unsupported format: {ext}")
    return _PROVIDER_MAP[ext](fps=fps, watermark=watermark)
```

## Data Flow

1. CLI calls `resolve_output_provider(out, fps, watermark)`
2. CLI creates `Animator(data, strategy, fps, watermark)`
3. CLI calls `provider.encode(animator.generate_frames())`
4. CLI writes bytes to file

## Animator Changes

- Make `generate_frames()` public (currently private `_generate_frames()`)
- `generate_gif()` becomes legacy/wraps new pattern

## Web App Changes

- Add optional `format` query parameter to `/api/generate`
- Return appropriate `media_type` based on format

## Error Handling

| Error | Handling |
|-------|----------|
| Unsupported extension | ValueError with supported formats list |
| Invalid frames | Provider-specific, caught by CLI |
| Missing dependencies | Clear error at import time |

## Testing

- Unit tests for each provider's `encode()` method
- Test `resolve_output_provider()` with valid/invalid extensions
- Integration test for full flow with different formats
