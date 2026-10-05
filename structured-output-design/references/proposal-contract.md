# Proposal contract and admission example

This is portable JSON Schema draft 2020-12, not a promise that every provider supports oneOf. Adapt constrained generation to the provider subset while preserving full server-side validation.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "oneOf": [
    {
      "type": "object", "additionalProperties": false,
      "properties": {
        "version": {"const": "1"}, "kind": {"const": "propose"},
        "item_id": {"type": "string", "minLength": 1, "maxLength": 80},
        "quantity_delta": {"type": "integer", "minimum": -1000, "maximum": 1000},
        "evidence_ids": {"type": "array", "minItems": 1, "maxItems": 8, "uniqueItems": true,
                         "items": {"type": "string", "minLength": 1, "maxLength": 80}}
      },
      "required": ["version", "kind", "item_id", "quantity_delta", "evidence_ids"]
    },
    {
      "type": "object", "additionalProperties": false,
      "properties": {"version": {"const": "1"}, "kind": {"const": "no_action"},
                     "reason": {"type": "string", "minLength": 1, "maxLength": 240}},
      "required": ["version", "kind", "reason"]
    },
    {
      "type": "object", "additionalProperties": false,
      "properties": {"version": {"const": "1"}, "kind": {"const": "insufficient_evidence"},
                     "missing": {"type": "array", "minItems": 1, "maxItems": 8,
                                 "items": {"type": "string", "minLength": 1, "maxLength": 120}}},
      "required": ["version", "kind", "missing"]
    }
  ]
}
```

Separate failures: provider refusal/transport/truncation → bounded parser → full schema → semantic validator → policy → approval if required → atomic executor. Only proposed actions reach admission. No-action and insufficient-evidence variants do not mutate inventory.

An item_id can fit the schema while being fabricated, inaccessible or stale. Verify source provenance, tenant ownership, evidence IDs, units and current stock. Compute stock + delta in trusted code and reject impossible state. Derive principal and permissions from authenticated context. A model-produced approved field is absent from the contract and never an approval grant.

Choose explicit duplicate-key rejection and non-finite-number policy before parsing. Preserve raw output by restricted reference, then canonicalize only fully validated data with a documented implementation suitable for the supported language/domain. Do not assume arbitrary JSON serializers yield equivalent hashes.

Repair recoverable formatting or construct a supported semantic alternative with a small stated attempt budget and unchanged constraints. Missing evidence is a semantic gap, not a syntax error to fill with invented IDs. Version adapters must preserve rejection and privilege semantics; test old, new, unknown and mixed variants.
