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
