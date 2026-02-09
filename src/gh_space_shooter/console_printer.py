"""Console output formatting and display functions."""

from rich.console import Console
from rich.text import Text

from .github_client import ContributionData

console = Console()


class ContributionConsolePrinter:
    """Prints GitHub contribution data to the console with formatting.

    Displays contribution statistics and renders a GitHub-style contribution
    graph using colored blocks via the Rich library.
    """

    def display_stats(self, data: ContributionData) -> None:
    def display_stats(self, data: ContributionData) -> None:
        """Display contribution statistics in a one-liner."""
        # Get date range
        all_days = [day for week in data["weeks"] for day in week["days"]]
        if all_days:
            start_date = all_days[0]["date"]
            end_date = all_days[-1]["date"]

            console.print(
                f"\n[bold green]✓[/bold green] @{data['username']}: "
                f"{data['total_contributions']} contributions from {start_date} to {end_date}, "
                f"{len(data['weeks'])} weeks in total.\n"
            )

    def display_contribution_graph(self, data: ContributionData) -> None:
        """Display a GitHub-style contribution graph."""
        weeks = data["weeks"]
        day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        console.print("[bold]Contribution Graph:[/bold]\n")

        for day_idx in range(7):  # 0=Sunday, 6=Saturday
            console.print(f"  {day_labels[day_idx]} ", end="")

            # Print colored blocks for this day across all weeks
            for week in weeks:
                
                if day_idx < len(week["days"]):
                    day = week["days"][day_idx]
                    level = day["level"]
                else:
                    level = 0
                self._print_block(level)

            console.print()  # New line after each day row

        # Print legend
        console.print("\n  Less ", end="")
        for level in range(5):
            self._print_block(level)
            console.print("  ", end="")
        console.print("More")

    COLOR_MAP = {
        0: "",        # Transparent
        1: "on rgb(0,109,50)",           # Light green
        2: "on rgb(38,166,65)",          # Medium green
        3: "on rgb(57,211,83)",          # Bright green
        4: "on rgb(87,242,135)",         # Very bright green
    }

    def _print_block(self, level: int) -> None:
        """Print a colored block based on contribution level."""
        text = Text("  ", style=self.COLOR_MAP.get(level, ""))
        console.print(text, end="")
