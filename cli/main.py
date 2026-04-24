"""Main CLI entry point."""
import asyncio
import sys
import click
from pathlib import Path
from core.logger import setup_logger, logger
from core.config import ConfigManager

# Import orchestrator components
from orchestrator import SiriBot


@click.group()
@click.version_option(version="1.0.0")
@click.option("--config", "-c", type=click.Path(), help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx, config, verbose):
    """SiriBot - Open-source AI assistant"""
    ctx.ensure_object(dict)
    
    log_level = "DEBUG" if verbose else "INFO"
    setup_logger(log_level)
    
    ctx.obj["config_path"] = config


@cli.command()
@click.option("--config", "-c", type=click.Path(), help="Config file path")
@click.pass_context
def init(ctx, config):
    """Initialize SiriBot configuration."""
    from core.config import Config
    
    config_path = config or "config/config.yaml"
    path = Path(config_path)
    
    if path.exists():
        click.confirm(f"{config_path} already exists. Overwrite?", abort=True)
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    default_config = Config()
    import yaml
    with open(path, "w") as f:
        yaml.dump(default_config.model_dump(), f, default_flow_style=False)
    
    click.echo(f"Created configuration at {config_path}")


@cli.command()
@click.option("--config", "-c", type=click.Path(), help="Config file path")
@click.pass_context
def chat(ctx, config):
    """Start interactive chat."""
    from cli.interface import SiriBotInterface
    
    config_path = config or ctx.obj.get("config_path")
    interface = SiriBotInterface(config_path)
    
    try:
        asyncio.run(interface.run())
    except KeyboardInterrupt:
        click.echo("\nGoodbye!")
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("command")
@click.option("--config", "-c", type=click.Path(), help="Config file path")
@click.pass_context
def run(ctx, command, config):
    """Execute a single command."""
    async def _run():
        bot = SiriBot(config or ctx.obj.get("config_path"))
        result = await bot.chat(command)
        click.echo(result)
    
    asyncio.run(_run())


@cli.command()
@click.option("--config", "-c", type=click.Path(), help="Config file path")
@click.pass_context
def voice(ctx, config):
    """Start voice mode."""
    from cli.interface import SiriBotInterface
    
    config_path = config or ctx.obj.get("config_path")
    interface = SiriBotInterface(config_path)
    interface.voice_mode = True
    
    try:
        asyncio.run(interface.run())
    except KeyboardInterrupt:
        click.echo("\nGoodbye!")
    except Exception as e:
        logger.error(f"Voice mode failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--config", "-c", type=click.Path(), help="Config file path")
@click.pass_context
def tools(ctx, config):
    """List available tools."""
    bot = SiriBot(config or ctx.obj.get("config_path"))
    
    tools_info = bot.get_available_tools()
    
    click.echo("Available tools:\n")
    for name, desc in tools_info.items():
        click.echo(f"  {click.style(name, fg='cyan')}: {desc}")


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
