# astree API Reference

`astree` provides dependency-free HTML tree parsing, CSS selector queries, streaming collectors, and structured record extraction powered by Python's standard library `html.parser.HTMLParser`. Python 3.14+ is required.

---

## 1. Document & Node Model

### `Document`

Constructed via:
- `Document.from_html(html: str, **limits) -> Document`: Convenience factory parsing the full HTML string.
- Or via `DocumentParser`.

#### Methods & Properties
- `title: str | None`: Returns the text of the `<title>` tag, if present.
- `text: str`: Normalized text across all descendants (excluding script/style/comments).
- `get_text(separator: str = '', strip: bool = False) -> str`: Concatenates text nodes with a separator and optional whitespace stripping.
- `select(selector: str) -> list[Node]`: Queries descendant elements using CSS selectors in document order.
- `select_one(selector: str) -> Node | None`: Returns the first matching element, or `None`.
- `find(tag: str | None = None, attrs: Mapping[str, Any] | None = None, **kwargs) -> Node | None`: Searches for matching descendant element.
- `find_all(tag: str | None = None, attrs: Mapping[str, Any] | None = None, **kwargs) -> list[Node]`: Finds all matching descendant elements.
- `descendants() -> Iterator[Node]`: Iterates over all descendant nodes in depth-first preorder.

### `Node`

Represents a DOM node.
- `kind: Literal['root', 'element', 'text', 'comment', 'decl', 'pi']`
- `tag: str | None`: Tag name for elements (e.g. `'div'`, `'a'`).
- `attrs: Mapping[str, str]`: Read-only attributes dictionary.
- `parent: Node | None`: Parent node.
- `children: tuple[Node, ...]`: Direct child nodes.
- `data: str | None`: Text content for text/comment/decl nodes.

---

## 2. Streaming Parsers & Collectors

### `DocumentParser`

Subclasses `html.parser.HTMLParser`. Incrementally feeds HTML chunks.

```python
parser = DocumentParser(max_depth=512, max_nodes=50_000, max_chars=10_000_000)
parser.feed(chunk)
parser.close()
doc = parser.document
```

### `LinkCollector`

Streaming anchor tag extractor:
```python
collector = LinkCollector(base_url='https://example.com/', collect=True, on_link=callback)
collector.feed(chunk)
collector.close()
for link in collector.links:
    print(link.url, link.text)
```

### `TextCollector`

Streaming text extractor ignoring non-visible tags:
```python
collector = TextCollector()
collector.feed(chunk)
collector.close()
print(collector.text)
```

---

## 3. Structured Record Extraction

Extracts typed dictionaries or dataclass records from HTML elements:

```python
from astree import Document, Field, extract_all

doc = Document.from_html(html)
records = extract_all(doc, 'article.item', {
    'id': Field(attribute='data-id', convert=int),
    'title': Field('h2'),
    'link': Field('a', attribute='href'),
    'tags': Field('span.tag', many=True),
})
```

- `Field(selector=None, attribute=None, default=..., required=True, many=False, convert=None)`: Defines how a record field is extracted from a scoped element.
- `extract(node, schema, factory=dict)`: Extracts a single record from a node.
- `extract_all(node, row_selector, schema, factory=dict)`: Scopes and extracts records for all elements matching `row_selector`.
- `ExtractionError`: Raised when extraction fails due to missing required fields, cardinality mismatch, or conversion errors.
