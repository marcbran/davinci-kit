local d = import '../main.libsonnet';

d.MediaInOut(
  function(mediaIn)
    local mask = d.EllipseMask('Foo', {
      // The key frames input can be used when animating multiple values between the same key frames
      // It will use different input types (BezierSpline, Path, Polyline, etc) depending on the structure of the provided input
      Inputs: d.Inputs.KeyFrames('Foo', {
        '0': {
          Width: 0.5,
          Height: 0.5,
          Center: { X: 0, Y: 0 },
        },
        '30': {
          Width: 0.75,
          Height: 0.25,
          Center: { X: 0.5, Y: 0.5 },
        },
      }),
    });
    d.Blur('Foo', {
      Inputs: {
        Input: d.Input.Output(mediaIn),
        EffectMask: d.Input.Mask(mask),
      },
    }),
)
