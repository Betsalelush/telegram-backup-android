#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix indentation in main_full.py - convert tabs to spaces"""

with open('main_full.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace tabs with 4 spaces
fixed_content = content.replace('\t', '    ')

with open('main_full.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed indentation in main_full.py")
