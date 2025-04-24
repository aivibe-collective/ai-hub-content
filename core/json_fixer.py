#!/usr/bin/env python3
"""
JSON fixer module for handling malformed JSON responses.
"""

import json
import re


def fix_json(json_str):
    """
    Fix common JSON formatting issues.
    
    Args:
        json_str (str): The JSON string to fix.
        
    Returns:
        dict or list: The parsed JSON object.
    """
    # Remove non-ASCII characters
    json_str = ''.join(c for c in json_str if ord(c) < 128)
    
    # Try to parse the JSON directly
    try:
        return json.loads(json_str.strip())
    except json.JSONDecodeError:
        pass
    
    # Try to fix common JSON issues
    try:
        # Fix missing commas between properties
        fixed_json = re.sub(r'"\s*(\w+)":', '",\1":', json_str)
        
        # Fix missing commas after closing quotes before a property name
        fixed_json = re.sub(r'"\s*{', '",{', fixed_json)
        fixed_json = re.sub(r'"\s*\[', '",[', fixed_json)
        
        # Fix trailing commas in arrays and objects
        fixed_json = re.sub(r',\s*(\]|\})', r'\1', fixed_json)
        
        # Try to parse the fixed JSON
        try:
            return json.loads(fixed_json.strip())
        except json.JSONDecodeError:
            pass
    except Exception:
        pass
    
    # If all else fails, try a more manual approach
    return manual_json_parse(json_str)


def manual_json_parse(json_str):
    """
    Manually parse a JSON string with common errors.
    
    Args:
        json_str (str): The JSON string to parse.
        
    Returns:
        dict or list: The parsed JSON object.
    """
    # Check if it's an array
    if json_str.strip().startswith('[') and ']' in json_str:
        # Extract the array content
        array_content = json_str.strip()[1:json_str.rfind(']')]
        
        # Split the array into items
        items = []
        current_item = ""
        brace_count = 0
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for char in array_content:
            if escape_next:
                current_item += char
                escape_next = False
                continue
                
            if char == '\\':
                current_item += char
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                current_item += char
                continue
                
            if in_string:
                current_item += char
                continue
                
            if char == '{':
                brace_count += 1
                current_item += char
                continue
                
            if char == '}':
                brace_count -= 1
                current_item += char
                if brace_count == 0 and bracket_count == 0:
                    # End of an object
                    if current_item.strip():
                        try:
                            items.append(manual_json_parse(current_item))
                            current_item = ""
                        except Exception:
                            # If we can't parse it, just add it as a string
                            current_item += char
                continue
                
            if char == '[':
                bracket_count += 1
                current_item += char
                continue
                
            if char == ']':
                bracket_count -= 1
                current_item += char
                continue
                
            if char == ',' and brace_count == 0 and bracket_count == 0:
                # End of an item
                if current_item.strip():
                    try:
                        items.append(manual_json_parse(current_item))
                    except Exception:
                        # If we can't parse it, just add it as a string
                        pass
                current_item = ""
                continue
                
            current_item += char
            
        # Add the last item
        if current_item.strip():
            try:
                items.append(manual_json_parse(current_item))
            except Exception:
                # If we can't parse it, just add it as a string
                pass
                
        return items
        
    # Check if it's an object
    elif json_str.strip().startswith('{') and '}' in json_str:
        # Extract the object content
        object_content = json_str.strip()[1:json_str.rfind('}')]
        
        # Split the object into properties
        properties = {}
        current_key = None
        current_value = ""
        brace_count = 0
        bracket_count = 0
        in_string = False
        escape_next = False
        in_key = True
        
        for char in object_content:
            if escape_next:
                if in_key:
                    current_key = (current_key or "") + char
                else:
                    current_value += char
                escape_next = False
                continue
                
            if char == '\\':
                if in_key:
                    current_key = (current_key or "") + char
                else:
                    current_value += char
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                if in_key:
                    current_key = (current_key or "") + char
                else:
                    current_value += char
                continue
                
            if in_string:
                if in_key:
                    current_key = (current_key or "") + char
                else:
                    current_value += char
                continue
                
            if char == ':' and in_key and brace_count == 0 and bracket_count == 0:
                in_key = False
                continue
                
            if char == '{':
                brace_count += 1
                current_value += char
                continue
                
            if char == '}':
                brace_count -= 1
                current_value += char
                continue
                
            if char == '[':
                bracket_count += 1
                current_value += char
                continue
                
            if char == ']':
                bracket_count -= 1
                current_value += char
                continue
                
            if char == ',' and brace_count == 0 and bracket_count == 0:
                # End of a property
                if current_key and current_key.strip():
                    # Clean up the key
                    key = current_key.strip()
                    if key.startswith('"') and key.endswith('"'):
                        key = key[1:-1]
                        
                    # Clean up the value
                    value = current_value.strip()
                    try:
                        # Try to parse the value
                        if value.startswith('{') or value.startswith('['):
                            properties[key] = manual_json_parse(value)
                        elif value.lower() == 'true':
                            properties[key] = True
                        elif value.lower() == 'false':
                            properties[key] = False
                        elif value.lower() == 'null':
                            properties[key] = None
                        elif value.startswith('"') and value.endswith('"'):
                            properties[key] = value[1:-1]
                        else:
                            try:
                                properties[key] = int(value)
                            except ValueError:
                                try:
                                    properties[key] = float(value)
                                except ValueError:
                                    properties[key] = value
                    except Exception:
                        # If we can't parse it, just add it as a string
                        properties[key] = value
                        
                current_key = None
                current_value = ""
                in_key = True
                continue
                
            if in_key:
                current_key = (current_key or "") + char
            else:
                current_value += char
                
        # Add the last property
        if current_key and current_key.strip():
            # Clean up the key
            key = current_key.strip()
            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]
                
            # Clean up the value
            value = current_value.strip()
            try:
                # Try to parse the value
                if value.startswith('{') or value.startswith('['):
                    properties[key] = manual_json_parse(value)
                elif value.lower() == 'true':
                    properties[key] = True
                elif value.lower() == 'false':
                    properties[key] = False
                elif value.lower() == 'null':
                    properties[key] = None
                elif value.startswith('"') and value.endswith('"'):
                    properties[key] = value[1:-1]
                else:
                    try:
                        properties[key] = int(value)
                    except ValueError:
                        try:
                            properties[key] = float(value)
                        except ValueError:
                            properties[key] = value
            except Exception:
                # If we can't parse it, just add it as a string
                properties[key] = value
                
        return properties
        
    # If it's a string
    elif json_str.strip().startswith('"') and json_str.strip().endswith('"'):
        return json_str.strip()[1:-1]
        
    # If it's a number
    elif json_str.strip().isdigit():
        return int(json_str.strip())
        
    # If it's a float
    elif re.match(r'^-?\d+\.\d+$', json_str.strip()):
        return float(json_str.strip())
        
    # If it's a boolean
    elif json_str.strip().lower() == 'true':
        return True
        
    elif json_str.strip().lower() == 'false':
        return False
        
    # If it's null
    elif json_str.strip().lower() == 'null':
        return None
        
    # If we can't parse it, just return the string
    return json_str.strip()


if __name__ == "__main__":
    # Test the JSON fixer
    test_json = """
    [
        {
            "id": "test1",
            "title": "Test Title 1",
            "authors": ["Author 1", "Author 2"]
            "year": 2021,
            "venue": "Test Venue",
            "url": "https://example.com/test1",
            "citation": "Author 1, Author 2 (2021). Test Title 1. Test Venue."
        }
    ]
    """
    
    result = fix_json(test_json)
    print(json.dumps(result, indent=2))
