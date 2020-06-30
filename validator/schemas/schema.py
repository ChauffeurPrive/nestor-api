"""Schemas class to validate the Nestor configurations"""

from application import APPLICATION_SCHEMA
from project import PROJECT_SCHEMA
from specs import SPECS

SCHEMAS = {
    "APPLICATIONS": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": SPECS,
        **APPLICATION_SCHEMA,
    },
    "PROJECT": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": SPECS,
        **PROJECT_SCHEMA,
    }
}
