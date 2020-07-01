# pylint: disable=duplicate-code
"""The project schema managed by Nestor"""

PROJECT_SCHEMA = {
    "type": "object",
    "properties": {
        "env": {},
        "domain": {},
        "env_suffix": {},
        "domain_prefix": {},
        "docker": {
            "type": "object",
            "properties": {
                "build": {
                    "type": "object",
                    "properties": {
                        "variables": {
                            "type": "object",
                            "patternProperties": {
                                "": {"type": "string", "pattern": "^([A-Z_]*)",},
                            },
                        },
                    },
                },
                "registries": {
                    "type": "object",
                    "properties": {
                        "docker.com": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string",},
                                    "organization": {"type": "string",},
                                },
                            },
                        },
                    },
                },
            },
            "required": ["build", "registries"],
            "additionalProperties": False,
        },
        "deployments": {},
        "concurrency_policy": {"type": "string",},
        "scales": {"$ref": "#/definitions/scales",},
        "resources": {"$ref": "#/definitions/resources",},
        "build": {
            "type": "object",
            "properties": {
                "variables": {
                    "type": "object",
                    "patternProperties": {"": {"type": ["boolean", "integer", "string"],},},
                },
            },
        },
        "is_enabled": {"type": "boolean",},
        "probes": {
            "type": "object",
            "properties": {"web": {"$ref": "#/definitions/probes",},},
            "additionalProperties": False,
        },
        "variables": {
            "type": "object",
            "properties": {
                "app": {"$ref": "#/definitions/variables/confSubObjects",},
                "ope": {"$ref": "#/definitions/variables/confSubObjects",},
                "secret": {"$ref": "#/definitions/variables/subObjectSecrets",},
            },
            "required": ["ope"],
            "additionalProperties": False,
        },
    },
    "required": [
        "project",
        "env",
        "domain",
        "env_suffix",
        "domain_prefix",
        "docker",
        "deployments",
        "probes",
        "variables",
        "workflow",
        "slack",
        "jira",
    ],
    "additionalProperties": True,
}
