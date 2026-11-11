"""A small Markdown syntax tree retaining line source spans."""

from dataclasses import dataclass
import re
from typing import Callable


@dataclass(frozen=True)
class MarkdownNode:
    kind: str
    text: str
    start_line: int
    end_line: int
    children: tuple['MarkdownNode', ...] = ()
    parent: 'MarkdownNode | None' = None

    def transform(self, visit: Callable[['MarkdownNode'], 'MarkdownNode | None']) -> 'MarkdownNode':
        def rebuild(node: MarkdownNode) -> MarkdownNode | None:
            children = tuple(child for item in node.children
                             if (child := rebuild(item)) is not None)
            current = MarkdownNode(node.kind, node.text, node.start_line, node.end_line, children, node.parent)
            return visit(current)
        result = rebuild(self)
        if result is None:
            raise ValueError('the root node cannot be removed')
        return result


def parse(source: str) -> MarkdownNode:
    """Parse headings, paragraphs, lists, and fenced code blocks."""
    if not isinstance(source, str):
        raise TypeError('Markdown input must be a string')
    lines = source.splitlines()
    children: list[MarkdownNode] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        number = index + 1
        if not line.strip():
            index += 1
            continue
        fence = re.match(r'^\s*(```+|~~~+)\s*(.*)$', line)
        if fence:
            marker, info = fence.groups()
            end = index + 1
            while end < len(lines) and not lines[end].lstrip().startswith(marker):
                end += 1
            body = '\n'.join(lines[index + 1:end])
            children.append(MarkdownNode('code_block', body, number, min(end + 1, len(lines))))
            index = min(end + 1, len(lines))
            continue
        heading = re.match(r'^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$', line)
        if heading:
            children.append(MarkdownNode(f'heading{len(heading.group(1))}', heading.group(2), number, number))
            index += 1
            continue
        if re.match(r'^\s*[-*+]\s+', line):
            items: list[MarkdownNode] = []
            start = index
            while index < len(lines):
                match = re.match(r'^\s*[-*+]\s+(.*)$', lines[index])
                if not match:
                    break
                items.append(MarkdownNode('list_item', match.group(1), index + 1, index + 1))
                index += 1
            children.append(MarkdownNode('list', '', start + 1, index, tuple(items)))
            continue
        start = index
        paragraph = [line.strip()]
        index += 1
        while index < len(lines) and lines[index].strip() and not re.match(r'^\s{0,3}#{1,6}\s+', lines[index]):
            paragraph.append(lines[index].strip())
            index += 1
        children.append(MarkdownNode('paragraph', '\n'.join(paragraph), start + 1, index))
    root = MarkdownNode('document', source, 1, max(1, len(lines)), tuple(children))
    return _with_parents(root)


def _with_parents(node: MarkdownNode, parent: MarkdownNode | None = None) -> MarkdownNode:
    children = tuple(_with_parents(child, node) for child in node.children)
    return MarkdownNode(node.kind, node.text, node.start_line, node.end_line, children, parent)


__all__ = ['MarkdownNode', 'parse']
