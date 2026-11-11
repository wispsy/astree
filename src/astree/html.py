"""HTML adapter and document model."""

from .nodes import Node
from .parser import Document, DocumentParser, ParseLimitError

__all__ = ['Document', 'DocumentParser', 'Node', 'ParseLimitError']
