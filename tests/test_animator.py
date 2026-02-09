"""Tests for Animator."""

from gh_space_shooter.game import Animator, ColumnStrategy
from gh_space_shooter.github_client import ContributionData


# Sample contribution data for testing
SAMPLE_DATA: ContributionData = {
    "username": "testuser",
    "total_contributions": 9,
    "weeks": [
        {
            "days": [
                {"level": 1, "date": "2024-01-01", "count": 1},
                {"level": 0, "date": "2024-01-02", "count": 0},
                {"level": 2, "date": "2024-01-03", "count": 3},
                {"level": 0, "date": "2024-01-04", "count": 0},
                {"level": 0, "date": "2024-01-05", "count": 0},
                {"level": 3, "date": "2024-01-06", "count": 5},
                {"level": 0, "date": "2024-01-07", "count": 0},
            ]
        }
    ],
}


def test_generate_frames_returns_iterator():
    """generate_frames should return an iterator of PIL Images."""
    strategy = ColumnStrategy()
    animator = Animator(SAMPLE_DATA, strategy, fps=30)

    frames = list(animator.generate_frames())

    assert len(frames) > 0
    assert all(hasattr(f, "save") for f in frames)  # PIL Images have save method
