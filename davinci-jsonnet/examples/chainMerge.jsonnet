local d = import '../main.libsonnet';

d.Generator(
  // The ChainMerge function is a utility to chain n tools together with n-1 Merge tools
  d.ChainMerge('FooBar', [
    d.EllipseMask('Foo', {}),
    d.EllipseMask('Bar', {}),
    d.EllipseMask('Baz', {}),
  ]),
)
