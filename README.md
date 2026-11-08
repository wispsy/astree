# astree

Shared structural traversal with specialized HTML, JSON, Markdown, Python, and JavaScript adapters.

Requires Python 3.14+.

## Highlights

- **Shared Traversal**: Use `walk`, `ancestors`, `descendants`, and `transform` where the node model supports them.
- **Specialized Adapters**: Preserve DOM, value-tree, source-span, and language-AST semantics instead of forcing one node type.
- **Full DOM Navigation**: Navigable `Document` and `Node` tree with parent/child links and attributes.
- **CSS Selectors**: Fast CSS selector queries (`select`, `select_one`).
- **Streaming Collectors**: Single-pass `LinkCollector` and `TextCollector` with bounds protection.
- **Declarative Schema Extraction**: `extract` and `extract_all` using `Field` definitions with type converters and cardinality validation.
- **Configurable Limits**: Protect against deeply nested tags or resource exhaustion (`max_depth`, `max_nodes`, `max_chars`).

## Installation

```sh
pip install astree
```

For development:

```sh
git clone https://github.com/wispsy/astree.git
cd astree
uv sync
```

JavaScript support is optional:

```sh
uv sync --extra javascript
```

## Quick Start

### Basic Parsing & Queries

```python
from astree import Document

doc = Document.from_html('''
<!doctype html>
<html>
  <head><title>My Article</title></head>
  <body>
    <article class="card" data-id="42">
      <h2>Headline</h2>
      <a href="/post/42">Read story</a>
    </article>
  </body>
</html>
''')

assert doc.title == 'My Article'
card = doc.select_one('article.card')
assert card is not None
assert card.attrs['data-id'] == '42'

link = card.find('a', href=True)
assert link is not None
assert link.attrs['href'] == '/post/42'
assert card.get_text(' ', strip=True) == 'Headline Read story'
```

### Structural Adapters

```python
from astree import ancestors, transform, walk
from astree.json import parse as parse_json
from astree.python import parse as parse_python

json_tree = parse_json('{"count": 2}')
json_tree = transform(json_tree, lambda node: node.value + 1
                      if node.kind == 'number' else node)
assert json_tree.value == {'count': 3}

python_tree = parse_python('answer = 42')
assert list(walk(python_tree))
```

`astree.markdown.parse` returns a source-span tree for headings, paragraphs,
lists, and fenced code blocks. `astree.javascript.parse` returns a tree-sitter
JavaScript node and requires the optional extra.

### Structured Record Extraction

```python
from astree import Document, Field, extract_all

records = extract_all(doc, 'article.card', {
    'id': Field(attribute='data-id', convert=int),
    'headline': Field('h2'),
    'url': Field('a', attribute='href'),
})

# [{'id': 42, 'headline': 'Headline', 'url': '/post/42'}]
```

## Documentation

See [docs/api.md](docs/api.md) for full API details, selector capabilities, collectors, and structured extraction specifications.

## Running Tests

```sh
python -m unittest discover -s tests -v
```

## License

MIT
