import click
import json
import src.davinci as davinci
import pyperclip
import src.macro as macro
import logging
from src.logger import setup_logging

@click.group()
def cli():
    """DaVinci Resolve CLI tool for automation and project management."""
    setup_logging()
    logging.info("DaVinci CLI started")
    pass

@cli.group()
def project():
    """Commands for working with the current project."""
    pass

@project.command()
def get():
    """Get information about the current project."""
    try:
        logging.debug("Getting current project information")
        project = davinci.get_current_project()
        info = {
            "name": project.GetName(),
        }
        logging.info(f"Retrieved project information: {info}")
        click.echo(json.dumps(info, indent=2))
    except davinci.DavinciError as e:
        logging.error(f"Failed to get project information: {str(e)}")
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
        logging.debug("Getting current timeline information")
        timeline = davinci.get_current_timeline()
        info = {
            "name": timeline.GetName(),
            "framerate": timeline.GetSetting("timelineFrameRate"),
            "start_frame": timeline.GetStartFrame(),
            "end_frame": timeline.GetEndFrame(),
            "track_count": {
                "video": timeline.GetTrackCount("video"),
                "audio": timeline.GetTrackCount("audio"),
                "subtitle": timeline.GetTrackCount("subtitle")
            }
        }
        logging.info(f"Retrieved timeline information: {info}")
        click.echo(json.dumps(info, indent=2))
    except davinci.DavinciError as e:
        logging.error(f"Failed to get timeline information: {str(e)}")
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
            "start": item.GetStart(),
            "end": item.GetEnd(),
            "duration": item.GetDuration(),
            "left_offset": item.GetLeftOffset(),
            "right_offset": item.GetRightOffset(),
        }, indent=2))
    except davinci.DavinciError as e:
        click.echo(str(e), err=True)
        return 1

@cli.group()
def media_pool_item():
    """Commands for working with the current media pool item."""
    pass

@media_pool_item.command()
def get():
    """Get information about the current media pool item."""
    try:
        item = davinci.get_current_media_pool_item()
        file = item.GetClipProperty("File Path")
        proxy = item.GetClipProperty('Proxy Media Path')
        media_start = int(item.GetClipProperty("Start"))
        media_end = int(item.GetClipProperty("End"))
        width, height = map(int, item.GetClipProperty("Resolution").split('x'))
        framerate = davinci.get_framerate(file)
        click.echo(json.dumps({
            "file": file,
            "proxy": proxy,
            'framerate': framerate,
            "media_start": media_start,
            "media_end": media_end,
            "width": width,
            "height": height,
        }, indent=2))
    except davinci.DavinciError as e:
        click.echo(str(e), err=True)
        return 1

@cli.group()
def comp():
    """Commands for working with the composition in the current video item."""
    pass

@comp.command()
@click.option('--json', 'output_json', is_flag=True, help='Output the setting as parsed JSON')
def copy(output_json):
    """Copy the selected nodes from the current composition."""
    try:
        logging.debug(f"Copying composition (output_json={output_json})")
        original_clipboard = pyperclip.paste()
        
        composition = davinci.get_composition(False)
        composition.Copy()
        settings = pyperclip.paste()
        
        output = settings
        if output_json:
            content = macro.parse(settings)
            output = json.dumps(content, indent=2)

        logging.info("Successfully copied composition settings")
        click.echo(output)

    except davinci.DavinciError as e:
        logging.error(f"Failed to copy composition: {str(e)}")
        click.echo(str(e), err=True)
        return 1
    finally:
        pyperclip.copy(original_clipboard)

@comp.command()
@click.option('--clear', 'clear', is_flag=True, help='Deletes all existing compositions in the current video item')
@click.option('--json', 'input_json', is_flag=True, help='Parse the input as JSON and convert to Lua table format')
def paste(clear, input_json):
    """Paste content from stdin into the current composition."""
    try:
        logging.debug(f"Pasting to composition (clear={clear}, input_json={input_json})")
        original_clipboard = pyperclip.paste()
        logging.info(f"Original clipboard: {original_clipboard}")
        
        input = click.get_text_stream('stdin').read()
        
        settings = input
        if input_json:
            try:
                content = json.loads(input)
                settings = macro.manifest(content)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON input: {str(e)}")
                click.echo(f"Error parsing JSON: {str(e)}", err=True)
                return 1

        click.echo(settings)

        pyperclip.copy(settings)
        composition = davinci.get_composition(clear)
        res = composition.Paste()
        logging.info(f"Paste result: {res}")
        
        logging.info("Successfully pasted composition settings")
        
    except davinci.DavinciError as e:
        logging.error(f"Failed to paste composition: {str(e)}")
        click.echo(str(e), err=True)
        return 1
    finally:
        pyperclip.copy(original_clipboard)

if __name__ == "__main__":
    cli()
