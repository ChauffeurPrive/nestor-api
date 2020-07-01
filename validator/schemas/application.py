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
        "databases": {
            "type": "object",
            "properties": {
                "postgres": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "db": {"type": "string",},
                            "password": {"type": "string",},
                            "username": {"type": "string",},
                        },
                    },
                },
            },
        },
        "scales": {"$ref": "#/definitions/scales",},
        "crons": {"$ref": "#/definitions/crons",},
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
                "tplTeam": {
                    "type": "string",
                    "example": "team-payment",
                    "description": "Define the team that is owner.",
                },
                "tplSlackAlertingChannel": {
                    "type": "string",
                    "example": "team-payment-alerts",
                    "description": "Define the slack channel for alerting",
                },
                "tplWeb2xxThreshold": {
                    "type": "string",
                    "pattern": "^[\b100\b|\b90\b|\b80\b|\b70\b|\b60\b|\b50\b|\b0\b|\bdefault\b]",
                    "example": "50",
                    "description": "Define the threshold for 2xx status. If below alert is raised.",
                },
                "tplWeb5xxThreshold": {
                    "type": "string",
                    "pattern": "^[\b40\b|\b10\b|\b5\b|\b0\b|\bdefault\b]",
                    "example": "40",
                    "description": "Define the threshold for 5xx errors. If above alert is raised.",
                },
                "tplWeb50thLatencyThreshold": {
                    "type": "string",
                    "pattern": "^0.0[12458]|^0.12$|^0.30$|^[123]$|^default$",
                    "example": "0.12",
                    "description": "Define the threshold for 50th percentile latency in ms."
                                   + "If above alert is raised.",
                },
                "tplWeb95thLatencyThreshold": {
                    "type": "string",
                    "pattern": "^0.0[123457]|^0.[123456]0$|^[124]$|^1.5$|^default$",
                    "example": "1.5",
                    "description": "Define the threshold for 95th percentile latency in ms."
                                   + "If above alert is raised.",
                },
                "tplSLO": {
                    "type": "string",
                    "pattern": "^99$|^99.[9]{1,3}|^none$",
                    "example": "99.9",
                    "description": "Define SLO in terms of availability",
                },
                "tplSLI": {
                    "type": "string",
                    "enum": [
                        "success_2xx",
                        "error_5xx",
                        "latency_50th",
                        "latency_95th",
                        "error_5xx_latency_50th",
                        "error_5xx_latency_95th",
                        "error_5xx_latency_50th_latency_95th",
                        "none",
                    ],
                    "description": "Define the SLI to use to calculate availability",
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
        "teams": {
            "oneOf": [
                {"type": "array", "items": {"type": "string",},},
                {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string",},
                        "slack": {"type": "string",},
                        "jira": {"type": "string",},
                    },
                    "required": ["name", "slack", "jira"],
                },
            ],
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
                "app": {"$ref": "#/definitions/variables/confSubObjects",},
                "ope": {"$ref": "#/definitions/variables/confSubObjects",},
                "integration": {"$ref": "#/definitions/variables/confSubObjects",},
                "secret": {"$ref": "#/definitions/variables/subObjectSecrets",},
            },
            "required": ["app", "ope"],
            "additionalProperties": False,
        },
    },
    "required": ["app", "variables", "git", "is_enabled", "teams"],
    "additionalProperties": True,
}
