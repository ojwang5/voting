import ast
import sys

try:
    with open('polls/views_admin.py', 'r') as f:
        code = f.read()
    ast.parse(code)
    print("No syntax errors found")
except SyntaxError as e:
    print(f"Syntax Error: {e}")
    sys.exit(1)
