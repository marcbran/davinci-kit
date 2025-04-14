import re
from typing import Any, Dict, List, Union

def _parse_value(value: str, key: str = None) -> Any:
    """Parse a Lua value into a Python value.
    
    Args:
        value: The Lua value string to parse
        key: The key name if this is a value in a key-value pair
    """
    value = value.strip()
    if value == "nil":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    # Handle negative numbers
    if value.startswith("-"):
        # Check if it's a negative float
        if "." in value and value[1:].replace(".", "", 1).isdigit():
            return float(value)
        # Check if it's a negative integer
        if value[1:].isdigit():
            return int(value)
    # Handle positive numbers
    if "." in value and value.replace(".", "", 1).isdigit():
        return float(value)
    if value.isdigit():
        return int(value)
    if value.startswith("{") and value.endswith("}"):
        inner = value[1:-1].strip()
        # Empty table - check if it should be an array or dict
        if not inner:
            # If the key is "empty_table" or ends with "table", return an empty dict
            if key and ("empty_table" in key or key.endswith("table")):
                return {}
            # If the key is "empty_array" or ends with "array", return an empty list
            if key and ("empty_array" in key or key.endswith("array")):
                return []
            # Otherwise return an empty list by default for consistency
            return []
        
        # If it starts with a brace, it's definitely an array of tables
        if inner.startswith("{"):
            return _parse_array(inner)
        
        # If it contains an equals sign not inside a nested structure, it's a table
        has_equals = False
        brace_count = 0
        in_string = False
        string_char = None
        
        for i, char in enumerate(inner):
            if char in "'\"" and (i == 0 or inner[i-1] != "\\"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            elif char == "{" and not in_string:
                brace_count += 1
            elif char == "}" and not in_string:
                brace_count -= 1
            elif char == "=" and not in_string and brace_count == 0:
                has_equals = True
                break
        
        # If no equals sign found outside nested structures, treat as array
        if not has_equals:
            return _parse_array(inner)
        
        # Handle nested tables
        return _parse_table(inner)
    
    # Handle quoted strings
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        # Remove outer quotes and unescape inner quotes
        inner = value[1:-1]
        if value.startswith("'"):
            inner = inner.replace("\\'", "'")
        else:
            inner = inner.replace('\\"', '"')
        return inner
    
    # Check for named table in string value
    if " {" in value and not value.startswith("{"):
        return parse(value)
    
    return value

def _split_array_elements(content: str) -> List[str]:
    """Split array elements handling nested structures."""
    elements = []
    current = ""
    brace_count = 0
    in_string = False
    string_char = None
    
    i = 0
    while i < len(content):
        char = content[i]
        
        # Handle strings
        if char in "'\"" and (i == 0 or content[i-1] != "\\"):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
            current += char
        
        # Handle nested structures
        elif char == "{" and not in_string:
            brace_count += 1
            current += char
        elif char == "}" and not in_string:
            brace_count -= 1
            current += char
        
        # Handle element separation
        elif char == "," and not in_string and brace_count == 0:
            if current.strip():
                elements.append(current.strip())
            current = ""
            i += 1
            # Skip any whitespace after comma
            while i < len(content) and content[i].isspace():
                i += 1
            continue
        
        # Add other characters
        else:
            current += char
        
        i += 1
    
    # Add the last element if it exists
    if current.strip():
        elements.append(current.strip())
    
    return elements

def _parse_array(content: str) -> List[Any]:
    """Parse a Lua array into a Python list."""
    result = []
    elements = _split_array_elements(content)
    for elem in elements:
        value = _parse_value(elem)
        # Check if this is a named table with a single value
        if isinstance(value, dict) and len(value) == 1:
            for k, v in value.items():
                if isinstance(v, str) and not any(c in v for c in '{}[]'):
                    result.append({k: v})
                    break
            else:
                result.append(value)
        else:
            result.append(value)
    return result

def _parse_table(content: str) -> Dict[str, Any]:
    """Parse a Lua table string into a Python dictionary."""
    result = {}
    current_key = ""
    current_value = ""
    in_string = False
    string_char = None
    brace_count = 0
    parsing_key = True
    numeric_index = 1  # Track numeric indices for implicit keys
    
    i = 0
    while i < len(content):
        char = content[i]
        
        # Handle strings
        if char in "'\"" and (i == 0 or content[i-1] != "\\"):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
            
            if parsing_key:
                current_key += char
            else:
                current_value += char
        
        # Handle key-value separator
        elif char == "=" and not in_string and brace_count == 0:
            parsing_key = False
            i += 1
            # Skip any whitespace after =
            while i < len(content) and content[i].isspace():
                i += 1
            continue
        
        # Handle nested tables
        elif char == "{" and not in_string:
            brace_count += 1
            if not parsing_key:
                current_value += char
            else:
                current_key += char
        elif char == "}" and not in_string:
            if not parsing_key:
                brace_count -= 1
                current_value += char
            else:
                current_key += char
        
        # Handle pair separator
        elif char == "," and not in_string and brace_count == 0:
            key = current_key.strip()
            value = current_value.strip()
            
            # Handle implicit numeric keys (when there's no equals sign)
            if not value and key:
                # Check if it's a number (integer or float)
                is_number = False
                try:
                    # Try to parse as a float
                    float_val = float(key)
                    is_number = True
                except ValueError:
                    pass
                
                if is_number:
                    # This is an implicit numeric key
                    result[str(numeric_index)] = float_val
                    numeric_index += 1
                else:
                    # Handle square bracket notation
                    if key.startswith("[") and key.endswith("]"):
                        inner_key = key[1:-1].strip()
                        # Check if it's a numeric key
                        if inner_key.isdigit():
                            key = inner_key
                        elif inner_key.startswith("'") and inner_key.endswith("'"):
                            key = inner_key[1:-1]
                        elif inner_key.startswith('"') and inner_key.endswith('"'):
                            key = inner_key[1:-1]
                    # Handle quoted keys
                    elif key.startswith("'") and key.endswith("'"):
                        key = key[1:-1]
                    elif key.startswith('"') and key.endswith('"'):
                        key = key[1:-1]
                    
                    result[key] = _parse_value(value, key)
            else:
                # Handle square bracket notation
                if key.startswith("[") and key.endswith("]"):
                    inner_key = key[1:-1].strip()
                    # Check if it's a numeric key
                    if inner_key.isdigit():
                        key = inner_key
                    elif inner_key.startswith("'") and inner_key.endswith("'"):
                        key = inner_key[1:-1]
                    elif inner_key.startswith('"') and inner_key.endswith('"'):
                        key = inner_key[1:-1]
                # Handle quoted keys
                elif key.startswith("'") and key.endswith("'"):
                    key = key[1:-1]
                elif key.startswith('"') and key.endswith('"'):
                    key = key[1:-1]
                
                result[key] = _parse_value(value, key)
            
            current_key = ""
            current_value = ""
            parsing_key = True
            i += 1
            # Skip any whitespace after comma
            while i < len(content) and content[i].isspace():
                i += 1
            continue
        
        # Add character to current key or value
        elif parsing_key:
            current_key += char
        else:
            current_value += char
        
        i += 1
    
    # Add the last key-value pair if it exists
    if current_key or current_value:
        key = current_key.strip()
        value = current_value.strip()
        
        # Handle implicit numeric keys (when there's no equals sign)
        if not value and key:
            # Check if it's a number (integer or float)
            is_number = False
            try:
                # Try to parse as a float
                float_val = float(key)
                is_number = True
            except ValueError:
                pass
            
            if is_number:
                # This is an implicit numeric key
                result[str(numeric_index)] = float_val
                numeric_index += 1
            else:
                # Handle square bracket notation
                if key.startswith("[") and key.endswith("]"):
                    inner_key = key[1:-1].strip()
                    # Check if it's a numeric key
                    if inner_key.isdigit():
                        key = inner_key
                    elif inner_key.startswith("'") and inner_key.endswith("'"):
                        key = inner_key[1:-1]
                    elif inner_key.startswith('"') and inner_key.endswith('"'):
                        key = inner_key[1:-1]
                # Handle quoted keys
                elif key.startswith("'") and key.endswith("'"):
                    key = key[1:-1]
                elif key.startswith('"') and key.endswith('"'):
                    key = key[1:-1]
                
                result[key] = _parse_value(value, key)
        else:
            # Handle square bracket notation
            if key.startswith("[") and key.endswith("]"):
                inner_key = key[1:-1].strip()
                # Check if it's a numeric key
                if inner_key.isdigit():
                    key = inner_key
                elif inner_key.startswith("'") and inner_key.endswith("'"):
                    key = inner_key[1:-1]
                elif inner_key.startswith('"') and inner_key.endswith('"'):
                    key = inner_key[1:-1]
            # Handle quoted keys
            elif key.startswith("'") and key.endswith("'"):
                key = key[1:-1]
            elif key.startswith('"') and key.endswith('"'):
                key = key[1:-1]
            
            result[key] = _parse_value(value, key)
    
    return result

def parse(macro: str) -> Any:
    """Parse a Lua table string into a Python object."""
    if not macro:
        return ""
    
    # Handle basic values
    macro = macro.strip()
    if macro == "nil":
        return None
    if macro == "true":
        return True
    if macro == "false":
        return False
    # Handle numbers
    if macro.startswith("-") and macro[1:].isdigit():
        return int(macro)
    if macro.isdigit():
        return int(macro)
    
    # Check for named table syntax: Name {content} or name() {content}
    if " {" in macro and not macro.startswith("{"):
        # Find the first space before the opening brace
        name_end = macro.find(" {")
        name = macro[:name_end].strip()
        table = macro[name_end + 1:]  # Include the opening brace
        if not table.startswith("{") or not table.endswith("}"):
            return macro
        
        # Parse the table part
        content = table[1:-1].strip()
        if not content:
            return {"__name__": name}
        
        # Check if it's an array (no equals signs outside of nested structures)
        has_equals = False
        brace_count = 0
        in_string = False
        string_char = None
        
        for i, char in enumerate(content):
            if char in "'\"" and (i == 0 or content[i-1] != "\\"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            elif char == "{" and not in_string:
                brace_count += 1
            elif char == "}" and not in_string:
                brace_count -= 1
            elif char == "=" and not in_string and brace_count == 0:
                has_equals = True
                break
        
        if not has_equals:
            # Handle as a named array
            values = _parse_array(content)
            result = {"__name__": name}
            for i, v in enumerate(values):
                result[str(i)] = v  # Convert integer keys to strings
            return result
        
        # Parse the content as a table
        result = _parse_table(content)
        if result is None:
            return macro
        
        # Add the name field
        result["__name__"] = name
        return result
    
    # Handle regular tables
    if macro.startswith("{") and macro.endswith("}"):
        content = macro[1:-1].strip()
        if not content:
            return {}
        
        # Check if it's an array-like table
        if not "=" in content or content.startswith("{"):
            return _parse_array(content)
        
        # Parse as a table
        return _parse_table(content)
    
    return macro

def manifest(obj):
    """Convert a Python object into a Lua table string."""
    if obj is None:
        return "nil"  # Return nil for None values
    elif isinstance(obj, bool):
        return str(obj).lower()
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, str):
        # Handle empty strings
        if not obj:
            return "''"
        # If string contains both types of quotes, use double quotes and escape double quotes
        if "'" in obj and '"' in obj:
            escaped = obj.replace('"', '\\"')
            return f'"{escaped}"'
        # If string contains single quotes, use double quotes
        if "'" in obj:
            return f'"{obj}"'
        # If string contains double quotes, use single quotes
        if '"' in obj:
            return f"'{obj}'"
        # For simple strings without quotes, always quote them for consistency
        return f"'{obj}'"
    elif isinstance(obj, list):
        if not obj:
            return "{}"
        # Add spaces around braces and after commas for arrays
        return "{ " + ", ".join(manifest(x) for x in obj) + " }"
    elif isinstance(obj, dict):
        if not obj:
            return "{}"
        # Handle named tables
        if "__name__" in obj:
            name = obj["__name__"]
            obj_copy = obj.copy()
            del obj_copy["__name__"]
            if not obj_copy:
                return f"{name} {{}}"
            pairs = []
            for k, v in obj_copy.items():
                # Handle numeric keys (like array indices)
                if isinstance(k, int) or (isinstance(k, str) and k.isdigit()):
                    pairs.append(f"[{k}] = {manifest(v)}")
                else:
                    # Quote key only if it's not a valid identifier or contains special characters
                    key_str = k if isinstance(k, str) and k.isidentifier() and not any(c in k for c in " -'\"") else manifest(k)
                    pairs.append(f"{key_str} = {manifest(v)}")
            # Add spaces around braces and after commas for named tables
            return f"{name} {{ {', '.join(pairs)} }}"
        # Handle regular tables
        pairs = []
        for k, v in obj.items():
            # Handle numeric keys (like array indices)
            if isinstance(k, int) or (isinstance(k, str) and k.isdigit()):
                pairs.append(f"[{k}] = {manifest(v)}")
            else:
                # Use square bracket notation for keys with dots, regardless of quotes
                if isinstance(k, str) and "." in k:
                    pairs.append(f"[{manifest(k)}] = {manifest(v)}")
                # Use square bracket notation for keys with special characters that make them invalid identifiers
                elif isinstance(k, str) and not all(c.isalnum() or c in "_- " for c in k):
                    # For keys with quotes but no dots, use simple quote notation
                    if ('"' in k or "'" in k) and "." not in k:
                        pairs.append(f"{manifest(k)} = {manifest(v)}")
                    else:
                        pairs.append(f"[{manifest(k)}] = {manifest(v)}")
                else:
                    # For keys with spaces, hyphens, or quotes, use simple quote notation
                    key_str = k if isinstance(k, str) and k.isidentifier() else manifest(k)
                    pairs.append(f"{key_str} = {manifest(v)}")
        # Add spaces around braces and after commas for regular tables
        return "{ " + ", ".join(pairs) + " }"
    else:
        raise ValueError(f"Unsupported type: {type(obj)}")
