from kubernetes import client, config
import json

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
            "app": "flask-app-label"
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

# Define the namespace and service name
namespace = expected_values["metadata"]["namespace"]
service_name = expected_values["metadata"]["name"]

# Get the service details
try:
    service = v1.read_namespaced_service(name=service_name, namespace=namespace)
    print(f"Service {service_name} is properly created.")
    
    # Save service details to a file
    with open('service_details.json', 'w') as f:
        json.dump(service.to_dict(), f, indent=4, default=str)
    
    # Load service details from the file
    with open('service_details.json', 'r') as f:
        service_details = json.load(f)
    
    # Extract relevant information
    extracted_info = {
        "apiVersion": service_details.get('api_version'),
        "kind": service_details.get('kind'),
        "metadata": {
            "name": service_details['metadata'].get('name'),
            "namespace": service_details['metadata'].get('namespace'),
            "annotations": service_details['metadata'].get('annotations')
        },
        "spec": {
            "selector": service_details['spec'].get('selector'),
            "ports": [
                {
                    "protocol": service_details['spec']['ports'][0].get('protocol'),
                    "port": service_details['spec']['ports'][0].get('port'),
                    "targetPort": service_details['spec']['ports'][0].get('target_port')
                }
            ]
        }
    }
    
    # Verify the service details
    def verify_service_details(extracted_info, expected_values):
        mismatches = []
        if extracted_info['apiVersion'] != expected_values['apiVersion']:
            mismatches.append(f"Expected apiVersion: {expected_values['apiVersion']}, but got: {extracted_info['apiVersion']}")
        if extracted_info['kind'] != expected_values['kind']:
            mismatches.append(f"Expected kind: {expected_values['kind']}, but got: {extracted_info['kind']}")
        if extracted_info['metadata']['name'] != expected_values['metadata']['name']:
            mismatches.append(f"Expected metadata.name: {expected_values['metadata']['name']}, but got: {extracted_info['metadata']['name']}")
        if extracted_info['metadata']['namespace'] != expected_values['metadata']['namespace']:
            mismatches.append(f"Expected metadata.namespace: {expected_values['metadata']['namespace']}, but got: {extracted_info['metadata']['namespace']}")
        if extracted_info['spec']['selector']['app'] != expected_values['spec']['selector']['app']:
            mismatches.append(f"Expected spec.selector.app: {expected_values['spec']['selector']['app']}, but got: {extracted_info['spec']['selector']['app']}")
        if extracted_info['spec']['ports'][0]['targetPort'] != expected_values['spec']['ports'][0]['targetPort']:
            mismatches.append(f"Expected spec.ports[0].targetPort: {expected_values['spec']['ports'][0]['targetPort']}, but got: {extracted_info['spec']['ports'][0]['targetPort']}")
        return mismatches
    
    mismatches = verify_service_details(extracted_info, expected_values)
    if not mismatches:
        print("Service details match the expected values.")
    else:
        print("Service details do not match the expected values.")
        for mismatch in mismatches:
            print(mismatch)
    
except client.exceptions.ApiException as e:
    if e.status == 404:
        print(f"Service {service_name} not found in namespace {namespace}.")
    else:
        print(f"An error occurred: {e}")
