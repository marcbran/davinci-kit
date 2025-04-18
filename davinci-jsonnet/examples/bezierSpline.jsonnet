local d = import '../main.libsonnet';

d.MediaInOut(
  function(mediaIn)
    d.Blur('Foo', {
      Inputs: {
        Input: d.Input.Output(mediaIn),
        // The bezier spline input will animate a single value between the provided key frames
        XBlurSize: d.Input.BezierSpline('Foo', {
          '0': 0,
          '30': 1,
        }),
      },
    }),
)
