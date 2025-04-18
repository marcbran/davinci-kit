local d = import '../main.libsonnet';

d.MediaInOut(
  function(mediaIn)
    local mask = d.PolylineMask('Foo', {
      Inputs: {
        // The polyline input can be used to animate a polyline (or polygon) between multiple key frames
        Polyline: d.Input.Polyline('Foo', {
          '0': d.Polyline {
            Closed: true,
            Points: [{ X: 0, Y: 0 }, { X: 1, Y: 0 }, { X: 1, Y: 1 }, { X: 0, Y: 1 }],
          },
          '30': d.Polyline {
            Closed: true,
            Points: [{ X: -1, Y: -1 }, { X: 2, Y: -1 }, { X: 2, Y: 2 }, { X: -1, Y: 2 }],
          },
        }),
      },
    });
    d.Blur('Foo', {
      Inputs: {
        Input: d.Input.Output(mediaIn),
        EffectMask: d.Input.Mask(mask),
      },
    }),
)
