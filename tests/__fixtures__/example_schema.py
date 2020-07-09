"""Example Schema"""

EXAMPLE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {"test": {"type": "string"}},
    "required": ["test"],
    "additionalProperties": False,
}
