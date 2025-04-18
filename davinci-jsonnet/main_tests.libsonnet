local d = import './main.libsonnet';

local toolTests = {
  name: 'tool',
  tests: [
    {
      name: 'Blur',
      input:: d.Blur('Foo', {
        Inputs: {},
      }),
      expected: '{"_": {"key": "BlurFoo","tools": {"BlurFoo": {"Inputs": {},"__name__": "Blur"}},"value": {"Inputs": {},"__name__": "Blur"}}}',
    },
  ],
};

local typeTests = {
  name: 'type',
  tests: [
    {
      name: 'AudioDisplay',
      input:: d.AudioDisplay {
        CtrlWZoom: false,
      },
      expected: '{"CtrlWZoom": false,"__name__": "AudioDisplay"}',
    },
    {
      name: 'Input',
      input:: d.Polyline {
        Points: [],
      },
      expected: '{"Points": [],"__name__": "Polyline"}',
    },
  ],
};

local functionTests = {
  name: 'function',
  tests: [
    {
      name: 'ordered()',
      input:: {
        Tools: d.ordered() {
          Left_1: d.AudioDisplay {
            CtrlWZoom: false,
          },
        },
      },
      expected: '{"Tools": {"Left_1": {"CtrlWZoom": false,"__name__": "AudioDisplay"},"__name__": "ordered()"}}',
    },
  ],
};

local inputTests = {
  name: 'input',
  tests: [
    {
      name: 'output',
      input:: d.Blur('Foo', {
        Inputs: {
          Input: d.Input.Output(d.MediaIn('1')),
        },
      }),
      expected: '{"_": {"key": "BlurFoo","tools": {"BlurFoo": {"Inputs": {"Input": {"Source": "Output","SourceOp": "MediaIn1","__name__": "Input"}},"__name__": "Blur"},"MediaIn1": {"__name__": "MediaIn"}},"value": {"Inputs": {"Input": {"Source": "Output","SourceOp": "MediaIn1","__name__": "Input"}},"__name__": "Blur"}}}',
    },
    {
      name: 'mask',
      input::
        local mask = d.EllipseMask('Foo', {
          Inputs: {},
        });
        d.Blur('Foo', {
          Inputs: {
            EffectMask: d.Input.Mask(mask),
          },
        }),
      expected: '{"_": {"key": "BlurFoo","tools": {"BlurFoo": {"Inputs": {"EffectMask": {"Source": "Mask","SourceOp": "EllipseMaskFoo","__name__": "Input"}},"__name__": "Blur"},"EllipseMaskFoo": {"Inputs": {},"__name__": "EllipseMask"}},"value": {"Inputs": {"EffectMask": {"Source": "Mask","SourceOp": "EllipseMaskFoo","__name__": "Input"}},"__name__": "Blur"}}}',
    },
  ],
};

local integrationTests = {
  name: 'integration',
  tests: [
    {
      name: 'bezierSpline',
      input:: import './examples/bezierSpline.jsonnet',
      expected: '{"Tools": {"BezierSplineFoo": {"KeyFrames": {"0": 0,"30": 1},"__name__": "BezierSpline"},"BlurFoo": {"Inputs": {"Input": {"Source": "Output","SourceOp": "MediaIn1","__name__": "Input"},"XBlurSize": {"Source": "Value","SourceOp": "BezierSplineFoo","__name__": "Input"}},"__name__": "Blur"},"MediaIn1": {"__name__": "MediaIn"},"MediaOut1": {"Inputs": {"Input": {"Source": "Output","SourceOp": "BlurFoo","__name__": "Input"}},"__name__": "MediaOut"},"__name__": "ordered()"}}',
    },
    {
      name: 'keyframes',
      input:: import './examples/keyframes.jsonnet',
      expected: '{"Tools": {"BezierSplineCenterFoo": {"KeyFrames": {"0": 0,"30": 1},"__name__": "BezierSpline"},"BezierSplineHeightFoo": {"KeyFrames": {"0": 0.5,"30": 0.25},"__name__": "BezierSpline"},"BezierSplineWidthFoo": {"KeyFrames": {"0": 0.5,"30": 0.75},"__name__": "BezierSpline"},"BlurFoo": {"Inputs": {"EffectMask": {"Source": "Mask","SourceOp": "EllipseMaskFoo","__name__": "Input"},"Input": {"Source": "Output","SourceOp": "MediaIn1","__name__": "Input"}},"__name__": "Blur"},"EllipseMaskFoo": {"Inputs": {"Center": {"Source": "Position","SourceOp": "PolyPathCenterFoo","__name__": "Input"},"Height": {"Source": "Value","SourceOp": "BezierSplineHeightFoo","__name__": "Input"},"Width": {"Source": "Value","SourceOp": "BezierSplineWidthFoo","__name__": "Input"}},"__name__": "EllipseMask"},"MediaIn1": {"__name__": "MediaIn"},"MediaOut1": {"Inputs": {"Input": {"Source": "Output","SourceOp": "BlurFoo","__name__": "Input"}},"__name__": "MediaOut"},"PolyPathCenterFoo": {"Inputs": {"Displacement": {"Source": "Value","SourceOp": "BezierSplineCenterFoo","__name__": "Input"},"PolyLine": {"Value": {"Points": [{"X": 0,"Y": 0},{"X": 0.5,"Y": 0.5}],"__name__": "Polyline"},"__name__": "Input"}},"__name__": "PolyPath"},"__name__": "ordered()"}}',
    },
    {
      name: 'mask',
      input:: import './examples/mask.jsonnet',
      expected: '{"Tools": {"BlurFoo": {"Inputs": {"EffectMask": {"Source": "Mask","SourceOp": "EllipseMaskFoo","__name__": "Input"},"Input": {"Source": "Output","SourceOp": "MediaIn1","__name__": "Input"}},"__name__": "Blur"},"EllipseMaskFoo": {"__name__": "EllipseMask"},"MediaIn1": {"__name__": "MediaIn"},"MediaOut1": {"Inputs": {"Input": {"Source": "Output","SourceOp": "BlurFoo","__name__": "Input"}},"__name__": "MediaOut"},"__name__": "ordered()"}}',
    },
    {
      name: 'mediaInOut',
      input:: import './examples/mediaInOut.jsonnet',
      expected: '{"Tools": {"MediaIn1": {"__name__": "MediaIn"},"MediaOut1": {"Inputs": {"Input": {"Source": "Output","SourceOp": "MediaIn1","__name__": "Input"}},"__name__": "MediaOut"},"__name__": "ordered()"}}',
    },
    {
      name: 'path',
      input:: import './examples/path.jsonnet',
      expected: '{"Tools": {"BezierSplineFoo": {"KeyFrames": {"0": 0,"30": 1},"__name__": "BezierSpline"},"BlurFoo": {"Inputs": {"EffectMask": {"Source": "Mask","SourceOp": "EllipseMaskFoo","__name__": "Input"},"Input": {"Source": "Output","SourceOp": "MediaIn1","__name__": "Input"}},"__name__": "Blur"},"EllipseMaskFoo": {"Inputs": {"Center": {"Source": "Position","SourceOp": "PolyPathFoo","__name__": "Input"}},"__name__": "EllipseMask"},"MediaIn1": {"__name__": "MediaIn"},"MediaOut1": {"Inputs": {"Input": {"Source": "Output","SourceOp": "BlurFoo","__name__": "Input"}},"__name__": "MediaOut"},"PolyPathFoo": {"Inputs": {"Displacement": {"Source": "Value","SourceOp": "BezierSplineFoo","__name__": "Input"},"PolyLine": {"Value": {"Points": [{"X": 0,"Y": 0},{"X": 1,"Y": 1}],"__name__": "Polyline"},"__name__": "Input"}},"__name__": "PolyPath"},"__name__": "ordered()"}}',
    },
    {
      name: 'polyline',
      input:: import './examples/polyline.jsonnet',
      expected: '{"Tools": {"BezierSplineFoo": {"KeyFrames": {"0": {"1": 0,"Value": {"Closed": true,"Points": [{"X": 0,"Y": 0},{"X": 1,"Y": 0},{"X": 1,"Y": 1},{"X": 0,"Y": 1}],"__name__": "Polyline"}},"30": {"1": 1,"Value": {"Closed": true,"Points": [{"X": -1,"Y": -1},{"X": 2,"Y": -1},{"X": 2,"Y": 2},{"X": -1,"Y": 2}],"__name__": "Polyline"}}},"__name__": "BezierSpline"},"BlurFoo": {"Inputs": {"EffectMask": {"Source": "Mask","SourceOp": "PolylineMaskFoo","__name__": "Input"},"Input": {"Source": "Output","SourceOp": "MediaIn1","__name__": "Input"}},"__name__": "Blur"},"MediaIn1": {"__name__": "MediaIn"},"MediaOut1": {"Inputs": {"Input": {"Source": "Output","SourceOp": "BlurFoo","__name__": "Input"}},"__name__": "MediaOut"},"PolylineMaskFoo": {"Inputs": {"Polyline": {"Source": "Value","SourceOp": "BezierSplineFoo","__name__": "Input"}},"__name__": "PolylineMask"},"__name__": "ordered()"}}',
    },
    {
      name: 'singleTool',
      input:: import './examples/singleTool.jsonnet',
      expected: '{"Tools": {"BlurFoo": {"Inputs": {"Input": {"Source": "Output","SourceOp": "MediaIn1","__name__": "Input"}},"__name__": "Blur"},"MediaIn1": {"__name__": "MediaIn"},"MediaOut1": {"Inputs": {"Input": {"Source": "Output","SourceOp": "BlurFoo","__name__": "Input"}},"__name__": "MediaOut"},"__name__": "ordered()"}}',
    },
  ],
};

{
  output(input): std.manifestJsonEx(input, indent='', newline=''),
  tests: [
    toolTests,
    typeTests,
    functionTests,
    inputTests,
    integrationTests,
  ],
}
