import os
import logging
from pathlib import Path

def setup_logging():
    """Set up logging to files in $XDG_DATA_HOME/davinci-cli/ for each log level."""
    # Get XDG_DATA_HOME, default to ~/.local/share if not set
    xdg_data_home = os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local' / 'share'))
    log_dir = Path(xdg_data_home) / 'davinci-cli'
    
    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Set up handlers for each log level
    log_levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    for level_name, level in log_levels.items():
        handler = logging.FileHandler(log_dir / f'{level_name}.log')
        handler.setLevel(level)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    
    # Also log to stderr for critical and error levels
    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)
    root_logger.addHandler(stderr_handler) 