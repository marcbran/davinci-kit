local d = import './main.libsonnet';

local namedTableTests = {
  name: 'named table',
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
      input:: d.Input {
        Value: 3840,
      },
      expected: '{"Value": 3840,"__name__": "Input"}',
    },
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

{
  output(input): std.manifestJsonEx(input, indent='', newline=''),
  tests: [
    namedTableTests,
  ],
}
