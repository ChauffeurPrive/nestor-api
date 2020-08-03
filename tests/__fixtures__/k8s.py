"""Kubernetes fixtures"""

# podAntiAffinity (hostname)
anti_affinity_node = {
    "podAntiAffinity": {
        "preferredDuringSchedulingIgnoredDuringExecution": [
            {
                "weight": 1,
                "podAffinityTerm": {
                    "labelSelector": {
                        "matchExpressions": [
                            {"key": "app", "operator": "In", "values": ["app-name"]},
                            {"key": "process", "operator": "In", "values": ["proc-name"]},
                        ]
                    },
                    "topologyKey": "kubernetes.io/hostname",
                },
            }
        ]
    }
}

# podAntiAffinity (zone)
anti_affinity_zone = {
    "podAntiAffinity": {
        "preferredDuringSchedulingIgnoredDuringExecution": [
            {
                "weight": 1,
                "podAffinityTerm": {
                    "labelSelector": {
                        "matchExpressions": [
                            {"key": "app", "operator": "In", "values": ["app-name"]},
                            {"key": "process", "operator": "In", "values": ["proc-name"]},
                        ]
                    },
                    "topologyKey": "failure-domain.beta.kubernetes.io/zone",
                },
            }
        ]
    }
}

# namespace
namespace = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "namespace"}}

# hpa
hpa = {
    "apiVersion": "autoscaling/v1",
    "kind": "HorizontalPodAutoscaler",
    "metadata": {"name": "app----web", "labels": {"app": "app", "process": "web"}},
    "spec": {
        "scaleTargetRef": {"apiVersion": "apps/v1", "kind": "Deployment", "name": "app----web"},
        "minReplicas": 1,
        "maxReplicas": 10,
        "targetCPUUtilizationPercentage": 75,
    },
}

# probes
probes = {
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
}

# get_sections_for_process
PROCESS_SPEC_EXPECTED_OUTPUT = """spec:
  template:
    metadata:
      annotations:
        date: '123456000'
    spec:
      containers:
      - ports:
        - containerPort: 8080
"""

# get_sections_for_cronjob
CRONJOB_SPEC_EXPECTED_OUTPUT = """spec:
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      job: spec
  schedule: '*/30 * * * *'
"""
