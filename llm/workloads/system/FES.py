#!/usr/bin/env python3
"""
FES.py for system functions
Usage: python FES.py <llm_output_file>
"""

import sys
import re
import os
import socket
from datetime import datetime

def get_cpu_usage():
    try:
        load = os.getloadavg()[0]
        cpu_count = os.cpu_count()
        percent = (load / cpu_count) * 100
        return f"{percent:.1f}%"
    except:
        return "Unable to get CPU usage"

def get_memory_usage():
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        mem_total = int(lines[0].split()[1]) / 1024 / 1024
        mem_available = int(lines[2].split()[1]) / 1024 / 1024
        mem_used = mem_total - mem_available
        percent = (mem_used / mem_total) * 100
        return f"{mem_used:.1f}GB / {mem_total:.1f}GB ({percent:.0f}%)"
    except:
        return "Unable to get memory usage"

def get_disk_usage():
    try:
        stat = os.statvfs('/')
        total = (stat.f_blocks * stat.f_frsize) / (1024**3)
        free = (stat.f_bavail * stat.f_frsize) / (1024**3)
        used = total - free
        percent = (used / total) * 100
        return f"{used:.1f}GB / {total:.1f}GB ({percent:.0f}%)"
    except:
        return "Unable to get disk usage"

def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{days} days, {hours} hours, {minutes} minutes"
    except:
        return "Unable to get uptime"

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to get IP address"

def get_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def read_file(path):
    try:
        with open(path.strip(), 'r') as f:
            content = f.read(500)
        return content
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error: {e}"

def list_files(directory):
    try:
        files = os.listdir(directory.strip())
        return files[:20]  # Limit to 20 files
    except FileNotFoundError:
        return f"Error: Directory not found: {directory}"
    except Exception as e:
        return f"Error: {e}"

FUNCTIONS = {
    'get_cpu_usage': {'fn': get_cpu_usage, 'args': 'none'},
    'get_memory_usage': {'fn': get_memory_usage, 'args': 'none'},
    'get_disk_usage': {'fn': get_disk_usage, 'args': 'none'},
    'get_uptime': {'fn': get_uptime, 'args': 'none'},
    'get_ip': {'fn': get_ip, 'args': 'none'},
    'get_date': {'fn': get_date, 'args': 'none'},
    'read_file': {'fn': read_file, 'args': 'string'},
    'list_files': {'fn': list_files, 'args': 'string'},
}

def parse_and_execute(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    pattern = r'CALL:\s*(\w+)\(([^)]*)\)'
    matches = re.findall(pattern, content)
    
    for func_name, args_str in matches:
        if func_name in FUNCTIONS:
            func_info = FUNCTIONS[func_name]
            func = func_info['fn']
            args_type = func_info['args']
            
            try:
                if args_type == 'none':
                    result = func()
                    print(f"{func_name}() = {result}")
                elif args_type == 'string':
                    arg = args_str.strip().strip('"').strip("'")
                    result = func(arg)
                    print(f"{func_name}({arg}) = {result}")
            except Exception as e:
                print(f"Error calling {func_name}: {e}")
        else:
            print(f"Unknown function: {func_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python FES.py <llm_output_file>")
        sys.exit(1)
    
    parse_and_execute(sys.argv[1])
