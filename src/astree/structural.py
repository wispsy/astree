"""Shared structural traversal helpers for tree-shaped objects."""

from collections.abc import Callable, Iterator
from typing import Any, Protocol, TypeVar

T = TypeVar('T')


class Structural(Protocol):
    """Minimal protocol implemented by structural tree nodes."""

    @property
    def children(self) -> tuple[Any, ...]:
        ...


def _children(node: Any) -> tuple[Any, ...]:
    if hasattr(node, 'children'):
        children = node.children
        return tuple(children() if callable(children) else children)
    if hasattr(node, 'child_nodes'):
        return tuple(node.child_nodes)
    try:
        import ast
        if isinstance(node, ast.AST):
            return tuple(ast.iter_child_nodes(node))
    except ImportError:
        pass
    if hasattr(node, 'children'):
        return tuple(node.children)
    return ()


def walk(node: T, *, include_root: bool = True) -> Iterator[T]:
    """Yield a tree in depth-first preorder."""
    pending = [node] if include_root else list(reversed(_children(node)))
    while pending:
        current = pending.pop()
        yield current
        pending.extend(reversed(_children(current)))


def descendants(node: T) -> Iterator[T]:
    """Yield all descendants in depth-first preorder."""
    return walk(node, include_root=False)


def ancestors(node: T, *, include_self: bool = False) -> Iterator[T]:
    """Yield parent nodes from nearest to farthest."""
    current = node if include_self else getattr(node, 'parent', None)
    while current is not None:
        yield current
        current = getattr(current, 'parent', None)


def transform(node: T, visit: Callable[[T], T | None]) -> T:
    """Apply a post-order transformation to a supported tree.

    Python ASTs use ``ast.NodeTransformer`` semantics. Other adapters can
    expose a ``transform`` method for their immutable value model.
    """
    try:
        import ast
        if isinstance(node, ast.AST):
            class Transformer(ast.NodeTransformer):
                def visit(self, current: ast.AST) -> ast.AST | None:
                    transformed = super().visit(current)
                    if transformed is None:
                        return None
                    result = visit(transformed)
                    return result

            result = Transformer().visit(node)
            if result is None:
                raise ValueError('the root node cannot be removed')
            return result  # type: ignore[return-value]
    except ImportError:
        pass
    method = getattr(node, 'transform', None)
    if method is None:
        raise TypeError(f'{type(node).__name__} does not support transformation')
    return method(visit)
