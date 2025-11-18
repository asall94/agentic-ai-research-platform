"""
Quick fix script to replace aisuite with openai
"""
import os
import re

files_to_fix = [
    "app/agents/reflection_agent.py",
    "app/agents/revision_agent.py",
    "app/agents/research_agent.py",
    "app/agents/writer_agent.py",
    "app/agents/editor_agent.py",
    "app/agents/planner_agent.py",
    "app/workflows/multi_agent.py"
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace imports
        content = content.replace('from aisuite import Client', 'from openai import OpenAI')
        content = content.replace('self.client = Client()', 'self.client = OpenAI()')
        content = content.replace('Client()', 'OpenAI()')
        
        # Fix model names (remove openai: prefix)
        content = content.replace('"openai:gpt-4o"', '"gpt-4o"')
        content = content.replace('"openai:gpt-4o-mini"', '"gpt-4o-mini"')
        content = content.replace('"openai:o4-mini"', '"gpt-4o-mini"')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed: {file_path}")

print("\n🎉 All files fixed!")
