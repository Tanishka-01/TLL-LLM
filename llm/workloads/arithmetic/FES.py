#!/usr/bin/env python3
"""
FES.py for arithmetic functions
Usage: python FES.py <llm_output_file>
"""

import sys
import re

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

FUNCTIONS = {
    'add': add,
    'subtract': subtract,
}

def parse_and_execute(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all CALL: function(args) patterns
    pattern = r'CALL:\s*(\w+)\(([^)]*)\)'
    matches = re.findall(pattern, content)
    
    for func_name, args_str in matches:
        if func_name in FUNCTIONS:
            # Parse arguments
            args = [x.strip() for x in args_str.split(',')]
            try:
                # Convert to numbers
                args = [float(x) for x in args]
                result = FUNCTIONS[func_name](*args)
                # Format output nicely
                args_display = ', '.join(str(int(x) if x.is_integer() else x) for x in args)
                print(f"{func_name}({args_display}) = {result}")
            except Exception as e:
                print(f"Error calling {func_name}: {e}")
        else:
            print(f"Unknown function: {func_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python FES.py <llm_output_file>")
        sys.exit(1)
    
    parse_and_execute(sys.argv[1])
