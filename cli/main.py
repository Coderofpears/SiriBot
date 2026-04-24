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


@cli.group()
def workflow():
    """Workflow management commands."""
    pass


@workflow.command("list")
@click.pass_context
def workflow_list(ctx):
    """List all workflows."""
    from orchestrator import SiriBot

    bot = SiriBot(ctx.obj.get("config_path"))
    workflows = bot.list_workflows()

    if not workflows:
        click.echo("No workflows registered")
        return

    for w in workflows:
        click.echo(f"  {click.style(w['name'], fg='cyan')}: {w['state']}")


@workflow.command("run")
@click.argument("workflow_id")
@click.pass_context
def workflow_run(ctx, workflow_id):
    """Execute a workflow."""

    async def _run():
        from orchestrator import SiriBot

        bot = SiriBot(ctx.obj.get("config_path"))
        result = await bot.execute_workflow(workflow_id)
        click.echo(f"Workflow result: {result}")

    asyncio.run(_run())


@cli.group()
def plugins():
    """Plugin marketplace commands."""
    pass


@plugins.command("list")
@click.pass_context
def plugins_list(ctx):
    """List installed plugins."""
    from orchestrator import SiriBot

    bot = SiriBot(ctx.obj.get("config_path"))
    plugins = bot.list_plugins()

    if not plugins:
        click.echo("No plugins installed")
        return

    for p in plugins:
        status = "[green]enabled[/green]" if p["enabled"] else "[red]disabled[/red]"
        click.echo(f"  {click.style(p['name'], fg='cyan')} ({p['version']}) - {status}")


@cli.group()
def models():
    """Personal model commands."""
    pass


@models.command("list")
@click.pass_context
def models_list(ctx):
    """List personal models."""
    from orchestrator import SiriBot

    bot = SiriBot(ctx.obj.get("config_path"))
    models = bot.list_models()

    if not models:
        click.echo("No personal models")
        return

    for m in models:
        click.echo(
            f"  {click.style(m['name'], fg='cyan')} - {m['type']} ({m['status']})"
        )


@cli.command()
@click.pass_context
def sync(ctx):
    """Show sync status."""
    from orchestrator import SiriBot

    bot = SiriBot(ctx.obj.get("config_path"))
    status = bot.get_sync_status()

    click.echo(f"Sync Status:")
    click.echo(f"  Enabled: {status.get('enabled', False)}")
    click.echo(f"  Pending changes: {status.get('pending_changes', 0)}")
    if status.get("device_id"):
        click.echo(f"  Device ID: {status.get('device_id')}")


@cli.command()
@click.pass_context
def health(ctx):
    """Check SiriBot health status."""
    from orchestrator import SiriBot

    bot = SiriBot(ctx.obj.get("config_path"))
    health = bot.health_check()

    status_color = "green" if health["status"] == "healthy" else "yellow"
    click.echo(f"Status: {click.style(health['status'].upper(), fg=status_color)}")
    click.echo(f"Version: {health['version']}")
    click.echo("\nServices:")

    for service, available in health["services"].items():
        icon = click.style("✓", fg="green") if available else click.style("✗", fg="red")
        click.echo(f"  {icon} {service}")


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
