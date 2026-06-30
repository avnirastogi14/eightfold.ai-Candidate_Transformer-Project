# Runtime output config

A config is a small JSON document with this shape:

```json
{
  "fields": [
    { "path": "<output field name>", "from": "<canonical path, optional>",
      "type": "string|string[]|...", "required": true|false,
      "normalize": "E164|canonical" }
  ],
  "include_confidence": true,
  "include_provenance": true,
  "on_missing": "null" | "omit" | "error"
}
```

- `path` is the key in the OUTPUT record.
- `from` (optional) is a dotted/bracketed path into the CANONICAL record,
  e.g. `emails[0]`, `location.city`, `skills[].name` (the `[]` operator maps
  the rest of the path over every list item). Defaults to `path` if omitted.
- `normalize` re-applies a normalizer at projection time (useful if you
  want a different format than the canonical record stores).
- `on_missing` controls behavior when a required field resolves to nothing:
  `null` (default, field present with null value), `omit` (drop the key),
  or `error` (record gets flagged in the pipeline's `errors` list).

If `fields` is omitted entirely, the full default canonical schema is
returned unfiltered.
