# Unofficial davinci-cli

A command-line interface tool for DaVinci Resolve that enables automation and project management.
This tool provides a set of commands to interact with DaVinci Resolve projects, timelines, and compositions.
It is nothing but a thin wrapper around the Python API provided by Blackmagic Design.

## Disclaimer

This project is not affiliated with DaVinci Resolve or Blackmagic Design.

It is a personal initiative created to explore AI-assisted coding.
While the tool functions as intended, the codebase is experimental and lacks refinement.

Use at your own discretion. It is not recommended for use in critical or production environments.

## Features

- Project management and information retrieval
- Timeline operations and metadata access
- Video item manipulation
- Media pool item management
- Composition node copying and pasting
- JSON support for composition settings

## Installation

1. Ensure you have Python 3.11 or higher installed
2. Also ensure that you have DaVinci Resolve installed and running in the background
3. Install the package locally:
   ```bash
   just install
   ```
4. Set these environment variables
   ```bash
   RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/"
   RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
   PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
   ```

## Usage

The CLI provides several command groups for different aspects of DaVinci Resolve:

### Project Commands

```bash
# Get information about the current project
davinci project get
```

### Timeline Commands

```bash
# Get information about the current timeline
davinci timeline get
```

### Video Item Commands

```bash
# Get information about the current video item
davinci video-item get
```

### Media Pool Item Commands

```bash
# Get information about the current media pool item
davinci media-pool-item get
```

### Composition Commands

```bash
# Copy the current composition settings
davinci comp copy

# Copy composition settings as JSON
davinci comp copy --json

# Paste composition settings
davinci comp paste

# Paste composition settings from JSON
davinci comp paste --json

# Clear existing compositions before pasting
davinci comp paste --clear
```

## Development

To set up the development environment:

1. Clone the repository
2. Install development dependencies:
   ```bash
   just dev-install
   ```
3. Run tests:
   ```bash
   just test
   ```

## Requirements

- Python 3.11+
- DaVinci Resolve
- Justfile
- click>=8.1.0
- pyperclip>=1.8.2
