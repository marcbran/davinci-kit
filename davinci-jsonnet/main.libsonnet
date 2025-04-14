local type(t) = {
  __name__: t,
};

local mergeObjects(objs) = std.foldl(function(acc, curr) acc + curr, objs, {});

local mapKeys(value) =
  if std.type(value) == 'object'
  then
    if std.objectHas(value, '_')
    then value._.key
    else {
      [kv.key]: mapKeys(kv.value)
      for kv in std.objectKeysValues(value)
    }
  else
    if std.type(value) == 'array'
    then [mapKeys(elem) for elem in value]
    else value;

local extractTools(value) =
  if std.type(value) == 'object'
  then
    if std.objectHas(value, '_')
    then value._.tools
    else mergeObjects([extractTools(kv.value) for kv in std.objectKeysValues(value)])
  else
    if std.type(value) == 'array'
    then mergeObjects([extractTools(elem) for elem in value])
    else {};

local tool(t, key, value={}) = {
  _: {
    local _ = self,
    key: '%s%s' % [t, key],
    value: type(t) + mapKeys(value),
    tools: { [_.key]: _.value } + extractTools(value),
  },
};

local toolType(type) = function(key, value={}) tool(type, key, value);

local toolNames = [
  'Background',
  'BezierSpline',
  'Blur',
  'EllipseMask',
  'MediaIn',
  'MediaOut',
  'Merge',
  'PolyPath',
  'Transform',
];

local typeNames = [
  'AudioDisplay',
  'FuID',
  'OperatorInfo',
  'Polyline',
];

local functionNames = [
  'ordered',
];

local tools = {
  [tool]: toolType(tool)
  for tool in toolNames
};

local types = {
  [t]: type(t)
  for t in typeNames
};

local functions = {
  [func]: function() type('%s()' % func)
  for func in functionNames
};

local inputs = {
  Input:: {
    local input(tool, source) =
      if std.type(tool) == 'object' && std.objectHas(tool, '_')
      then type('Input') {
        SourceOp: tool,
        Source: source,
      }
      else type('Input') {
        [source]: tool,
      },
    Output(tool):: input(tool, 'Output'),
    Mask(tool):: input(tool, 'Mask'),
    Position(tool):: input(tool, 'Position'),
    Value(tool):: input(tool, 'Value'),
    BezierSpline(key, keyFrames):: $.Input.Value($.BezierSpline(key, {
      KeyFrames: keyFrames,
    })),
    Path(key, keyFrames)::
      local sortedKeyValues = std.sort(std.objectKeysValues(keyFrames), function(kv) std.parseInt(kv.key));
      local length = std.length(sortedKeyValues);
      self.Position($.PolyPath(key, {
        Inputs: {
          PolyLine: $.Input.Value($.Polyline {
            Points: [kv.value for kv in sortedKeyValues],
          }),
          Displacement: $.Input.Value($.BezierSpline(key, {
            KeyFrames: {
              [kvi.key]: [if length > 1 then kvi.i / (length - 1) else 1]
              for kvi in std.mapWithIndex(function(i, kv) { i: i } + kv, sortedKeyValues)
            },
          })),
        },
      })),
  },
  Inputs:: {
    KeyFrames(key, keyFrames):
      local sortedKeyValues = std.sort(std.objectKeysValues(keyFrames), function(kv) std.parseInt(kv.key));
      if std.length(sortedKeyValues) == 0 then {} else
        local prototypeKeyFrame = sortedKeyValues[0].value;
        {
          [inputKv.key]:
            if std.type(prototypeKeyFrame[inputKv.key]) == 'object'
            then $.Input.Path('%s%s' % [inputKv.key, key], {
              [frameKv.key]: frameKv.value[inputKv.key]
              for frameKv in sortedKeyValues
            })
            else $.Input.BezierSpline('%s%s' % [inputKv.key, key], {
              [frameKv.key]: frameKv.value[inputKv.key]
              for frameKv in sortedKeyValues
            })
          for inputKv in std.objectKeysValues(prototypeKeyFrame)
        },
  },
};

local main = {
  Tools(tools): {
    Tools: $.ordered() + extractTools(tools),
  },
  MediaInOut(processor):
    $.Tools([
      $.MediaOut('1', {
        Inputs: {
          Input: $.Input.Output(processor($.MediaIn('1'))),
        },
      }),
    ]),
};

tools + types + functions + inputs + main
