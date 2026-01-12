#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix all indentation in main_full.py"""

with open('main_full.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    # Replace tabs with 4 spaces
    fixed_line = line.replace('\t', '    ')
    fixed_lines.append(fixed_line)

with open('main_full.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed all tabs in main_full.py")
