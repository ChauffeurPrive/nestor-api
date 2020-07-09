# pylint: disable=duplicate-code
"""The application schema configuration managed by Nestor"""

APPLICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "app": {"type": "string", "maxLength": 58,},
        "git": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "pattern": "((ssh://)?git@[\\w\\.]+)(:(//)?)([\\w\\.@\\:/\\-~]+)(\\.git)(/)?",
                },
            },
            "required": ["origin"],
            "additionalProperties": False,
        },
        "processes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "pattern": "^([a-zA-Z0-9]*-?)*$",},
                    "is_cronjob": {"type": "boolean",},
                    "start_command": {"type": "string",},
                },
                "required": ["name", "is_cronjob", "start_command"],
            },
        },
        "scales": {"$ref": "#/definitions/scales",},
        "crons": {"$ref": "#/definitions/crons",},
        "resources": {"$ref": "#/definitions/resources",},
        "templateVars": {
            "type": "object",
            "properties": {
                "tplCriticity": {
                    "type": "string",
                    "enum": ["high", "low", "none"],
                    "description": "Define if the application is on the critical path",
                },
                "tplPublicService": {
                    "type": "string",
                    "enum": ["true", "false"],
                    "description": "Define if the application web is public accessible or not",
                },
                "tplExpandedTimeout": {
                    "type": "integer",
                    "example": "3600",
                    "description": "Define the timeout on the ingress controller",
                },
                "tplMountDirectory": {
                    "type": "string",
                    "example": "/opt/my-folder",
                    "description": "Define the folder to mount a file through ConfigMap or others",
                },
                "tplSessionAffinity": {
                    "type": "boolean",
                    "example": "false",
                    "description": "Activate or deactivate session affinity on ingress controller",
                },
                "tplTerminationGracePeriod": {
                    "type": "integer",
                    "example": "20",
                    "description": "Define POD termination grace period",
                },
                "tplCanary": {
                    "type": "string",
                    "pattern": "^[a-z0-9-]+",
                    "example": "test-123",
                    "description": "Define name for canary",
                },
            },
            "additionalProperties": False,
        },
        "dependencies": {"type": "array", "items": {"type": "string",},},
        "docker": {
            "type": "object",
            "properties": {"image_name": {"type": "string",}, "dockerfile": {"type": "string",},},
            "additionalProperties": False,
        },
        "is_enabled": {"type": "boolean",},
        "public": {"type": "boolean",},
        "public_aliases": {"type": "array", "items": {"type": "string",},},
        "probes": {
            "type": "object",
            "properties": {"web": {"type": "object",},},
            "additionalProperties": False,
        },
        "variables": {
            "type": "object",
            "properties": {
                # Awaiting for implementation Explain in a markdown file the meaning of each part
                "app": {"$ref": "#/definitions/variables/confSubObjects",},
                "ope": {"$ref": "#/definitions/variables/confSubObjects",},
                "integration": {"$ref": "#/definitions/variables/confSubObjects",},
                "secret": {"$ref": "#/definitions/variables/subObjectSecrets",},
            },
            "required": ["app", "ope"],
            "additionalProperties": False,
        },
    },
    "required": ["app", "variables", "git", "is_enabled"],
    "additionalProperties": True,
}
