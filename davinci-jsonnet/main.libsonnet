local namedTable(name) = {
  __name__: name,
};

local names = [
  'AudioDisplay',
  'Background',
  'BezierSpline',
  'FuID',
  'Input',
  'OperatorInfo',
  'Polyline',
];

local functions = [
  'ordered',
];

local namedTables = {
  [name]: namedTable(name)
  for name in names
};

local functionTables = {
  [name]: function() namedTable('%s()' % name)
  for name in functions
};

namedTables + functionTables
