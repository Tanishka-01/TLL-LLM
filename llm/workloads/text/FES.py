#!/usr/bin/env python3
"""
FES.py for text functions
Usage: python FES.py <llm_output_file>
"""

import sys
import re
from collections import Counter

def word_count(text):
    words = text.split()
    return len(words)

def char_count(text):
    return len(text)

def frequency(text):
    words = text.lower().split()
    freq = Counter(words)
    return dict(freq.most_common(10))  # Top 10 words

def find_word(text, word):
    words = text.lower().split()
    return words.count(word.lower())

def line_count(filepath):
    try:
        with open(filepath.strip(), 'r') as f:
            lines = f.readlines()
        return len(lines)
    except FileNotFoundError:
        return f"Error: File not found: {filepath}"
    except Exception as e:
        return f"Error: {e}"

FUNCTIONS = {
    'word_count': word_count,
    'char_count': char_count,
    'frequency': frequency,
    'find_word': find_word,
    'line_count': line_count,
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
            args_str = args_str.strip()
            
            try:
                if func_name in ['word_count', 'char_count', 'frequency', 'line_count']:
                    # Single string argument
                    arg = args_str.strip('"').strip("'")
                    result = FUNCTIONS[func_name](arg)
                    print(f"{func_name}(\"{arg[:30]}...\") = {result}")
                
                elif func_name == 'find_word':
                    # Two string arguments
                    parts = args_str.split(',', 1)
                    text = parts[0].strip().strip('"').strip("'")
                    word = parts[1].strip().strip('"').strip("'")
                    result = FUNCTIONS[func_name](text, word)
                    print(f"{func_name}(\"{text[:20]}...\", \"{word}\") = {result}")
                    
            except Exception as e:
                print(f"Error calling {func_name}: {e}")
        else:
            print(f"Unknown function: {func_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python FES.py <llm_output_file>")
        sys.exit(1)
    
    parse_and_execute(sys.argv[1])
