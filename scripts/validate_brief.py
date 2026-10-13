#!/usr/bin/env python3
"""Validate a JSON file against a schema in schema/.

stdlib only (jsonschema is not assumed to be installed on a stranger's machine).
Implements just the subset of JSON Schema draft-07 the schemas in this
repo actually use: required, type, enum, pattern, minLength, minItems,
additionalProperties, one level of nested object (with enum and
minLength on its string fields).

Usage:
  python3 scripts/validate_brief.py <file.json> [--schema creative_brief|brand_foundation|agent_spec]
If --schema is omitted, auto-detects by looking for "brief_id" (creative_brief),
"brand_id" (brand_foundation) or "agent_id" (agent_spec) in the file.
Exit 0 + "VALID" on success. Exit 1 + list of errors on failure.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = {
    "creative_brief": ROOT / "schema" / "creative_brief.schema.json",
    "brand_foundation": ROOT / "schema" / "brand_foundation.schema.json",
    "agent_spec": ROOT / "schema" / "agent_spec.schema.json",
}


def validate(brief: dict, schema: dict) -> list[str]:
    errors = []
    props = schema.get("properties", {})
    required = schema.get("required", [])

    for field in required:
        if field not in brief:
            errors.append(f"missing required field: {field}")

    if schema.get("additionalProperties") is False:
        for key in brief:
            if key not in props:
                errors.append(f"unexpected field not in schema: {key}")

    for field, spec in props.items():
        if field not in brief:
            continue
        val = brief[field]
        t = spec.get("type")
        if t == "string" and not isinstance(val, str):
            errors.append(f"{field}: expected string, got {type(val).__name__}")
            continue
        if t == "array" and not isinstance(val, list):
            errors.append(f"{field}: expected array, got {type(val).__name__}")
            continue
        if t == "object" and not isinstance(val, dict):
            errors.append(f"{field}: expected object, got {type(val).__name__}")
            continue
        if t == "object":
            sub_props = spec.get("properties", {})
            sub_required = spec.get("required", [])
            for sub_field in sub_required:
                if sub_field not in val:
                    errors.append(f"{field}.{sub_field}: missing required field")
            if spec.get("additionalProperties") is False:
                for key in val:
                    if key not in sub_props:
                        errors.append(f"{field}.{key}: unexpected field not in schema")
            for sub_field, sub_spec in sub_props.items():
                if sub_field not in val:
                    continue
                sub_val = val[sub_field]
                sub_t = sub_spec.get("type")
                if sub_t == "string" and not isinstance(sub_val, str):
                    errors.append(f"{field}.{sub_field}: expected string, got {type(sub_val).__name__}")
                elif sub_t == "boolean" and not isinstance(sub_val, bool):
                    errors.append(f"{field}.{sub_field}: expected boolean, got {type(sub_val).__name__}")
                elif sub_t == "string":
                    if "enum" in sub_spec and sub_val not in sub_spec["enum"]:
                        errors.append(f"{field}.{sub_field}: '{sub_val}' not in enum {sub_spec['enum']}")
                    if "minLength" in sub_spec and len(sub_val) < sub_spec["minLength"]:
                        errors.append(f"{field}.{sub_field}: shorter than minLength {sub_spec['minLength']}")
            # Ad-copy specific rule: has_copy true requires real headline + placement text.
            if field == "ad_copy" and val.get("has_copy") is True:
                if not val.get("headline", "").strip():
                    errors.append("ad_copy.headline: required non-empty when ad_copy.has_copy is true")
                if not val.get("placement", "").strip():
                    errors.append("ad_copy.placement: required non-empty when ad_copy.has_copy is true")
            continue
        if t == "string":
            if "minLength" in spec and len(val) < spec["minLength"]:
                errors.append(f"{field}: shorter than minLength {spec['minLength']}")
            if "pattern" in spec and not re.match(spec["pattern"], val):
                errors.append(f"{field}: does not match pattern {spec['pattern']}")
            if "enum" in spec and val not in spec["enum"]:
                errors.append(f"{field}: '{val}' not in enum {spec['enum']}")
        if t == "array":
            if "minItems" in spec and len(val) < spec["minItems"]:
                errors.append(f"{field}: fewer than minItems {spec['minItems']}")
            item_type = spec.get("items", {}).get("type")
            if item_type == "string":
                for i, item in enumerate(val):
                    if not isinstance(item, str):
                        errors.append(f"{field}[{i}]: expected string")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--schema", choices=list(SCHEMAS.keys()), default=None)
    args = parser.parse_args()

    file_path: Path = args.file
    if not file_path.exists():
        print(f"ERROR: file not found: {file_path}", file=sys.stderr)
        return 2

    try:
        data = json.loads(file_path.read_text())
    except json.JSONDecodeError as e:
        print(f"INVALID: not valid JSON: {e}")
        return 1

    schema_name = args.schema
    if schema_name is None:
        if "agent_id" in data:
            schema_name = "agent_spec"
        elif "brand_id" in data:
            schema_name = "brand_foundation"
        else:
            schema_name = "creative_brief"

    schema = json.loads(SCHEMAS[schema_name].read_text())
    errors = validate(data, schema)
    if errors:
        print(f"INVALID ({schema_name}): {file_path}")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"VALID ({schema_name}): {file_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
