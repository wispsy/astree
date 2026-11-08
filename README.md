# astree

Dependency-free HTML tree parsing, CSS selector querying, and structured record extraction powered by Python's `html.parser`.

Requires Python 3.14+.

## Highlights

- **Dependency-Free**: Built strictly on Python standard library primitives.
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
