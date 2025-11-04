local d = import '../main.libsonnet';

d.Effect(
  function(mediaIn)
    d.Blur('Foo', {
      Inputs: {
        Input: mediaIn,
        // The bezier spline input will animate a single value between the provided key frames
        XBlurSize: d.BezierSpline('Foo', {
          '0': 0,
          '30': 1,
        }),
      },
    }),
)
