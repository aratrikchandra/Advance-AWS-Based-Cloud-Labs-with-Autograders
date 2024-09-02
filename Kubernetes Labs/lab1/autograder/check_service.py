import yaml
from kubernetes import client, config

# Load kubeconfig
config.load_kube_config()

# Create API client
v1 = client.CoreV1Api()

# Define the expected values
expected_values = {
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
        "name": "flask-app-service",
        "namespace": "flask-app-namespace"
    },
    "spec": {
        "selector": {
            "app": "flask-app"
        },
        "ports": [
            {
                "protocol": "TCP",
                "port": 8000,
                "targetPort": 5000
            }
        ]
    }
}

# Load the service.yaml file
with open('service.yaml', 'r') as file:
    service_yaml = yaml.safe_load(file)

# Verify the fields and values in service.yaml
def verify_service_yaml(service_yaml, expected_values):
    for key, value in expected_values.items():
        if key not in service_yaml or service_yaml[key] != value:
            return False
    return True

if verify_service_yaml(service_yaml, expected_values):
    print("service.yaml file is correctly filled.")
else:
    print("service.yaml file is not correctly filled.")
    exit(0)

# Define the namespace and service name
namespace = expected_values["metadata"]["namespace"]
service_name = expected_values["metadata"]["name"]

# Get the service details
try:
    service = v1.read_namespaced_service(name=service_name, namespace=namespace)
    print(f"Service {service_name} is properly created.")
    # print(f"Service Details:\n{service}")
except client.exceptions.ApiException as e:
    if e.status == 404:
        print(f"Service {service_name} not found in namespace {namespace}.")
    else:
        print(f"An error occurred: {e}")
