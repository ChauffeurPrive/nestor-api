# pylint: disable=duplicate-code
"""Schemas class to validate the Nestor configurations"""

from validator.schemas.application import APPLICATION_SCHEMA
from validator.schemas.project import PROJECT_SCHEMA
from validator.schemas.specs import SPECS

SCHEMA_BASE: str = "http://json-schema.org/draft-07/schema#"
APPLICATIONS_SCHEMA: dict = {
    "$schema": SCHEMA_BASE,
    "definitions": SPECS,
    **APPLICATION_SCHEMA,
}

PROJECTS_SCHEMA: dict = {
    "$schema": SCHEMA_BASE,
    "definitions": SPECS,
    **PROJECT_SCHEMA,
}

SCHEMAS = {
    **APPLICATIONS_SCHEMA,
    **PROJECTS_SCHEMA,
}
