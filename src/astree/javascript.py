"""Optional JavaScript syntax adapter backed by tree-sitter."""

from typing import Any


def parse(source: str) -> Any:
    """Parse JavaScript source with tree-sitter.

    Install ``astree[javascript]`` to enable this adapter. The returned
    tree-sitter node exposes ``children``, ``parent``, ``type``, and source
    span properties.
    """
    if not isinstance(source, str):
        raise TypeError('JavaScript input must be a string')
    try:
        from tree_sitter import Language, Parser
        import tree_sitter_javascript
    except ImportError as exc:
        raise ImportError(
            'JavaScript parsing requires the optional astree[javascript] extra'
        ) from exc
    language = Language(tree_sitter_javascript.language())
    parser = Parser(language)
    return parser.parse(source.encode()).root_node


__all__ = ['parse']
