local d = import '../main.libsonnet';

d.Effect(
  function(mediaIn)
    local mask = d.EllipseMask('Foo', {
      Inputs: {
        // The path input will create a PolyLine under the hood to attach the path to the receiving tool
        // It also creates a displacement BezierSpline input to animate along the path according to the provided keyframes
        //
        // The points are considered as displacements from the center point (0.5, 0.5)
        Center: d.Path('Foo', {
          '0': { X: 0, Y: 0 },
          '30': { X: 1, Y: 1 },
        }),
      },
    });
    d.Blur('Foo', {
      Inputs: {
        Input: mediaIn,
        EffectMask: mask,
      },
    }),
)
