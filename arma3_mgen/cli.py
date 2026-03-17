"""CLI entry point for ARMA 3 Mission Generator."""

import sys
from pathlib import Path

import click

from .config_loader import load_config
from .generators.mission_folder import generate_mission


@click.group()
def cli():
    """IBC ARMA 3 Mission Generator"""
    pass


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Output directory (default: Documents/Arma 3/missions/)",
)
def generate(config_file: str, output: str | None):
    """Generate an ARMA 3 mission from a JSON config file."""
    if output is None:
        output = str(Path.home() / "Documents" / "Arma 3" / "missions")

    click.echo(f"Loading config: {config_file}")
    config = load_config(config_file)

    click.echo(f"Generating mission: {config.meta.mission_name}")
    click.echo(f"Map: {config.meta.map}")
    click.echo(f"Output: {output}")

    mission_path = generate_mission(config, output)

    click.echo(f"\nMission generated successfully!")
    click.echo(f"Folder: {mission_path}")
    click.echo(f"\nOpen Eden Editor in ARMA 3 to load this mission.")


@cli.command()
def list_maps():
    """List available maps and their classnames."""
    from .config_loader import MAPS_DB

    click.echo("Available maps:\n")
    for name, classname in sorted(MAPS_DB.items()):
        click.echo(f"  {name:<25} -> {classname}")
    click.echo(f"\nUse 'map_classname_override' in config for unlisted workshop maps.")


def main():
    cli()


if __name__ == "__main__":
    main()
