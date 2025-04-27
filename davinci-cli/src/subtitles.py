import logging
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from src.davinci import get_current_timeline

def extract_subtitles(timeline, track_num):
    """Extract subtitle items from a specific track into a list of objects with text, start, and end."""
    subtitle_objects = []
    
    items = timeline.GetItemListInTrack("subtitle", track_num)
    items = sorted(items, key=lambda item: item.GetStart())

    for item in items:
        subtitle_objects.append({
            "text": item.GetName(),
            "start": item.GetStart(),
            "end": item.GetEnd()
        })

    return subtitle_objects

def export_subtitles(tracks):
    """Export subtitles from specified tracks."""
    try:
        timeline = get_current_timeline()
        
        all_subtitles = []
        for track_num in tracks:
            track_subtitles = extract_subtitles(timeline, track_num)
            all_subtitles.extend(track_subtitles)
        
        all_subtitles = sorted(all_subtitles, key=lambda subtitle: subtitle["start"])
        
        return all_subtitles
    except Exception as e:
        logging.error(f"Failed to export subtitles: {str(e)}")
        raise

def format_subtitles(subtitles, format_type="text"):
    """Format subtitles according to the specified format type."""
    if format_type == "json":
        return json.dumps(subtitles, indent=2)
    elif format_type == "text":
        return "\n".join([subtitle["text"] for subtitle in subtitles])
    elif format_type == "srt":
        return format_srt(subtitles)
    elif format_type == "ttml":
        return format_ttml(subtitles)
    else:
        raise ValueError(f"Unsupported format: {format_type}")

def format_srt(subtitles):
    """Format subtitles as SRT."""
    timeline = get_current_timeline()
    frame_rate = float(timeline.GetSetting("timelineFrameRate"))
    
    srt_lines = []
    for i, subtitle in enumerate(subtitles, 1):
        # Convert frame numbers to time using the actual frame rate
        start_time = format_time_srt(subtitle["start"], frame_rate)
        end_time = format_time_srt(subtitle["end"], frame_rate)
        srt_lines.append(f"{i}\n{start_time} --> {end_time}\n{subtitle['text']}\n")
    return "\n".join(srt_lines)

def format_time_srt(frames, fps=24):
    """Convert frame number to SRT time format (HH:MM:SS,mmm)."""
    seconds = frames / fps
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def format_ttml(subtitles):
    """Format subtitles as TTML with pretty printing."""
    timeline = get_current_timeline()
    frame_rate = float(timeline.GetSetting("timelineFrameRate"))
    
    # Create the root element
    root = ET.Element("tt", {
        "xml:lang": "en",
        "xmlns": "http://www.w3.org/ns/ttml",
        "xmlns:ttm": "http://www.w3.org/ns/ttml#metadata",
        "xmlns:tts": "http://www.w3.org/ns/ttml#styling",
        "xmlns:ttp": "http://www.w3.org/ns/ttml#parameter",
        "xmlns:ittp": "http://www.w3.org/ns/ttml/profile/imsc1#parameter",
        "xmlns:itts": "http://www.w3.org/ns/ttml/profile/imsc1#styling",
        "ttp:profile": "http://www.w3.org/ns/ttml/profile/imsc1/text",
        "ttp:frameRate": str(frame_rate),
        "ttp:timeBase": "media"
    })
    
    # Create head element
    head = ET.SubElement(root, "head")
    
    # Create styling element
    styling = ET.SubElement(head, "styling")
    style = ET.SubElement(styling, "style", {
        "xml:id": "default_style",
        "tts:color": "#ffffff",
        "tts:opacity": "1",
        "tts:fontSize": "100%",
        "tts:fontFamily": "default",
        "tts:fontWeight": "bold",
        "tts:textAlign": "center"
    })
    
    # Create layout element
    layout = ET.SubElement(head, "layout")
    region = ET.SubElement(layout, "region", {
        "xml:id": "default_region",
        "tts:origin": "7.919% 83.140%",
        "tts:extent": "84.193% 16.898%",
        "tts:displayAlign": "center"
    })
    
    # Create body element
    body = ET.SubElement(root, "body")
    
    # Create div element
    div = ET.SubElement(body, "div", {
        "xml:id": "d0",
        "region": "default_region",
        "style": "default_style"
    })
    
    # Add subtitle paragraphs
    for subtitle in subtitles:
        start_time = format_time_ttml(subtitle["start"], frame_rate)
        end_time = format_time_ttml(subtitle["end"], frame_rate)
        p = ET.SubElement(div, "p", {
            "begin": start_time,
            "end": end_time
        })
        p.text = subtitle["text"]
    
    # Convert to string with proper XML declaration and pretty print
    xml_str = ET.tostring(root, encoding='unicode', method='xml')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")
    
    # Remove empty lines that minidom adds
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
    
    return pretty_xml

def format_time_ttml(frames, fps=24):
    """Convert frame number to TTML time format (HH:MM:SS.mmm)."""
    seconds = frames / fps
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}" 
