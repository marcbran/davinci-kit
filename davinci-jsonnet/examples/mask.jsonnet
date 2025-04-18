local d = import '../main.libsonnet';

d.MediaInOut(
  function(mediaIn)
    local mask = d.EllipseMask('Foo', {});
    d.Blur('Foo', {
      Inputs: {
        Input: d.Input.Output(mediaIn),
        // The mask tool's input connects the provided mask tool to the mask input of the receiving tool
        EffectMask: d.Input.Mask(mask),
      },
    }),
)
