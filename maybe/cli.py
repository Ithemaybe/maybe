import click
from maybe.commands.serve import serve


@click.group()
@click.version_option(package_name="maybe")
def main():
    """maybe — personal CLI toolkit."""
    pass


main.add_command(serve)
