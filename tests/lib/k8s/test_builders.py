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
            "app": "my-app",
            "docker": {"registry": {"organization": "my-organization"}},
        }
        image_url = k8s_builders.get_image_name(
            app_config, {"branch": "feature/api", "tag": "1.0.0-sha-a2b3c4"}
        )
        self.assertEqual(image_url, "my-organization/my-app:feature/api")

    def test_get_image_name_tag(self):
        """Returns the URL of the docker image if only a tag is provided"""
        app_config = {
            "app": "my-app",
            "docker": {"registry": {"organization": "my-organization"}},
        }
        image_url = k8s_builders.get_image_name(app_config, {"tag": "1.0.0-sha-a2b3c4"})
        self.assertEqual(image_url, "my-organization/my-app:1.0.0-sha-a2b3c4")

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

    @patch("nestor_api.lib.k8s.builders.K8sConfiguration", autospec=True)
    def test_set_environment_variables(self, config_mock):
        """Should correctly attach the environment variables."""
        config_mock.get_service_port.return_value = 4242
        deployment_config = {
            "variables": {
                "app": {"APP_VAR_1": "app_var_1", "APP_VAR_2": "app_var_2",},
                "ope": {
                    "PORT": "1234",  # should be overridden
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
                {"name": "PORT", "value": "4242"},
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

    @patch("nestor_api.lib.k8s.builders.load_templates", autospec=True)
    @patch("nestor_api.lib.k8s.builders.get_sections_for_cronjob", autospec=True)
    @patch("nestor_api.lib.k8s.builders.get_sections_for_process", autospec=True)
    def test_build_yaml(
        self, get_sections_for_process_mock, get_sections_for_cronjobs_mock, _load_templates_mock
    ):
        """Should correctly concatenate the built sections."""
        # Mock
        def _cron_mock(cronjob, _1, _2, _3):
            return ["---", f'cronjob: {cronjob["name"]}']

        def _process_mock(process, _1, _2, _3):
            return ["---", f'hpa: {process["name"]}', "---", f'process: {process["name"]}']

        get_sections_for_cronjobs_mock.side_effect = _cron_mock
        get_sections_for_process_mock.side_effect = _process_mock

        # Setup
        deployment_config = {
            "processes": [
                {"name": "process-1", "is_cronjob": False},
                {"name": "process-2", "is_cronjob": False},
                {"name": "cronjob-1", "is_cronjob": True},
                {"name": "cronjob-2", "is_cronjob": True},
            ]
        }

        # Test
        yaml_output = k8s_builders.build_yaml(deployment_config, "/path/to/templates", "tag")

        # Assertions
        self.assertEqual(
            yaml_output,
            """---
hpa: process-1
---
process: process-1
---
hpa: process-2
---
process: process-2
---
cronjob: cronjob-1
---
cronjob: cronjob-2""",
        )

    def _create_template_validator(self, expected: dict, return_value: dict):
        """A test helper validating the arguments passed to a template."""

        def template_validator(parameters):
            self.assertEqual(parameters, expected)
            return return_value

        return template_validator

    @patch("nestor_api.lib.k8s.builders.set_namespace", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_environment_variables", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_probes", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_command", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_resources", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_node_selector", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_anti_affinity", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_replicas", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_secret", autospec=True)
    @patch("nestor_api.lib.k8s.builders.yaml_lib.parse_yaml", autospec=True)
    @patch("nestor_api.lib.k8s.builders.time.time", autospec=True)
    def test_get_sections_for_process(
        self,
        time_mock,
        parse_yaml_mock,
        set_secret_mock,
        set_replicas_mock,
        set_anti_affinity_mock,
        set_node_selector_mock,
        set_resources_mock,
        set_command_mock,
        set_probes_mock,
        set_environment_variables_mock,
        set_namespace_mock,
    ):
        """Should correctly build the sections for the given process."""
        # Mocks
        time_mock.return_value = 123456
        parse_yaml_mock.side_effect = lambda x: x
        set_replicas_mock.return_value = None
        set_namespace_mock.return_value = None

        # Setup
        process = {"name": "my-process"}
        deployment_config = {
            "app": "my-app",
            "project": "my-project",
            "docker": {"registry": {"organization": "my-organization"}},
        }
        tag_to_deploy = "1.0.0-sha-1ab23cd"
        templates = {
            "deployment": self._create_template_validator(
                expected={
                    "app": "my-app",
                    "name": "my-app----my-process",
                    "image": "my-organization/my-app:1.0.0-sha-1ab23cd",
                    "process": "my-process",
                    "project": "my-project",
                },
                return_value={"spec": {"template": {"metadata": {}, "spec": {"containers": [{}]}}}},
            )
        }

        # Test
        sections = k8s_builders.get_sections_for_process(
            process, deployment_config, tag_to_deploy, templates
        )

        # Assertions
        self.assertEqual(sections, ["---", k8s_fixtures.PROCESS_SPEC_EXPECTED_OUTPUT])

        set_secret_mock.assert_called_once()
        set_replicas_mock.assert_called_once()
        set_anti_affinity_mock.assert_called_once()
        set_node_selector_mock.assert_called_once()
        set_resources_mock.assert_called_once()
        set_command_mock.assert_called_once()
        set_probes_mock.assert_called_once()
        set_environment_variables_mock.assert_called_once()
        set_namespace_mock.assert_called_once()

    @patch("nestor_api.lib.k8s.builders.set_namespace", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_environment_variables", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_probes", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_command", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_resources", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_node_selector", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_anti_affinity", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_replicas", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_secret", autospec=True)
    @patch("nestor_api.lib.k8s.builders.yaml_lib.parse_yaml", autospec=True)
    @patch("nestor_api.lib.k8s.builders.time.time", autospec=True)
    def test_get_sections_for_process_with_hpa_and_namespace(
        self,
        time_mock,
        parse_yaml_mock,
        set_secret_mock,
        set_replicas_mock,
        set_anti_affinity_mock,
        set_node_selector_mock,
        set_resources_mock,
        set_command_mock,
        set_probes_mock,
        set_environment_variables_mock,
        set_namespace_mock,
    ):
        """Should build the sections with the configured hpa and namespace."""
        # Mocks
        time_mock.return_value = 123456
        parse_yaml_mock.side_effect = lambda x: x
        set_replicas_mock.return_value = {"template": "hpa"}
        set_namespace_mock.return_value = {"template": "namespace"}

        # Setup
        process = {"name": "my-process"}
        deployment_config = {
            "app": "my-app",
            "project": "my-project",
            "docker": {"registry": {"organization": "my-organization"}},
        }
        tag_to_deploy = "1.0.0-sha-1ab23cd"
        templates = {
            "deployment": self._create_template_validator(
                expected={
                    "app": "my-app",
                    "name": "my-app----my-process",
                    "image": "my-organization/my-app:1.0.0-sha-1ab23cd",
                    "process": "my-process",
                    "project": "my-project",
                },
                return_value={"spec": {"template": {"metadata": {}, "spec": {"containers": [{}]}}}},
            )
        }

        # Test
        sections = k8s_builders.get_sections_for_process(
            process, deployment_config, tag_to_deploy, templates
        )

        # Assertions
        self.assertEqual(
            sections,
            [
                "---",
                "template: namespace\n",
                "---",
                "template: hpa\n",
                "---",
                k8s_fixtures.PROCESS_SPEC_EXPECTED_OUTPUT,
            ],
        )

        set_secret_mock.assert_called_once()
        set_replicas_mock.assert_called_once()
        set_anti_affinity_mock.assert_called_once()
        set_node_selector_mock.assert_called_once()
        set_resources_mock.assert_called_once()
        set_command_mock.assert_called_once()
        set_probes_mock.assert_called_once()
        set_environment_variables_mock.assert_called_once()
        set_namespace_mock.assert_called_once()

    @patch("nestor_api.lib.k8s.builders.set_namespace", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_environment_variables", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_probes", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_command", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_resources", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_node_selector", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_anti_affinity", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_replicas", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_secret", autospec=True)
    @patch("nestor_api.lib.k8s.builders.yaml_lib.parse_yaml", autospec=True)
    @patch("nestor_api.lib.k8s.builders.time.time", autospec=True)
    def test_get_sections_for_process_with_web_process(
        self,
        time_mock,
        parse_yaml_mock,
        set_secret_mock,
        set_replicas_mock,
        set_anti_affinity_mock,
        set_node_selector_mock,
        set_resources_mock,
        set_command_mock,
        set_probes_mock,
        set_environment_variables_mock,
        set_namespace_mock,
    ):
        """Should correctly build the sections for the web process."""
        # Mocks
        time_mock.return_value = 123456
        parse_yaml_mock.side_effect = lambda x: x
        set_replicas_mock.return_value = None
        set_namespace_mock.return_value = None

        # Setup
        process = {"name": "web"}
        deployment_config = {
            "app": "my-app",
            "project": "my-project",
            "docker": {"registry": {"organization": "my-organization"}},
        }
        tag_to_deploy = "1.0.0-sha-1ab23cd"
        templates = {
            "deployment": self._create_template_validator(
                expected={
                    "app": "my-app",
                    "name": "my-app----web",
                    "image": "my-organization/my-app:1.0.0-sha-1ab23cd",
                    "process": "web",
                    "project": "my-project",
                },
                return_value={"spec": {"template": {"metadata": {}, "spec": {"containers": [{}]}}}},
            ),
            "service": self._create_template_validator(
                expected={
                    "app": "my-app",
                    "name": "my-app",
                    "image": "my-organization/my-app:1.0.0-sha-1ab23cd",
                    "target_port": 8080,
                },
                return_value={"template": "web"},
            ),
        }

        # Test
        sections = k8s_builders.get_sections_for_process(
            process, deployment_config, tag_to_deploy, templates
        )

        # Assertions
        self.assertEqual(
            sections, ["---", "template: web\n", "---", k8s_fixtures.PROCESS_SPEC_EXPECTED_OUTPUT],
        )

        set_secret_mock.assert_called_once()
        set_replicas_mock.assert_called_once()
        set_anti_affinity_mock.assert_called_once()
        set_node_selector_mock.assert_called_once()
        set_resources_mock.assert_called_once()
        set_command_mock.assert_called_once()
        set_probes_mock.assert_called_once()
        set_environment_variables_mock.assert_called_once()
        set_namespace_mock.assert_called_once()

    @patch("nestor_api.lib.k8s.builders.set_namespace", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_node_selector", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_environment_variables", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_command", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_resources", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_secret", autospec=True)
    @patch("nestor_api.lib.k8s.builders.yaml_lib.parse_yaml", autospec=True)
    def test_get_sections_for_cronjob(
        self,
        parse_yaml_mock,
        set_secret_mock,
        set_resources_mock,
        set_command_mock,
        set_environment_variables_mock,
        set_node_selector_mock,
        set_namespace_mock,
    ):
        """Should correctly build the sections for cronjob."""
        # Mocks
        parse_yaml_mock.side_effect = lambda x: x
        set_namespace_mock.return_value = None

        # Setup
        cronjob = {"name": "my-cron"}
        deployment_config = {
            "app": "my-app",
            "project": "my-project",
            "docker": {"registry": {"organization": "my-organization"}},
            "crons": {"my-cron": {"schedule": "*/30 * * * *", "concurrency_policy": "Forbid"}},
        }
        tag_to_deploy = "1.0.0-sha-1ab23cd"
        templates = {
            "cronjob": self._create_template_validator(
                expected={
                    "app": "my-app",
                    "name": "my-app----my-cron",
                    "image": "my-organization/my-app:1.0.0-sha-1ab23cd",
                    "process": "my-cron",
                    "project": "my-project",
                },
                return_value={"spec": {"jobTemplate": {}}},
            ),
            "job": self._create_template_validator(
                expected={
                    "app": "my-app",
                    "name": "my-app----my-cron",
                    "image": "my-organization/my-app:1.0.0-sha-1ab23cd",
                    "process": "my-cron",
                    "project": "my-project",
                },
                return_value={"spec": {"job": "spec"}},
            ),
        }

        # Test
        sections = k8s_builders.get_sections_for_cronjob(
            cronjob, deployment_config, tag_to_deploy, templates
        )

        # Assertions
        self.assertEqual(
            sections, ["---", k8s_fixtures.CRONJOB_SPEC_EXPECTED_OUTPUT],
        )

        set_secret_mock.assert_called_once()
        set_resources_mock.assert_called_once()
        set_command_mock.assert_called_once()
        set_environment_variables_mock.assert_called_once()
        set_node_selector_mock.assert_called_once()
        set_namespace_mock.assert_called_once()

    @patch("nestor_api.lib.k8s.builders.set_namespace", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_node_selector", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_environment_variables", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_command", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_resources", autospec=True)
    @patch("nestor_api.lib.k8s.builders.set_secret", autospec=True)
    @patch("nestor_api.lib.k8s.builders.yaml_lib.parse_yaml", autospec=True)
    def test_get_sections_for_cronjob_with_namespace(
        self,
        parse_yaml_mock,
        set_secret_mock,
        set_resources_mock,
        set_command_mock,
        set_environment_variables_mock,
        set_node_selector_mock,
        set_namespace_mock,
    ):
        """Should build the sections with the configured namespace."""
        # Mocks
        parse_yaml_mock.side_effect = lambda x: x
        set_namespace_mock.return_value = {"template": "namespace"}

        # Setup
        cronjob = {"name": "my-cron"}
        deployment_config = {
            "app": "my-app",
            "project": "my-project",
            "docker": {"registry": {"organization": "my-organization"}},
            "crons": {"my-cron": {"schedule": "*/30 * * * *", "concurrency_policy": "Forbid"}},
        }
        tag_to_deploy = "1.0.0-sha-1ab23cd"
        templates = {
            "cronjob": self._create_template_validator(
                expected={
                    "app": "my-app",
                    "name": "my-app----my-cron",
                    "image": "my-organization/my-app:1.0.0-sha-1ab23cd",
                    "process": "my-cron",
                    "project": "my-project",
                },
                return_value={"spec": {"jobTemplate": {}}},
            ),
            "job": self._create_template_validator(
                expected={
                    "app": "my-app",
                    "name": "my-app----my-cron",
                    "image": "my-organization/my-app:1.0.0-sha-1ab23cd",
                    "process": "my-cron",
                    "project": "my-project",
                },
                return_value={"spec": {"job": "spec"}},
            ),
        }

        # Test
        sections = k8s_builders.get_sections_for_cronjob(
            cronjob, deployment_config, tag_to_deploy, templates
        )

        # Assertions
        self.assertEqual(
            sections,
            ["---", "template: namespace\n", "---", k8s_fixtures.CRONJOB_SPEC_EXPECTED_OUTPUT],
        )

        set_secret_mock.assert_called_once()
        set_resources_mock.assert_called_once()
        set_command_mock.assert_called_once()
        set_environment_variables_mock.assert_called_once()
        set_node_selector_mock.assert_called_once()
        set_namespace_mock.assert_called_once()
