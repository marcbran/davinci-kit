import DaVinciResolveScript as dvr_script

class DavinciError(Exception):
    pass

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

def get_current_composition() -> object:
    video_item = get_current_video_item()
    composition = video_item.GetFusionCompByIndex(1)
    
    if composition == None:
        raise DavinciError("no composition is currently active")
        
    return composition
