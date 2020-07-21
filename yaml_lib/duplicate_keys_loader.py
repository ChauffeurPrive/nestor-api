"""A custom YAML Loader to comply with the official YAML Spec

This constructor is a workaround for the issue: https://github.com/yaml/pyyaml/issues/165

The YAML spec states that duplicated keys are not allowed within the same block,
including the root block.

Currently pyyaml, doesn't raise any exception. And silently uses the latter key,
in the yaml file for duplicated keys.

With this custom loader, it's possible to detect and raise an exception for duplicated keys.
"""

import yaml


class DuplicateKeysLoader(yaml.SafeLoader):  # pylint: disable=too-many-ancestors
    """A custom YAML Loader to comply with the official YAML Spec"""

    def construct_mapping(self, node, deep=False) -> dict:
        """Create a YAML mapping node to avoid duplicates

        Args:
            self (SafeConstructor): the safe constructor to override the default loader
            node (dict): The node representing a yaml part
            deep (bool, optional): Flag to specify deep . Defaults to False.

        Raises:
            yaml.constructor.ConstructorError: An error if a duplicate key is found

        Returns:
            dict: The representation of the yaml file as a dict
        """

        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in result:
                raise yaml.constructor.ConstructorError(f"Found a duplicate key: {key}")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


DuplicateKeysLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, DuplicateKeysLoader.construct_mapping,
)
