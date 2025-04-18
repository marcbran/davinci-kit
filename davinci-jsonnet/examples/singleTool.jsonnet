local d = import '../main.libsonnet';

d.MediaInOut(
  function(mediaIn)
    // The blur tool is return from the function and thus will be connected to the MediaOut tool
    d.Blur('Foo', {
      Inputs: {
        // The blur tool is using the provided MediaIn tool's output as its input
        Input: d.Input.Output(mediaIn),
      },
    }),
)
