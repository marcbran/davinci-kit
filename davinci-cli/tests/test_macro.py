import pytest
from src.macro import parse, manifest

# Shared test cases for both parse and manifest functions
# Format: (lua_str, python_obj, manifest_str)
# manifest_str is optional - if None, lua_str is used for manifest verification
TEST_CASES = [
    # Basic test cases
    ("nil", None, None),  # nil
    # ("simple", "simple", None),  # Simple string
    # ("", "", None),  # Empty string
    ("true", True, None),  # True boolean
    ("false", False, None),  # False boolean
    ("42", 42, None),  # Positive integer
    ("-42", -42, None),  # Negative integer
    ("0", 0, None),  # Zero
    
    # Primitive value test cases
    ("{ number = 42 }", {"number": 42}, None),  # Positive integer
    ("{ negative = -42 }", {"negative": -42}, None),  # Negative integer
    ("{ zero = 0 }", {"zero": 0}, None),  # Zero
    ("{ true_val = true }", {"true_val": True}, None),  # True boolean
    ("{ false_val = false }", {"false_val": False}, None),  # False boolean
    ("{ nil_val = nil }", {"nil_val": None}, None),  # Nil/None
    ("{ empty_str = '' }", {"empty_str": ""}, None),  # Empty string
    ("{ single_quote = 'hello' }", {"single_quote": "hello"}, None),  # Single quoted string
    (
        "{ double_quote = \"world\" }",
        {"double_quote": "world"},
        "{ double_quote = 'world' }",
    ),
    (
        "{ escaped = 'hello \\'world\\'' }",
        {"escaped": "hello 'world'"},
        "{ escaped = \"hello 'world'\" }",
    ),  # Escaped quotes
    
    # Simple table test cases
    ("{ x = 1 }", {"x": 1}, None),  # Simple key-value
    ("{ x = 1, y = 2 }", {"x": 1, "y": 2}, None),  # Multiple key-values
    ("{ nested = { x = 1 } }", {"nested": {"x": 1}}, None),  # Nested table
    ("{ array = { 1, 2, 3 } }", {"array": [1, 2, 3]}, None),  # Array/table
    ("{ 'quoted string' = 42 }", {"quoted string": 42}, None),  # Quoted strings
    ("{ x = true, y = false }", {"x": True, "y": False}, None),  # Booleans
    ("{ x = nil }", {"x": None}, None),  # Nil/None values
    
    # Complex nested structures
    (
        "{ deeply = { nested = { table = { value = 42 } } } }",
        {"deeply": {"nested": {"table": {"value": 42}}}},
        None
    ),
    
    # Integer keys
    (
        "{ [1] = 'one', [2] = 'two', [3] = 'three' }",
        {"1": "one", "2": "two", "3": "three"},
        None
    ),
    
    # Mixed type arrays
    (
        "{ mixed = { 1, 'two', true, { x = 1 }, nil, { 1, 2 } } }",
        {"mixed": [1, "two", True, {"x": 1}, None, [1, 2]]},
        None
    ),
    
    # Complex string handling
    (
        "{ 'key with \"quotes\"' = 'value with \\'quotes\\'' }",
        {"key with \"quotes\"": "value with 'quotes'"},
        "{ 'key with \"quotes\"' = \"value with 'quotes'\" }"
    ),
    
    # Multiple nested arrays
    (
        "{ matrix = { { 1, 2 }, { 3, 4 }, { 5, 6 } } }",
        {"matrix": [[1, 2], [3, 4], [5, 6]]},
        None
    ),
    
    # Mixed nesting with arrays and tables
    (
        "{ data = { points = { { x = 1, y = 2 }, { x = 3, y = 4 } }, valid = true } }",
        {"data": {"points": [{"x": 1, "y": 2}, {"x": 3, "y": 4}], "valid": True}},
        None
    ),
    
    # Complex key types and spacing
    (
        "{ ['key.with.dots'] = 42, 'key-with-dashes' = 43, 'key with spaces' = 44 }",
        {"key.with.dots": 42, "key-with-dashes": 43, "key with spaces": 44},
        None
    ),
    
    # Empty structures
    ("{}", {}, None),  # Empty table
    ("{ empty_array = {} }", {"empty_array": []}, None),  # Empty array
    ("{ empty_table = {} }", {"empty_table": {}}, None),  # Empty nested table
    
    # Array with trailing comma (should handle both cases)
    ("{ array = { 1, 2, 3, } }", {"array": [1, 2, 3]}, "{ array = { 1, 2, 3 } }"),
    
    # Named table test cases
    (
        "Input { SourceOp = \"Polygon1Polyline\", Source = \"Value\" }",
        {"__name__": "Input", "SourceOp": "Polygon1Polyline", "Source": "Value"},
        "Input { SourceOp = 'Polygon1Polyline', Source = 'Value' }"
    ),
    
    # Named table with nested structure
    (
        "Transform { Position = { X = 1, Y = 2, Z = 3 }, Rotation = { X = 0, Y = 90, Z = 0 } }",
        {"__name__": "Transform", "Position": {"X": 1, "Y": 2, "Z": 3}, "Rotation": {"X": 0, "Y": 90, "Z": 0}},
        None
    ),
    
    # Named table with array
    (
        "Array { values = { 1, 2, 3, 4, 5 } }",
        {"__name__": "Array", "values": [1, 2, 3, 4, 5]},
        None
    ),
    
    # Named table with mixed types
    (
        "Mixed { string = \"hello\", number = 42, boolean = true, nil = nil, array = { 1, 2, 3 } }",
        {"__name__": "Mixed", "string": "hello", "number": 42, "boolean": True, "nil": None, "array": [1, 2, 3]},
        "Mixed { string = 'hello', number = 42, boolean = true, nil = nil, array = { 1, 2, 3 } }"
    ),
    
    # Named table with empty content
    (
        "Empty {}",
        {"__name__": "Empty"},
        None
    ),
    
    # Named table with complex nested structure
    (
        "Complex { data = { points = { { x = 1, y = 2 }, { x = 3, y = 4 } }, valid = true } }",
        {"__name__": "Complex", "data": {"points": [{"x": 1, "y": 2}, {"x": 3, "y": 4}], "valid": True}},
        None
    ),
    
    # Named table with function-like name (empty parentheses)
    (
        "ordered() { value = 42 }",
        {"__name__": "ordered()", "value": 42},
        None
    ),
    
    # Additional test cases to ensure no hardcoded values
    
    # Different numeric values
    ("{ a = 123, b = -456, c = 0 }", {"a": 123, "b": -456, "c": 0}, None),
    
    # Different string values with various quotes
    ("{ str1 = 'hello', str2 = \"world\", str3 = 'complex \\'string\\'' }", 
     {"str1": "hello", "str2": "world", "str3": "complex 'string'"}, 
     "{ str1 = 'hello', str2 = 'world', str3 = \"complex 'string'\" }"),
    
    # Different nested table structures
    ("{ outer = { middle = { inner = { value = 999 } } } }", 
     {"outer": {"middle": {"inner": {"value": 999}}}}, None),
    
    # Different array values and structures
    ("{ arr1 = { 10, 20, 30 }, arr2 = { 'a', 'b', 'c' }, arr3 = { { 1, 2 }, { 3, 4 } } }", 
     {"arr1": [10, 20, 30], "arr2": ["a", "b", "c"], "arr3": [[1, 2], [3, 4]]}, None),
    
    # Different named tables
    ("CustomName { field1 = 100, field2 = 'test' }", 
     {"__name__": "CustomName", "field1": 100, "field2": "test"}, None),
    
    # Complex nested named tables
    ("Parent { child = Child { value = 500 }, array = { Child { x = 1 }, Child { x = 2 } } }", 
     {"__name__": "Parent", "child": {"__name__": "Child", "value": 500}, 
      "array": [{"__name__": "Child", "x": 1}, {"__name__": "Child", "x": 2}]}, None),
    
    # Tables with special characters in keys
    ("{ ['special!@#$%^&*()'] = 1, 'key with spaces' = 2, 'key-with-dashes' = 3 }", 
     {"special!@#$%^&*()": 1, "key with spaces": 2, "key-with-dashes": 3}, None),
    
    # Tables with various value types mixed
    ("{ num = 42, str = 'hello', bool = true, nil_val = nil, arr = { 1, 2 }, tbl = { x = 1 } }", 
     {"num": 42, "str": "hello", "bool": True, "nil_val": None, "arr": [1, 2], "tbl": {"x": 1}}, None),
    
    # Empty structures with different names
    ("EmptyTable {}", {"__name__": "EmptyTable"}, None),
    ("EmptyArray { values = {} }", {"__name__": "EmptyArray", "values": []}, None),
    
    # Tables with trailing commas in different positions
    ("{ a = 1, b = 2, }", {"a": 1, "b": 2}, "{ a = 1, b = 2 }"),
    ("{ arr = { 1, 2, 3, }, }", {"arr": [1, 2, 3]}, "{ arr = { 1, 2, 3 } }"),
   
    # Tables with mixed array and object values
    ("{ 1, b = 2, }", {"1": 1, "b": 2}, "{ [1] = 1, b = 2 }"),
    ("{ 2.3, b = 2, }", {"1": 2.3, "b": 2}, "{ [1] = 2.3, b = 2 }"),
    ("{ a = 1, 2, }", {"a": 1, "1": 2}, "{ a = 1, [1] = 2 }"),
     
    # Tables coming from DaVinci Resolve
    (
        "OperatorInfo { Pos = { -605, -49.5 } }",
        {
            "__name__": "OperatorInfo",
            "Pos": [-605, -49.5]
        },
        None
    ),
    (
        "{['Gamut.SLogVersion'] = Input { Value = FuID { 'SLog2' }}}",
        {
            "Gamut.SLogVersion": {
                "__name__": "Input",
                "Value": {"__name__": "FuID", "0": "SLog2"}
            }
        },
        "{ ['Gamut.SLogVersion'] = Input { Value = FuID { [0] = 'SLog2' } } }"
    ),
    
    # Named array with multiple values
    (
        "MultiArray { 'first', 'second', 'third' }",
        {
            "__name__": "MultiArray",
            "0": "first",
            "1": "second",
            "2": "third"
        },
        "MultiArray { [0] = 'first', [1] = 'second', [2] = 'third' }"
    ),
]

@pytest.mark.parametrize("lua_str,python_obj,_", TEST_CASES)
def test_parse(lua_str, python_obj, _):
    """Test parsing Lua table strings into Python objects."""
    result = parse(lua_str)
    assert result == python_obj

@pytest.mark.parametrize("lua_str,python_obj,manifest_str", TEST_CASES)
def test_manifest(lua_str, python_obj, manifest_str):
    """Test converting Python objects into Lua table strings."""
    result = manifest(python_obj)
    # Use manifest_str if provided, otherwise use lua_str
    expected = manifest_str if manifest_str is not None else lua_str
    assert result == expected 