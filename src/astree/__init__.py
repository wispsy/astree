"""Structural traversal and specialized syntax-tree adapters."""

from .collectors import Link, LinkCollector, TextCollector
from .extract import ExtractionError, Field, extract, extract_all
from .nodes import Node
from .parser import Document, DocumentParser, ParseLimitError
from .selectors import SelectorSyntaxError
from .structural import Structural, ancestors, descendants, transform, walk

__version__ = '0.1.0'

__all__ = [
    'Document',
    'DocumentParser',
    'Node',
    'ParseLimitError',
    'SelectorSyntaxError',
    'Link',
    'LinkCollector',
    'TextCollector',
    'Field',
    'ExtractionError',
    'extract',
    'extract_all',
    'walk',
    'ancestors',
    'descendants',
    'transform',
    'Structural',
    '__version__',
]
