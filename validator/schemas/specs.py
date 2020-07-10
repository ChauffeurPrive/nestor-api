"""Schemas managed by Nestor"""

SPECS = {
    "variables": {
        "confSubObjects": {"type": "object", "patternProperties": {"": {"type": "string",},},},
        "subObjectSecrets": {
            "type": "object",
            "patternProperties": {
                "": {
                    "type": "object",
                    "properties": {"name": {"type": "string",}, "key": {"type": "string",},},
                },
            },
        },
        "projectSubObjects": {"type": "object", "patternProperties": {"": {"type": "string",},},},
    },
    "scales": {
        "type": "object",
        "patternProperties": {"": {"$ref": "#/definitions/scales/definitions/scaleSubProperty",},},
        "definitions": {
            "scaleSubProperty": {
                "type": "object",
                "properties": {
                    "maxReplicas": {"type": "integer",},
                    "minReplicas": {"type": "integer",},
                    "targetCPUUtilizationPercentage": {
                        "type": "integer",
                        "maximum": 100,
                        "minimum": 0,
                    },
                },
                "required": ["maxReplicas", "minReplicas", "targetCPUUtilizationPercentage",],
                "additionalProperties": False,
            },
        },
    },
    "crons": {
        "type": "object",
        "patternProperties": {"": {"$ref": "#/definitions/crons/definitions/cronProperty",},},
        "additionalProperties": False,
        "definitions": {
            "cronProperty": {
                "type": "object",
                "properties": {
                    "schedule": {
                        "type": "string",
                        "pattern": "([0-9]{0,2}[*/,-]{0,3}[0-9]*\\s?){5}",
                    },
                    "concurrency_policy": {"type": "string",},
                    "suspend": {"type": "boolean",},
                },
                "required": ["schedule", "concurrency_policy"],
                "additionalProperties": False,
            },
        },
    },
    "probes": {
        "type": "object",
        "patternProperties": {
            "": {
                "properties": {
                    "path": {"type": "string",},
                    "delay": {"type": "integer",},
                    "timeout": {"type": "integer",},
                },
                "required": ["path"],
            },
        },
    },
    "resources": {
        "type": "object",
        "patternProperties": {
            "": {
                "type": "object",
                "properties": {
                    "limits": {"$ref": "#/definitions/resources/definitions/resourcesSubProperty",},
                    "requests": {
                        "$ref": "#/definitions/resources/definitions/resourcesSubProperty",
                    },
                },
            },
        },
        "definitions": {
            "resourcesSubProperty": {
                "type": "object",
                "properties": {
                    "cpu": {"anyOf": [{"type": "string",}, {"type": "number", "minimum": 0,},],},
                    "memory": {"type": "string",},
                },
            },
        },
    },
}
