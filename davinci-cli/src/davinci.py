import DaVinciResolveScript as dvr_script
import subprocess
import json

class DavinciError(Exception):
    pass

def get_framerate(video_path):
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=r_frame_rate',
        '-of', 'json',
        video_path
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error: Could not retrieve video information for {video_path}")
        print(f"Error details: {result.stderr}")
        return None

    try:
        info = json.loads(result.stdout)
        framerate_str = info['streams'][0]['r_frame_rate']
        num, denom = map(int, framerate_str.split('/'))
        framerate = num / denom
        return framerate
    except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
        print(f"Error parsing framerate information: {e}")
        print(f"ffprobe output: {result.stdout}")
        return None


def get_current_project() -> object:
    resolve = dvr_script.scriptapp("Resolve")
    projectManager = resolve.GetProjectManager()
    project = projectManager.GetCurrentProject()
    
    if project == None:
        raise DavinciError("no project is currently open")
        
    return project

def get_current_timeline() -> object:
    project = get_current_project()
    timeline = project.GetCurrentTimeline()
    
    if timeline == None:
        raise DavinciError("no timeline is currently active")
        
    return timeline

def get_current_video_item() -> object:
    timeline = get_current_timeline()
    current_item = timeline.GetCurrentVideoItem()
    
    if current_item == None:
        raise DavinciError("no video item is currently selected")
        
    return current_item 

def get_current_media_pool_item() -> object:
    video_item = get_current_video_item()
    media_pool_item = video_item.GetMediaPoolItem()
    
    if media_pool_item == None:
        raise DavinciError("no video item is currently selected")
        
    return media_pool_item

def get_composition(clear, add) -> object:
    video_item = get_current_video_item()
    composition = video_item.GetFusionCompByIndex(1)

    composition_name = None
    if add:
        old_compositions = video_item.GetFusionCompNameList()
        video_item.AddFusionComp()
        new_compositions = video_item.GetFusionCompNameList()
        composition_name = list(set(new_compositions) - set(old_compositions))[0]
    else:
        composition_name = video_item.GetFusionCompNameList()[-1]

    composition = video_item.GetFusionCompByName(composition_name)

    if clear:
        for name in video_item.GetFusionCompNameList():
            if name != composition_name:
                video_item.DeleteFusionCompByName(name)

        composition.FindToolByID('MediaIn').Delete()
        composition.FindToolByID('MediaOut').Delete()

    if composition == None:
        raise DavinciError("no composition is currently active")
        
    return composition
