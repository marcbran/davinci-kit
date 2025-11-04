local d = import '../main.libsonnet';

d.Effect(
  function(mediaIn)
    local mask = d.EllipseMask('Foo', {});
    local blur = d.Blur('Foo', {
      Inputs: {
        Input: mediaIn,
        EffectMask: mask,
      },
    });
    d.Group('Foo', {
      Outputs: {
        Output1: blur,
      },
    }),
)
