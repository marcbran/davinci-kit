local d = import '../main.libsonnet';

d.Effect(
  function(mediaIn)
    // The blur tool is returned from the function and thus will be connected to the MediaOut tool
    d.Blur('Foo', {
      Inputs: {
        // The blur tool is using the provided MediaIn tool's output as its input
        Input: mediaIn,
        // Scalar values will be automatically wrapped in Value Inputs
        XBlurSize: 10,
      },
    }),
)
