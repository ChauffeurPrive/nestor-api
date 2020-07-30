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
            "anti-affinity-node": check_anti_affinity_node_template,
            "anti-affinity-zone": check_anti_affinity_zone_template,
            "hpa": check_hpa,
            "namespace": check_namespace,
        }

    @patch("nestor_api.lib.k8s.builders.io", autospec=True)
    def test_load_templates(self, io_mock):
        """Should load the templates and correctly substitute `{{variable}}`."""

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
        app_config = {
            "app": "app",
            "registry": {"platform": "docker-hub", "id": "id-1"},
            "docker": {
                "registries": {
                    "docker-hub": [
                        {"id": "id-1", "organization": "my-organization-1"},
                        {"id": "id-2", "organization": "my-organization-2"},
                    ],
                },
            },
        }
        image_url = k8s_builders.get_image_name(
            app_config, {"branch": "feature/api", "tag": "1.0.0-sha-a2b3c4"}
        )
        self.assertEqual(image_url, "my-organization-1/app:feature/api")

    def test_get_image_name_tag(self):
        """Returns the URL of the docker image if only a tag is provided"""
        app_config = {
            "app": "app",
            "registry": {"platform": "docker-hub", "id": "id-1"},
            "docker": {
                "registries": {
                    "docker-hub": [
                        {"id": "id-1", "organization": "my-organization-1"},
                        {"id": "id-2", "organization": "my-organization-2"},
                    ],
                },
            },
        }
        image_url = k8s_builders.get_image_name(app_config, {"tag": "1.0.0-sha-a2b3c4"})
        self.assertEqual(image_url, "my-organization-1/app:1.0.0-sha-a2b3c4")

    def test_get_image_name_registry_not_found(self):
        """Should throw if the registry is not in the configuration."""
        app_config = {
            "app": "app",
            "registry": {"platform": "docker-hub", "id": "id-not-existing"},
            "docker": {"registries": {"docker-hub": [],},},
        }

        with self.assertRaisesRegex(ValueError, 'No registry matching "id-not-existing"'):
            k8s_builders.get_image_name(app_config, {"tag": "1.0.0-sha-a2b3c4"})

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

    @patch("nestor_api.lib.k8s.builders.get_anti_affinity_zone", autospec=True)
    @patch("nestor_api.lib.k8s.builders.get_anti_affinity_node", autospec=True)
    def test_set_anti_affinity_when_both_true(
        self, get_anti_affinity_node_mock, get_anti_affinity_zone_mock
    ):
        """Should correctly merge both specs."""
        get_anti_affinity_node_mock.return_value = k8s_fixtures.anti_affinity_node
        get_anti_affinity_zone_mock.return_value = k8s_fixtures.anti_affinity_zone
        deployment = {"spec": {"template": {"spec": {}}}}

        k8s_builders.set_anti_affinity({}, "web", deployment, {})

        self.assertEqual(
            deployment["spec"]["template"]["spec"]["affinity"],
            {
                "podAntiAffinity": {
                    "preferredDuringSchedulingIgnoredDuringExecution": [
                        {
                            "weight": 1,
                            "podAffinityTerm": {
                                "labelSelector": {
                                    "matchExpressions": [
                                        {"key": "app", "operator": "In", "values": ["app-name"]},
                                        {
                                            "key": "process",
                                            "operator": "In",
                                            "values": ["proc-name"],
                                        },
                                    ],
                                },
                                "topologyKey": "kubernetes.io/hostname",
                            },
                        },
                        {
                            "weight": 1,
                            "podAffinityTerm": {
                                "labelSelector": {
                                    "matchExpressions": [
                                        {"key": "app", "operator": "In", "values": ["app-name"]},
                                        {
                                            "key": "process",
                                            "operator": "In",
                                            "values": ["proc-name"],
                                        },
                                    ],
                                },
                                "topologyKey": "failure-domain.beta.kubernetes.io/zone",
                            },
                        },
                    ],
                },
            },
        )

    @patch("nestor_api.lib.k8s.builders.get_anti_affinity_zone", autospec=True)
    @patch("nestor_api.lib.k8s.builders.get_anti_affinity_node", autospec=True)
    def test_set_anti_affinity_when_both_false(
        self, get_anti_affinity_node_mock, get_anti_affinity_zone_mock
    ):
        """Should not add the section to the spec."""
        get_anti_affinity_node_mock.return_value = None
        get_anti_affinity_zone_mock.return_value = None
        resource = {"spec": {"template": {"spec": {}}}}

        k8s_builders.set_anti_affinity({}, "web", resource, {})

        self.assertEqual(resource, {"spec": {"template": {"spec": {}}}})

    def test_set_command(self):
        """Should correctly set the process' command to the resource."""
        process = {"start_command": "npm start"}
        resource = {"spec": {"template": {"spec": {"containers": [{}]}}}}

        k8s_builders.set_command(process, resource)

        self.assertEqual(
            resource,
            {
                "spec": {
                    "template": {
                        "spec": {"containers": [{"args": ["/bin/bash", "-c", "npm start"]}]},
                    },
                },
            },
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

    def test_set_environment_variables(self):
        """Should correctly attach the environment variables."""
        deployment_config = {
            "variables": {
                "app": {"APP_VAR_1": "app_var_1", "APP_VAR_2": "app_var_2",},
                "ope": {
                    "PORT": "4242",  # should be overridden
                    "OPE_VAR_1": "ope_var_1",
                    "OPE_VAR_2": "ope_var_2",
                },
                "secret": {
                    "SECRET_VAR_1": {"name": "secret-name", "key": "SECRET_VAR_1"},
                    "SECRET_VAR_2": {"name": "secret-name", "key": "SECRET_VAR_2"},
                },
            },
        }
        resource = {"spec": {"template": {"spec": {"containers": [{}]}}}}

        k8s_builders.set_environment_variables(deployment_config, resource)

        self.assertEqual(
            resource["spec"]["template"]["spec"]["containers"][0]["env"],
            [
                {"name": "APP_VAR_1", "value": "app_var_1"},
                {"name": "APP_VAR_2", "value": "app_var_2"},
                {"name": "PORT", "value": "8080"},
                {"name": "OPE_VAR_1", "value": "ope_var_1"},
                {"name": "OPE_VAR_2", "value": "ope_var_2"},
                {
                    "name": "SECRET_VAR_1",
                    "valueFrom": {"secretKeyRef": {"key": "SECRET_VAR_1", "name": "secret-name"}},
                },
                {
                    "name": "SECRET_VAR_2",
                    "valueFrom": {"secretKeyRef": {"key": "SECRET_VAR_2", "name": "secret-name"}},
                },
            ],
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

    def test_set_node_selector_configured(self):
        """Should use the configured node selector from the configuration."""
        deployment_config = {"nodeSelector": {"my-process": {"tier": "app"}}}
        resource = {"spec": {"template": {"spec": {}}}}

        k8s_builders.set_node_selector(deployment_config, "my-process", resource)

        self.assertEqual(resource["spec"]["template"]["spec"]["nodeSelector"], {"tier": "app"})

    def test_set_node_selector_default(self):
        """Should use the default node selector from the configuration."""
        deployment_config = {"nodeSelector": {"default": {"tier": "app"}}}
        resource = {"spec": {"template": {"spec": {}}}}

        k8s_builders.set_node_selector(deployment_config, "my-process-not-configured", resource)

        self.assertEqual(resource["spec"]["template"]["spec"]["nodeSelector"], {"tier": "app"})

    def test_set_node_selector_none(self):
        """Should not set the node selector if none is found in the configuration."""
        deployment_config = {"nodeSelector": {}}
        resource = {"spec": {"template": {"spec": {}}}}

        k8s_builders.set_node_selector(deployment_config, "my-process", resource)

        self.assertEqual(resource["spec"]["template"]["spec"], {})

    @patch("nestor_api.lib.k8s.builders.get_probes", autospec=True)
    def test_set_probes_configured(self, get_probes_mock):
        """Should attach the probes to the resource."""
        get_probes_mock.return_value = k8s_fixtures.probes
        deployment_config = {"probes": {"my-process": {}}}
        resource = {"spec": {"template": {"spec": {"containers": [{}]}}}}

        k8s_builders.set_probes(deployment_config, "my-process", resource)

        self.assertEqual(
            resource["spec"]["template"]["spec"]["containers"][0],
            {
                "livenessProbe": {
                    "httpGet": {"path": "/heartbeat", "port": 8080},
                    "initialDelaySeconds": 10,
                    "periodSeconds": 10,
                    "timeoutSeconds": 2,
                },
                "readinessProbe": {
                    "httpGet": {"path": "/heartbeat", "port": 8080},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5,
                    "timeoutSeconds": 1,
                },
            },
        )

    @patch("nestor_api.lib.k8s.builders.get_probes", autospec=True)
    def test_set_probes_only_liveness_configured(self, get_probes_mock):
        """Should attach the liveness probes to the resource."""
        get_probes_mock.return_value = {
            "livenessProbe": k8s_fixtures.probes["livenessProbe"],
        }
        deployment_config = {"probes": {"my-process": {}}}
        resource = {"spec": {"template": {"spec": {"containers": [{}]}}}}

        k8s_builders.set_probes(deployment_config, "my-process", resource)

        self.assertEqual(
            resource["spec"]["template"]["spec"]["containers"][0],
            {
                "livenessProbe": {
                    "httpGet": {"path": "/heartbeat", "port": 8080},
                    "initialDelaySeconds": 10,
                    "periodSeconds": 10,
                    "timeoutSeconds": 2,
                },
            },
        )

    @patch("nestor_api.lib.k8s.builders.get_probes", autospec=True)
    def test_set_probes_only_readiness_configured(self, get_probes_mock):
        """Should attach the readiness probes to the resource."""
        get_probes_mock.return_value = {
            "readinessProbe": k8s_fixtures.probes["readinessProbe"],
        }
        deployment_config = {"probes": {"my-process": {}}}
        resource = {"spec": {"template": {"spec": {"containers": [{}]}}}}

        k8s_builders.set_probes(deployment_config, "my-process", resource)

        self.assertEqual(
            resource["spec"]["template"]["spec"]["containers"][0],
            {
                "readinessProbe": {
                    "httpGet": {"path": "/heartbeat", "port": 8080},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5,
                    "timeoutSeconds": 1,
                },
            },
        )

    @patch("nestor_api.lib.k8s.builders.get_probes", autospec=True)
    def test_set_probes_not_configured(self, get_probes_mock):
        """Should not attach the probes to the resource if not configured."""
        deployment_config = {"probes": {}}
        resource = {"spec": {"template": {"spec": {"containers": [{}]}}}}

        k8s_builders.set_probes(deployment_config, "my-process", resource)

        self.assertEqual(
            resource["spec"]["template"]["spec"]["containers"][0], {},
        )
        get_probes_mock.assert_not_called()

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

    def test_set_secret_configured(self):
        """Should attach the configured secret to the resource."""
        deployment_config = {"secret": "secret-registry"}
        resource = {"spec": {"template": {"spec": {}}}}

        k8s_builders.set_secret(deployment_config, resource)

        self.assertEqual(
            resource["spec"]["template"]["spec"],
            {"imagePullSecrets": [{"name": "secret-registry"}]},
        )

    def test_set_secret_not_configured(self):
        """Should not attach the secret if none configured."""
        deployment_config = {}
        resource = {"spec": {"template": {"spec": {}}}}

        k8s_builders.set_secret(deployment_config, resource)

        self.assertEqual(
            resource["spec"]["template"]["spec"], {},
        )
