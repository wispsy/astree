"""JSON value trees with structural traversal and immutable transforms."""

from collections.abc import Iterator
import json as _json
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class JsonNode:
    """A view over one JSON value."""

    value: Any
    parent: 'JsonNode | None' = None
    key: str | int | None = None

    @property
    def kind(self) -> str:
        if isinstance(self.value, dict):
            return 'object'
        if isinstance(self.value, list):
            return 'array'
        if self.value is None:
            return 'null'
        if isinstance(self.value, bool):
            return 'boolean'
        if isinstance(self.value, (int, float)):
            return 'number'
        return 'string'

    @property
    def children(self) -> tuple['JsonNode', ...]:
        if isinstance(self.value, dict):
            return tuple(JsonNode(value, self, key) for key, value in self.value.items())
        if isinstance(self.value, list):
            return tuple(JsonNode(value, self, index) for index, value in enumerate(self.value))
        return ()

    def descendants(self) -> Iterator['JsonNode']:
        from .structural import descendants
        return descendants(self)

    def transform(self, visit: Callable[['JsonNode'], 'JsonNode | Any | None']) -> 'JsonNode':
        def rebuild(node: JsonNode) -> JsonNode | None:
            if isinstance(node.value, dict):
                values = ((child.key, rebuild(child)) for child in node.children)
                value = {key: rebuilt.value for key, rebuilt in values if rebuilt is not None}
            elif isinstance(node.value, list):
                value = [rebuilt.value for child in node.children
                         if (rebuilt := rebuild(child)) is not None]
            else:
                value = node.value
            current = JsonNode(value, node.parent, node.key)
            replacement = visit(current)
            if replacement is None:
                return None
            return replacement if isinstance(replacement, JsonNode) else JsonNode(replacement, node.parent, node.key)

        result = rebuild(self)
        if result is None:
            raise ValueError('the root node cannot be removed')
        return result


def parse(source: str) -> JsonNode:
    """Parse JSON text into a value tree."""
    if not isinstance(source, str):
        raise TypeError('JSON input must be a string')
    return JsonNode(_json.loads(source))


def dumps(node: JsonNode, **kwargs: Any) -> str:
    """Serialize a JSON value tree."""
    return _json.dumps(node.value, **kwargs)


__all__ = ['JsonNode', 'parse', 'dumps']
