# Unofficial davinci-jsonnet

A Jsonnet library for programmatically creating DaVinci Resolve Fusion compositions.
This library provides a composable way to create complex node graphs for DaVinci Resolve's Fusion page.

## Disclaimer

This project is not affiliated with DaVinci Resolve or Blackmagic Design.

It is a personal initiative created to explore AI-assisted coding.
While the tool functions as intended, the codebase is experimental and lacks refinement.

Use at your own discretion. It is not recommended for use in critical or production environments.

## Features

- DSL for tool creation and connection
- Support for various input types:
  - Media input/output
  - Masks (Ellipse, Polyline)
  - Bezier splines for animation
  - Path animation
  - Polyline animation
- Composable tool creation
- Automatic tool ordering
- Helper functions for common patterns

## Installation

1. Make sure you have [Jsonnet](https://jsonnet.org/) and [jsonnet-bundler](https://github.com/jsonnet-bundler/jsonnet-bundler) installed
2. Install the library

   ```bash
   jb install https://github.com/marcbran/jsonnet.git/davinci@davinci
   ```

3. Import the library in your Jsonnet files:
    ```jsonnet
    local d = import 'davinci/main.libsonnet';

    d.MediaInOut(
      function(mediaIn)
        // The blur tool is return from the function and thus will be connected to the MediaOut tool
        d.Blur('Foo', {
          Inputs: {
            // The blur tool is using the provided MediaIn tool's output as its input
            Input: d.Input.Output(mediaIn),
          },
        }),
    )
    ```

## Usage

Please see [the examples](examples/README.md) for details on how to use this library.

This tool can be combined with its sibling, the davinci-cli, to create compositions and paste them into DaVinci Resolve:

```bash
jsonnet ./examples/singleTool.jsonnet | davinci comp paste --clear --json
```

## Development

To set up the development environment:

1. Clone the repository
2. Run tests:
   ```bash
   just test
   ```
