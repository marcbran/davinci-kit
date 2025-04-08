import click
import json
import src.davinci as davinci
import pyperclip
import src.macro as macro

@click.group()
def cli():
    """DaVinci Resolve CLI tool for automation and project management."""
    pass

@cli.group()
def project():
    """Commands for working with the current project."""
    pass

@project.command()
def get():
    """Get information about the current project."""
    try:
        project = davinci.get_current_project()
        click.echo(json.dumps({
            "name": project.GetName(),
        }, indent=2))
    except davinci.DavinciError as e:
        click.echo(str(e), err=True)
        return 1

@cli.group()
def timeline():
    """Commands for working with the current timeline."""
    pass

@timeline.command()
def get():
    """Get information about the current timeline."""
    try:
        timeline = davinci.get_current_timeline()
        click.echo(json.dumps({
            "name": timeline.GetName(),
            "fps": timeline.GetSetting("fps"),
            "start_frame": timeline.GetStartFrame(),
            "end_frame": timeline.GetEndFrame(),
            "track_count": {
                "video": timeline.GetTrackCount("video"),
                "audio": timeline.GetTrackCount("audio"),
                "subtitle": timeline.GetTrackCount("subtitle")
            }
        }, indent=2))
    except davinci.DavinciError as e:
        click.echo(str(e), err=True)
        return 1

@cli.group()
def video_item():
    """Commands for working with the current video item in timeline."""
    pass

@video_item.command()
def get():
    """Get information about the current video item."""
    try:
        item = davinci.get_current_video_item()
        click.echo(json.dumps({
            "name": item.GetName(),
            "start_frame": item.GetStart(),
            "end_frame": item.GetEnd(),
            "duration": item.GetDuration()
        }, indent=2))
    except davinci.DavinciError as e:
        click.echo(str(e), err=True)
        return 1

@cli.group()
def comp():
    """Commands for working with the composition in the current video item."""
    pass

@comp.command()
def get():
    """Get information about the current composition."""
    try:
        composition = davinci.get_current_composition()
        click.echo(json.dumps({}, indent=2))
    except davinci.DavinciError as e:
        click.echo(str(e), err=True)
        return 1

@comp.command()
@click.option('--json', 'output_json', is_flag=True, help='Output the setting as parsed JSON')
def copy(output_json):
    """Copy the selected nodes from the current composition."""
    try:
        original_clipboard = pyperclip.paste()
        
        composition = davinci.get_current_composition()
        composition.Copy()
        settings = pyperclip.paste()
        
        output = settings
        if output_json:
            content = macro.parse(settings)
            output = json.dumps(content, indent=2)

        click.echo(output)

    except davinci.DavinciError as e:
        click.echo(str(e), err=True)
        return 1
    finally:
        pyperclip.copy(original_clipboard)

@comp.command()
@click.option('--json', 'input_json', is_flag=True, help='Parse the input as JSON and convert to Lua table format')
def paste(input_json):
    """Paste content from stdin into the current composition."""
    try:
        original_clipboard = pyperclip.paste()
        
        input = click.get_text_stream('stdin').read()
        
        settings = input
        if input_json:
            try:
                content = json.loads(input)
                settings = macro.manifest(content)
            except json.JSONDecodeError as e:
                click.echo(f"Error parsing JSON: {str(e)}", err=True)
                return 1
        
        pyperclip.copy(settings)
        composition = davinci.get_current_composition()
        composition.Paste()
        
    except davinci.DavinciError as e:
        click.echo(str(e), err=True)
        return 1
    finally:
        pyperclip.copy(original_clipboard)

if __name__ == "__main__":
    cli()
