from __future__ import annotations

import asyncio
import sys
import typer
from mcp.client.stdio import StdioServerParameters
from mirascope.mcp import sse_client, stdio_client
from pathlib import Path
from rich.console import Console
from sygaldry_cli.config_manager import ConfigManager, SygaldryConfig
from sygaldry_cli.core.utils import get_sygaldry_config

app = typer.Typer(help="Run a sygaldry agent as an MCP server.")
console = Console()


@app.command(name="mcp", help="Run a specified agent using MCP.")
def run_mcp_agent(
    agent_name: str = typer.Argument(..., help="The name of the agent to run."),
    mode: str = typer.Option(
        "stdio",
        "--mode",
        "-m",
        help="Server mode ('stdio' or 'http'). Currently only 'stdio' is actively supported by this command.",
        case_sensitive=False,
    ),
    host: str = typer.Option(None, "--host", help="Host for HTTP server."),
    port: int = typer.Option(None, "--port", help="Port for HTTP server."),
) -> None:
    """
    Runs a specified sygaldry agent as a Model Context Protocol (MCP) server.

    This command locates the agent within your project (based on sygaldry.json
    configuration), finds its MCP entrypoint (typically `mcp_server.py`),
    and launches it.

    It primarily uses `stdio` for communication, as per Mirascope's MCP client examples.
    """
    config_manager = ConfigManager()
    sygaldry_config = get_sygaldry_config(config_manager.project_root)

    if not sygaldry_config:
        console.print(
            f"[bold red]Error: sygaldry.json not found in project root ({config_manager.project_root}). "
            f"Please run `sygaldry init` first.[/bold red]"
        )
        raise typer.Exit(code=1)

    # Determine host and port
    final_host = host or sygaldry_config.get("default_mcp_host", "0.0.0.0")
    final_port = port or sygaldry_config.get("default_mcp_port", 8000)

    agent_dir_str = sygaldry_config.get("agentDirectory")
    if not agent_dir_str:
        console.print("[bold red]Error: Agent directory not configured in sygaldry.json.[/bold red]")
        raise typer.Exit(code=1)

    agent_path = config_manager.project_root / Path(agent_dir_str) / agent_name
    mcp_server_file = agent_path / "mcp_server.py"

    if not mcp_server_file.exists():
        console.print(
            f"[bold red]Error: MCP server entrypoint 'mcp_server.py' not found for agent '{agent_name}' "
            f"at {mcp_server_file}.[/bold red]"
        )
        console.print(f"Ensure the agent '{agent_name}' is correctly structured and includes an 'mcp_server.py' file.")
        raise typer.Exit(code=1)

    console.print(f"[cyan]Attempting to run agent '{agent_name}' using MCP ({mode.lower()} mode)...[/cyan]")
    console.print(f"MCP server script: {mcp_server_file}")
    if mode.lower() in ("http", "sse"):
        console.print(f"HTTP/SSE server will be started at: http://{final_host}:{final_port}")

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", str(mcp_server_file), "--mode", mode.lower(), "--host", final_host, "--port", str(final_port)],
        env=None,
    )

    async def _run_client():
        try:
            client_context = None
            if mode.lower() in ("http", "sse"):
                # Allow some time for the server to start
                await asyncio.sleep(2)  # TODO: Make this more robust, e.g., with retries or health check
                url = f"http://{final_host}:{final_port}"
                console.print(f"[cyan]Connecting to SSE client at: {url}[/cyan]")
                client_context = sse_client(url)
            else:  # stdio mode
                client_context = stdio_client(server_params)

            async with client_context as client:
                console.print(f"[green]Successfully connected to MCP server for '{agent_name}'.[/green]")
                console.print("Attempting to list prompts...")
                try:
                    prompts = await client.list_prompts()
                    if prompts:
                        console.print(f"[bold green]Available prompts for '{agent_name}':[/bold green]")
                        for p in prompts:
                            console.print(f"  - Name: {p.name}")
                            console.print(f"    Description: {p.description}")
                            if p.arguments:
                                console.print("    Arguments:")
                                for arg in p.arguments:
                                    console.print(f"      - {arg.name} (Required: {arg.required})")
                                    if arg.description:
                                        console.print(f"        Description: {arg.description}")
                    else:
                        console.print(f"[yellow]No prompts exposed by agent '{agent_name}'.[/yellow]")

                    if prompts and any(p.name == "echo_agent_prompt" for p in prompts):
                        console.print("\nAttempting to get template for 'echo_agent_prompt'...")
                        try:
                            template = await client.get_prompt_template("echo_agent_prompt")
                        except Exception as e:
                            console.print(f"[red]Error getting prompt template: {e}[/red]")

                except Exception as e:
                    console.print(f"[bold red]Error interacting with MCP server: {e}[/bold red]")
                    console.print(
                        "This might happen if the agent doesn't expose prompts/tools as expected, or an issue within the agent itself."
                    )

        except ConnectionRefusedError:
            console.print(f"[bold red]Error: Connection refused by MCP server for agent '{agent_name}'.[/bold red]")
            console.print("Ensure the agent's MCP server script is runnable and correctly configured.")
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred while running agent '{agent_name}': {e}[/bold red]")

    try:
        asyncio.run(_run_client())
    except KeyboardInterrupt:
        console.print("\n[yellow]Agent run interrupted by user.[/yellow]")
    finally:
        console.print(f"[cyan]Finished running agent '{agent_name}'.[/cyan]")


if __name__ == "__main__":
    dummy_config_path = Path.cwd() / "sygaldry.json"
    if not dummy_config_path.exists():
        dummy_config_content = {
            "$schema": "./sygaldry.schema.json",
            "agentDirectory": "packages/sygaldry_registry/components/agents",
            "defaultProvider": "openai",
            "defaultModel": "gpt-4o-mini",
            "stream": False,
        }
        import json

        with open(dummy_config_path, "w") as f:
            json.dump(dummy_config_content, f, indent=2)
        print(f"Created dummy {dummy_config_path} for testing.")

    dummy_agent_base = Path.cwd() / "packages/sygaldry_registry/components/agents"
    dummy_agent_path = dummy_agent_base / "echo_agent"
    dummy_mcp_server = dummy_agent_path / "mcp_server.py"

    if not dummy_mcp_server.exists():
        dummy_agent_path.mkdir(parents=True, exist_ok=True)
        dummy_mcp_content = '''
# Dummy mcp_server.py for testing run_agent_cmd.py
import sys
print(f"Dummy MCP Server started with args: {sys.argv}")
if __name__ == "__main__":
    print("Dummy server running. This script would typically start a Mirascope MCP server.")
'''
        with open(dummy_mcp_server, "w") as f:
            f.write(dummy_mcp_content)
        print(f"Created dummy {dummy_mcp_server} for testing.")

    if len(sys.argv) > 1:
        test_agent_name = sys.argv[1]
        console.print(f"[magenta]Running test for agent: {test_agent_name}[/magenta]")
        try:
            run_mcp_agent(agent_name=test_agent_name, mode="stdio")
        except SystemExit as e:
            console.print(
                f"[yellow]Script exited with code {e.code}. This is expected if errors are caught by Typer.Exit.[/yellow]"
            )
        except Exception as e:
            console.print(f"[bold red]Test run failed: {e}[/bold red]")
    else:
        console.print("[bold yellow]To test: python src/sygaldry_cli/commands/mcp_cmd.py <agent_name>[/bold yellow]")
        console.print("Example: python src/sygaldry_cli/commands/mcp_cmd.py echo_agent")
