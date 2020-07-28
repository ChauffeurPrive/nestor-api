from unittest import TestCase
from unittest.mock import call, patch

import nestor_api.lib.k8s.builders as k8s_builders
import tests.__fixtures__.k8s as k8s_fixtures


class TestK8sBuilders(TestCase):
    def compiled_templates_mock(self):
        """To mock compiled templates (with handlebars)"""

        def check_anti_affinity_node_template(parameters):
            self.assertEqual(parameters, {"app": "app", "process": "web"})
            return "mock: template_anti_affinity_node"

        def check_anti_affinity_zone_template(parameters):
            self.assertEqual(parameters, {"app": "app", "process": "web"})
            return "mock: template_anti_affinity_zone"

        def check_hpa(parameters):
            self.assertEqual(
                parameters,
                {
                    "app": "app",
                    "process": "web",
                    "name": "app----web",
                    "minReplicas": 5,
                    "maxReplicas": 15,
                    "targetCPUUtilizationPercentage": 90,
                },
            )
            return "mock: template_hpa"

        def check_namespace(parameters):
            self.assertEqual(parameters, {"name": "namespace"})
            return "mock: template_namespace"

        return {
            "anti_affinity_node": check_anti_affinity_node_template,
            "anti_affinity_zone": check_anti_affinity_zone_template,
            "hpa": check_hpa,
            "namespace": check_namespace,
        }

    @patch("nestor_api.lib.k8s.builders.io", autospec=True)
    def test_load_templates(self, io_mock):
        """Should load the templates and correctly substitute `{{variable}}`"""

        io_mock.read.side_effect = (
            lambda file_name: f"file: {file_name}\n" + "template: {{variable}}\n"
        )

        templates = k8s_builders.load_templates("/path", ["template_a", "template_b"])
        result_a = templates["template_a"]({"variable": "value_a"})
        result_b = templates["template_b"]({"variable": "value_b"})

        io_mock.read.assert_has_calls(
            [call("/path/template_a.yaml"), call("/path/template_b.yaml")]
        )
        self.assertEqual(result_a, "file: /path/template_a.yaml\ntemplate: value_a\n")
        self.assertEqual(result_b, "file: /path/template_b.yaml\ntemplate: value_b\n")

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_get_anti_affinity_node_not_enabled_default(self, parse_yaml_mock):
        """Returns None if not enabled by default"""
        parse_yaml_mock.return_value = k8s_fixtures.anti_affinity_node
        anti_affinity_node = k8s_builders.get_anti_affinity_node(
            {"app": "app", "affinity": {"default": {"is_anti_affinity_node_enabled": False}}},
            "web",
            self.compiled_templates_mock(),
        )

        self.assertEqual(anti_affinity_node, None)

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_get_anti_affinity_node_not_enabled_for_process(self, parse_yaml_mock):
        """Returns None if not enabled for the process"""
        parse_yaml_mock.return_value = k8s_fixtures.anti_affinity_node
        anti_affinity_node = k8s_builders.get_anti_affinity_node(
            {
                "app": "app",
                "affinity": {
                    "default": {"is_anti_affinity_node_enabled": False},
                    "web": {"is_anti_affinity_node_enabled": False},
                },
            },
            "web",
            self.compiled_templates_mock(),
        )
        self.assertEqual(anti_affinity_node, None)

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_get_anti_affinity_node_enabled_default(self, parse_yaml_mock):
        """Returns the anti affinity node if enabled by default"""
        parse_yaml_mock.return_value = k8s_fixtures.anti_affinity_node
        anti_affinity_node = k8s_builders.get_anti_affinity_node(
            {"app": "app", "affinity": {"default": {"is_anti_affinity_node_enabled": True}}},
            "web",
            self.compiled_templates_mock(),
        )
        self.assertEqual(anti_affinity_node, k8s_fixtures.anti_affinity_node)

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_get_anti_affinity_node_enabled_for_process(self, parse_yaml_mock):
        """Returns the anti affinity node if enabled for the process"""
        parse_yaml_mock.return_value = k8s_fixtures.anti_affinity_node
        anti_affinity_node = k8s_builders.get_anti_affinity_node(
            {
                "app": "app",
                "affinity": {
                    "default": {"is_anti_affinity_node_enabled": False},
                    "web": {"is_anti_affinity_node_enabled": True},
                },
            },
            "web",
            self.compiled_templates_mock(),
        )
        self.assertEqual(anti_affinity_node, k8s_fixtures.anti_affinity_node)

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_get_anti_affinity_zone_not_enabled_default(self, parse_yaml_mock):
        """Returns None if not enabled by default"""
        parse_yaml_mock.return_value = k8s_fixtures.anti_affinity_zone
        anti_affinity_zone = k8s_builders.get_anti_affinity_zone(
            {"app": "app", "affinity": {"default": {"is_anti_affinity_zone_enabled": False}}},
            "web",
            self.compiled_templates_mock(),
        )

        self.assertEqual(anti_affinity_zone, None)

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_get_anti_affinity_zone_not_enabled_for_process(self, parse_yaml_mock):
        """Returns None if not enabled for the process"""
        parse_yaml_mock.return_value = k8s_fixtures.anti_affinity_zone
        anti_affinity_zone = k8s_builders.get_anti_affinity_zone(
            {
                "app": "app",
                "affinity": {
                    "default": {"is_anti_affinity_zone_enabled": False},
                    "web": {"is_anti_affinity_zone_enabled": False},
                },
            },
            "web",
            self.compiled_templates_mock(),
        )
        self.assertEqual(anti_affinity_zone, None)

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_get_anti_affinity_zone_enabled_default(self, parse_yaml_mock):
        """Returns the anti affinity zone if enabled by default"""
        parse_yaml_mock.return_value = k8s_fixtures.anti_affinity_zone
        anti_affinity_zone = k8s_builders.get_anti_affinity_zone(
            {"app": "app", "affinity": {"default": {"is_anti_affinity_zone_enabled": True}}},
            "web",
            self.compiled_templates_mock(),
        )
        self.assertEqual(anti_affinity_zone, k8s_fixtures.anti_affinity_zone)

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_get_anti_affinity_zone_enabled_for_process(self, parse_yaml_mock):
        """Returns the anti affinity zone if enabled for the process"""
        parse_yaml_mock.return_value = k8s_fixtures.anti_affinity_zone
        anti_affinity_zone = k8s_builders.get_anti_affinity_zone(
            {
                "app": "app",
                "affinity": {
                    "default": {"is_anti_affinity_zone_enabled": False},
                    "web": {"is_anti_affinity_zone_enabled": True},
                },
            },
            "web",
            self.compiled_templates_mock(),
        )
        self.assertEqual(anti_affinity_zone, k8s_fixtures.anti_affinity_zone)

    def test_get_image_name_branch(self):
        """Returns the URL of the docker image if tag and branch are provided"""
        app_config = {"app": "app", "registry": {"organization": "my-organization"}}
        image_url = k8s_builders.get_image_name(
            app_config, {"branch": "feature/api", "tag": "1.0.0-sha-a2b3c4"}
        )
        self.assertEqual(image_url, "my-organization/app:feature/api")

    def test_get_image_name_tag(self):
        """Returns the URL of the docker image if only a tag is provided"""
        app_config = {"app": "app", "registry": {"organization": "my-organization"}}
        image_url = k8s_builders.get_image_name(app_config, {"tag": "1.0.0-sha-a2b3c4"})
        self.assertEqual(image_url, "my-organization/app:1.0.0-sha-a2b3c4")

    def test_get_probes_both_configured(self):
        """Check that the configuration of probes is correct if both configured"""
        probes = k8s_builders.get_probes(
            {
                "liveness": {"path": "/api/heartbeat", "delay": 5, "period": 5, "timeout": 1},
                "readiness": {"path": "/api/heartbeat", "delay": 10, "period": 10, "timeout": 2},
            },
            8080,
        )

        self.assertEqual(
            probes,
            {
                "livenessProbe": {
                    "httpGet": {"path": "/api/heartbeat", "port": 8080},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5,
                    "timeoutSeconds": 1,
                },
                "readinessProbe": {
                    "httpGet": {"path": "/api/heartbeat", "port": 8080},
                    "initialDelaySeconds": 10,
                    "periodSeconds": 10,
                    "timeoutSeconds": 2,
                },
            },
        )

    def test_get_probes_liveness_only(self):
        """Check that the configuration of probes is correct if only liveness configured"""
        probes = k8s_builders.get_probes(
            {"liveness": {"path": "/api/heartbeat", "delay": 5, "period": 5, "timeout": 1}}, 8080
        )

        self.assertEqual(
            probes,
            {
                "livenessProbe": {
                    "httpGet": {"path": "/api/heartbeat", "port": 8080},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5,
                    "timeoutSeconds": 1,
                },
            },
        )

    def test_get_probes_readiness_only(self):
        """Check that the configuration of probes is correct if only readiness configured"""
        probes = k8s_builders.get_probes(
            {"readiness": {"path": "/api/heartbeat", "delay": 5, "period": 5, "timeout": 1}}, 8080
        )

        self.assertEqual(
            probes,
            {
                "readinessProbe": {
                    "httpGet": {"path": "/api/heartbeat", "port": 8080},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5,
                    "timeoutSeconds": 1,
                },
            },
        )

    def test_get_probes_unique_config_for_both(self):
        """Check that the configuration of probes is correct if configuration is unique for both"""
        probes = k8s_builders.get_probes(
            {"path": "/api/heartbeat", "delay": 5, "period": 5, "timeout": 1}, 8080
        )

        self.assertEqual(
            probes,
            {
                "livenessProbe": {
                    "httpGet": {"path": "/api/heartbeat", "port": 8080},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5,
                    "timeoutSeconds": 1,
                },
                "readinessProbe": {
                    "httpGet": {"path": "/api/heartbeat", "port": 8080},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5,
                    "timeoutSeconds": 1,
                },
            },
        )

    def test_get_sanitized_names_nothing_to_sanitize(self):
        """Does not sanitize if already clean"""
        app, sanitized_process_name, metadata_name = k8s_builders.get_sanitized_names(
            {"app": "app"}, "web"
        )

        self.assertEqual(app, "app")
        self.assertEqual(sanitized_process_name, "web")
        self.assertEqual(metadata_name, "app----web")

    def test_get_sanitized_names_lowercase(self):
        """Transform to lowercase application and process name"""
        app, sanitized_process_name, metadata_name = k8s_builders.get_sanitized_names(
            {"app": "app"}, "My-Web-Process"
        )

        self.assertEqual(app, "app")
        self.assertEqual(sanitized_process_name, "my-web-process")
        self.assertEqual(metadata_name, "app----my-web-process")

    def test_get_sanitized_names_underscore(self):
        """Transform underscores into dashes"""
        app, sanitized_process_name, metadata_name = k8s_builders.get_sanitized_names(
            {"app": "app"}, "my_web_process"
        )

        self.assertEqual(app, "app")
        self.assertEqual(sanitized_process_name, "my-web-process")
        self.assertEqual(metadata_name, "app----my-web-process")

    def test_get_secret_variables(self):
        """Merge both app and ope variables"""
        app_config = {
            "variables": {
                "secret": {
                    "SECRET_USERNAME": {"name": "mysecret", "key": "username"},
                    "SECRET_PASSWORD": {"name": "mysecret", "key": "password"},
                }
            }
        }

        variables = k8s_builders.get_secret_variables(app_config)

        self.assertEqual(
            variables,
            {
                "SECRET_PASSWORD": {"secretKeyRef": {"key": "password", "name": "mysecret"}},
                "SECRET_USERNAME": {"secretKeyRef": {"key": "username", "name": "mysecret"}},
            },
        )

    def test_get_variables(self):
        """Merge both app and ope variables"""
        app_config = {
            "variables": {
                "app": {"VARIABLE_1": "1111", "VARIABLE_2": "2222"},
                "ope": {"VARIABLE_2": "3333", "VARIABLE_3": "4444"},
            }
        }

        variables = k8s_builders.get_variables(app_config)

        self.assertEqual(
            variables, {"VARIABLE_1": "1111", "VARIABLE_2": "3333", "VARIABLE_3": "4444"}
        )

    def test_set_namespace_no_namespace(self):
        """Return None if no namespace in config and should not modify resources definition"""
        app_config = {}
        resources = [
            {"metadata": {"name": "hpa"}},
            {"metadata": {"name": "deployment"}},
        ]

        namespace = k8s_builders.set_namespace(
            app_config, resources, self.compiled_templates_mock()
        )

        self.assertEqual(namespace, None)
        self.assertEqual(
            resources, [{"metadata": {"name": "hpa"}}, {"metadata": {"name": "deployment"}},]
        )

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_set_namespace_with_namespace(self, parse_yaml_mock):
        """Return namespace and should modify resources definition"""
        parse_yaml_mock.return_value = k8s_fixtures.namespace

        app_config = {"namespace": "namespace"}
        resources = [
            {"metadata": {"name": "hpa"}},
            {"metadata": {"name": "deployment"}},
        ]

        namespace = k8s_builders.set_namespace(
            app_config, resources, self.compiled_templates_mock()
        )

        self.assertEqual(namespace, k8s_fixtures.namespace)
        self.assertEqual(
            resources,
            [
                {"metadata": {"name": "hpa", "namespace": "namespace"}},
                {"metadata": {"name": "deployment", "namespace": "namespace"}},
            ],
        )

    def test_set_replicas_min_replicas_zero(self):
        """Return None and set replicas to 0 in the recipe"""
        app_config = {"app": "app", "scales": {"web": {"minReplicas": 0}}}
        recipe = {"spec": {}}
        hpa = k8s_builders.set_replicas(app_config, "web", recipe, self.compiled_templates_mock())
        self.assertEqual(hpa, None)
        self.assertEqual(recipe, {"spec": {"replicas": 0}})

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_set_replicas_with_process_default(self, parse_yaml_mock):
        """Return the hpa configuration"""
        parse_yaml_mock.return_value = k8s_fixtures.hpa

        app_config = {
            "app": "app",
            "scales": {
                "default": {
                    "minReplicas": 5,
                    "maxReplicas": 15,
                    "targetCPUUtilizationPercentage": 90,
                },
            },
        }
        recipe = {"spec": {}}

        hpa = k8s_builders.set_replicas(app_config, "web", recipe, self.compiled_templates_mock())

        self.assertEqual(hpa, k8s_fixtures.hpa)

    @patch("yaml_lib.parse_yaml", autospec=True)
    def test_set_replicas_with_process_configuration(self, parse_yaml_mock):
        """Return the hpa configuration"""
        parse_yaml_mock.return_value = k8s_fixtures.hpa

        app_config = {
            "app": "app",
            "scales": {
                "default": {
                    "minReplicas": 3,
                    "maxReplicas": 9,
                    "targetCPUUtilizationPercentage": 80,
                },
                "web": {"minReplicas": 5, "maxReplicas": 15, "targetCPUUtilizationPercentage": 90},
            },
        }
        recipe = {"spec": {}}

        hpa = k8s_builders.set_replicas(app_config, "web", recipe, self.compiled_templates_mock())

        self.assertEqual(hpa, k8s_fixtures.hpa)

    def test_set_resources_no_resources_default(self):
        """Should not set resources if none are configured"""
        app_config = {}
        recipe = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "app----web"},
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": "app",
                                "image": "my-organization/app:1.0.0-sha-a1b2c3d",
                                "imagePullPolicy": "Always",
                                "env": [{"name": "MESSAGE", "value": "hello world"}],
                            }
                        ],
                    }
                }
            },
        }

        k8s_builders.set_resources(app_config, "web", recipe)
        self.assertEqual(
            recipe,
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": "app----web",},
                "spec": {
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": "app",
                                    "image": "my-organization/app:1.0.0-sha-a1b2c3d",
                                    "imagePullPolicy": "Always",
                                    "env": [{"name": "MESSAGE", "value": "hello world"}],
                                }
                            ],
                        }
                    }
                },
            },
        )

    def test_set_resources_configured_default(self):
        """Should set default resources configured"""
        app_config = {
            "resources": {
                "default": {
                    "requests": {"memory": "256Mi", "cpu": 0.1},
                    "limits": {"memory": "1024Mi", "cpu": 1},
                }
            }
        }
        recipe = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "app----web",},
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": "app",
                                "image": "my-organization/app:1.0.0-sha-a1b2c3d",
                                "imagePullPolicy": "Always",
                                "env": [{"name": "MESSAGE", "value": "hello world"}],
                            }
                        ],
                    }
                }
            },
        }

        k8s_builders.set_resources(app_config, "web", recipe)
        self.assertEqual(
            recipe,
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": "app----web",},
                "spec": {
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": "app",
                                    "image": "my-organization/app:1.0.0-sha-a1b2c3d",
                                    "imagePullPolicy": "Always",
                                    "env": [{"name": "MESSAGE", "value": "hello world"}],
                                    "resources": {
                                        "requests": {"memory": "256Mi", "cpu": 0.1},
                                        "limits": {"memory": "1024Mi", "cpu": 1},
                                    },
                                }
                            ],
                        }
                    }
                },
            },
        )

    def test_set_resources_configured_process(self):
        """Should set resources configured for the process"""
        app_config = {
            "resources": {
                "default": {
                    "requests": {"memory": "256Mi", "cpu": 0.1},
                    "limits": {"memory": "1024Mi", "cpu": 1},
                },
                "web": {
                    "requests": {"memory": "512Mi", "cpu": 0.2},
                    "limits": {"memory": "2048Mi", "cpu": 2},
                },
            }
        }
        recipe = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "app----web",},
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": "app",
                                "image": "my-organization/app:1.0.0-sha-a1b2c3d",
                                "imagePullPolicy": "Always",
                                "env": [{"name": "MESSAGE", "value": "hello world"}],
                            }
                        ],
                    }
                }
            },
        }

        k8s_builders.set_resources(app_config, "web", recipe)
        self.assertEqual(
            recipe,
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": "app----web",},
                "spec": {
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": "app",
                                    "image": "my-organization/app:1.0.0-sha-a1b2c3d",
                                    "imagePullPolicy": "Always",
                                    "env": [{"name": "MESSAGE", "value": "hello world"}],
                                    "resources": {
                                        "requests": {"memory": "512Mi", "cpu": 0.2},
                                        "limits": {"memory": "2048Mi", "cpu": 2},
                                    },
                                }
                            ],
                        }
                    }
                },
            },
        )
