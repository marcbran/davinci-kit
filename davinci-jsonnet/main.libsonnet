local mergeObjects(objs) = std.foldl(function(acc, curr) acc + curr, objs, {});

local named(t) = {
  __name__: t,
};

local functionNames = [
  'ordered',
];

local functions = {
  [func]: function() named('%s()' % func)
  for func in functionNames
};

local type(t, value) = {
  _: {
    ref(target='Input'):: named(target) {
      Value: named(t) + value,
    },
    value: named(t) + value,
  },
};

local typeNames = [
  'AudioDisplay',
  'FuID',
  'OperatorInfo',
  'Polyline',
];

local types = {
  [t]: function(value={}) type(t, value)
  for t in typeNames
};

local extractRefs(value, target='Input') =
  if std.type(value) == 'object' && std.objectHas(value, '_')
  then value._.ref(target)
  else named(target) {
    Value: value,
  };

local extractTools(value) =
  if std.type(value) == 'object'
  then
    if std.objectHas(value, '_')
    then
      if std.objectHas(value._, 'tools')
      then value._.tools
      else {}
    else mergeObjects([extractTools(kv.value) for kv in std.objectKeysValues(value)])
  else
    if std.type(value) == 'array'
    then mergeObjects([extractTools(elem) for elem in value])
    else {};

local extractMacroInputs(value) =
  if std.type(value) == 'object'
  then
    if std.objectHas(value, '_')
    then
      if std.objectHas(value._, 'macroInputs')
      then value._.macroInputs
      else []
    else std.flattenArrays([extractMacroInputs(kv.value) for kv in std.objectKeysValues(value)])
  else
    if std.type(value) == 'array'
    then std.flattenArrays([extractMacroInputs(elem) for elem in value])
    else [];

local suffix(value, sfx) =
  if std.type(value) == 'object'
  then
    if std.objectHas(value, '_')
    then value {
      _+: {
        key: '%s%s' % [value._.key, sfx],
        rawValue: suffix(value._.rawValue, sfx),
      },
    }
    else { [kv.key]: suffix(kv.value, sfx) for kv in std.objectKeysValues(value) }
  else
    if std.type(value) == 'array'
    then [suffix(elem, sfx) for elem in value]
    else value;

local tool(t, refSource, key, value={}) = {
  _: {
    local _ = self,
    rawValue:: value,

    key: '%s%s' % [t, key],
    refSource: refSource,
    ref(target='Input'):: named(target) {
      SourceOp: _.key,
      Source: _.refSource,
    },
    value: named(t) + (
      if std.objectHas(_.rawValue, 'Inputs') then {
        Inputs: {
          [kv.key]: extractRefs(kv.value)
          for kv in std.objectKeysValues(std.get(_.rawValue, 'Inputs', {}))
        },
      } else {}
    ) + (
      if std.objectHas(_.rawValue, 'KeyFrames') then { KeyFrames: _.rawValue.KeyFrames } else {}
    ),
    tools: { [_.key]: _.value } + extractTools(_.rawValue),
    macroInputs: [
      named('InstanceInput') {
        SourceOp: _.key,
        Source: kv.key,
      }
      for kv in std.objectKeysValues(std.get(_.rawValue, 'Inputs', {}))
      if std.type(kv.value) == 'object' && std.objectHas(kv.value, '_') && std.objectHas(kv.value._, 'macroInput')
    ] + extractMacroInputs(_.rawValue),
  },
  Suffix(sfx):: suffix(self, sfx),
};

local toolNames = {
  Output: [
    'Background',
    'BrightnessContrast',
    'Blur',
    'MacroOperator',
    'MediaIn',
    'MediaOut',
    'Merge',
    'Shadow',
    'TextPlus',
    'Transform',
  ],
  Mask: [
    'EllipseMask',
    'RectangleMask',
    'PolylineMask',
  ],
  Result: [
    'KeyStretcher',
  ],
};

local tools = mergeObjects([
  {
    [type]: function(key, value={}) tool(type, kv.key, key, value)
    for type in kv.value
  }
  for kv in std.objectKeysValues(toolNames)
]);

local groups = {
  Group(key, value={}): {
    _: {
      local _ = self,
      rawValue:: value,

      key: '%s%s' % ['Group', key],
      ref(target='Input'):: _.rawValue.Outputs.Output1._.ref(target),
      value: named('GroupOperator') + {
        Inputs: $.ordered() + {
          [kv.key]: extractRefs(kv.value {
            _+: {
              refSource: 'Input',
            },
          }, 'InstanceInput')
          for kv in std.objectKeysValues(std.get(_.rawValue, 'Inputs', {}))
        },
        Outputs: {
          [kv.key]: extractRefs(kv.value, 'InstanceOutput')
          for kv in std.objectKeysValues(std.get(_.rawValue, 'Outputs', {}))
        },
        Tools: $.ordered() + extractTools(_.rawValue),
      },
      tools: { [_.key]: _.value },
      macroInputs: extractMacroInputs(_.rawValue),
    },
    Suffix(sfx):: suffix(self, sfx),
  },
};

local macros = {
  MacroInput(value): {
    _: {
      ref(target='Input'):: named(target) {
        Value: value,
      },
      macroInput: true,
    },
  },
  Macro(key, value={}): $.Tools({
    _: {
      local _ = self,
      rawValue:: value,

      key: key,
      value: named('MacroOperator') + {
        Inputs: {
          ['Input%d' % vi.i]: vi.v
          for vi in std.mapWithIndex(function(i, v) { i: i, v: v }, extractMacroInputs(_.rawValue))
        },
        Outputs: {
          MainOutput1: value._.ref('InstanceOutput'),
        },
        Tools: $.ordered() + extractTools(_.rawValue),
      },
      tools: { [_.key]: _.value },
    },
  }),
};

local animations = {
  BezierSpline(key, keyFrames): tool('BezierSpline', 'Value', key, {
    KeyFrames: {
      [kv.key]: {
        '1': kv.value,
      }
      for kv in std.objectKeysValues(keyFrames)
    },
  }),
  PolyPath(key, value): tool('PolyPath', 'Position', key, value),
  Path(key, keyFrames):
    local sortedKeyValues = std.sort(std.objectKeysValues(keyFrames), function(kv) std.parseInt(kv.key));
    local points = [kv.value for kv in sortedKeyValues];
    local distance(a, b) = std.sqrt(std.pow(b.X - a.X, 2) + std.pow(b.Y - a.Y, 2));
    local length = std.foldl(
      function(acc, curr) {
        total: acc.total + distance(acc.prev, curr),
        prev: curr,
      },
      points,
      { total: 0, prev: points[0] }
    ).total;
    local displacements = std.foldl(
      function(acc, curr) {
        total: acc.total + distance(acc.prev, curr),
        displacements: acc.displacements + [if length > 0 then self.total / length else 0],
        prev: curr,
      },
      points,
      { total: 0, displacements: [], prev: points[0] }
    ).displacements;
    $.PolyPath(key, {
      Inputs: {
        PolyLine: $.Polyline({
          Points: points,
        }),
        Displacement: $.BezierSpline(key, {
          [kvi.key]: displacements[kvi.i]
          for kvi in std.mapWithIndex(function(i, kv) { i: i } + kv, sortedKeyValues)
        }),
      },
    }),
  PolylineBezierSpline(key, keyFrames):
    local sortedKeyValues = std.sort(std.objectKeysValues(keyFrames), function(kv) std.parseInt(kv.key));
    $.BezierSpline(key, {
      [kvi.key]: {
        '1': kvi.i,
        Value: kvi.value._.value,
      }
      for kvi in std.mapWithIndex(function(i, kv) { i: i } + kv, sortedKeyValues)
    }),
};

local inputs = {
  Expression(expression): {
    _: {
      ref(target='Input'):: named(target) {
        Expression: expression,
      },
    },
  },
  Number(value): {
    _: {
      ref(target='Input'):: named(target) {
        Value: named('Number') {
          Value: value,
        },
      },
    },
  },
  Inputs: {
    KeyFrames(key, keyFrames):
      local sortedKeyValues = std.sort(std.objectKeysValues(keyFrames), function(kv) std.parseInt(kv.key));
      if std.length(sortedKeyValues) == 0 then {} else
        local prototypeKeyFrame = sortedKeyValues[0].value;
        {
          [inputKv.key]:
            if std.type(prototypeKeyFrame[inputKv.key]) == 'object'
            then
              if std.get(prototypeKeyFrame[inputKv.key], '__name__', '') == 'Polyline' then
                $.Input.Polyline('%s%s' % [inputKv.key, key], {
                  [frameKv.key]: frameKv.value[inputKv.key]
                  for frameKv in sortedKeyValues
                })
              else
                $.Input.Path('%s%s' % [inputKv.key, key], {
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
  Suffix(value, sfx): suffix(value, sfx),
  ChainMerge(key, tools, value={ Inputs: {} }): std.foldl(
    function(acc, curr)
      if acc == null then curr.value else $.Merge('%s%d' % [key, curr.index], {
        Inputs: {
          Background: acc,
          Foreground: curr.value,
        } + value.Inputs,
      }),
    std.mapWithIndex(function(index, value) { index: index, value: value }, tools),
    null
  ),
  Effect(processor):
    $.Tools([
      $.MediaOut('1', {
        Inputs: {
          Input: processor($.MediaIn('1')),
        },
      }),
    ]),
  Generator(generator):
    $.Tools([
      $.MediaOut('1', {
        Inputs: {
          Input: generator,
        },
      }),
    ]),
};

functions + types + tools + groups + macros + animations + inputs + main
