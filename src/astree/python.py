"""Python syntax trees backed by the standard library ``ast`` module."""

import ast

parse = ast.parse
PythonNode = ast.AST

__all__ = ['PythonNode', 'ast', 'parse']
