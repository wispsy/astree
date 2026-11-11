import ast
import importlib.util
import unittest

from astree import ancestors, descendants, transform, walk
from astree.html import Document
from astree.json import JsonNode, parse as parse_json
from astree.markdown import parse as parse_markdown
from astree.python import parse as parse_python
from astree.javascript import parse as parse_javascript


class StructuralTests(unittest.TestCase):
    def test_html_walk_and_relationships(self):
        document = Document.from_html('<main><p>Hello <b>world</b></p></main>')
        paragraph = document.find('p')
        self.assertIsNotNone(paragraph)
        self.assertEqual([node.kind for node in walk(document)], [
            'document', 'element', 'element', 'text', 'element', 'text',
        ])
        self.assertEqual(list(ancestors(paragraph)), [document.find('main'), document])
        self.assertEqual(list(descendants(paragraph))[0].kind, 'text')

    def test_json_is_value_oriented_and_transformable(self):
        tree = parse_json('{"items": [1, 2], "ok": true}')
        self.assertIsInstance(tree, JsonNode)
        self.assertEqual(tree.children[0].key, 'items')
        changed = transform(tree, lambda node: node.value * 10
                             if isinstance(node.value, int) and not isinstance(node.value, bool)
                             else node)
        self.assertEqual(changed.value, {'items': [10, 20], 'ok': True})
        self.assertEqual(changed.children[0].parent, changed)

    def test_python_uses_standard_ast(self):
        tree = parse_python('x = 1 + 2')
        names = [node.id for node in walk(tree) if isinstance(node, ast.Name)]
        self.assertEqual(names, ['x'])
        changed = transform(tree, lambda node: ast.Constant(value=3)
                             if isinstance(node, ast.Constant) and node.value == 2 else node)
        ast.fix_missing_locations(changed)
        self.assertEqual(ast.unparse(changed), 'x = 1 + 3')

    def test_markdown_preserves_spans_and_transforms(self):
        tree = parse_markdown('# Title\n\nA paragraph')
        self.assertEqual(tree.children[0].kind, 'heading1')
        self.assertEqual((tree.children[0].start_line, tree.children[0].end_line), (1, 1))
        changed = transform(tree, lambda node: type(node)(
            node.kind, node.text.upper(), node.start_line, node.end_line,
            node.children, node.parent
        ) if node.kind == 'heading1' else node)
        self.assertEqual(changed.children[0].text, 'TITLE')

    @unittest.skipUnless(
        importlib.util.find_spec('tree_sitter') and importlib.util.find_spec('tree_sitter_javascript'),
        'JavaScript extra is not installed',
    )
    def test_javascript_uses_tree_sitter_nodes(self):
        tree = parse_javascript('const answer = 42;')
        self.assertEqual(tree.type, 'program')
        self.assertTrue(any(node.type == 'lexical_declaration' for node in walk(tree)))


if __name__ == '__main__':
    unittest.main()
