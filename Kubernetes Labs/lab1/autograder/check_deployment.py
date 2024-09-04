from kubernetes import client, config
import json

# Load kubeconfig
config.load_kube_config()

# Create API client
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

# Define the expected values for deployment.yaml
expected_deployment_values = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": "flask-app-deployment",
        "namespace": "flask-app-namespace"
    },
    "spec": {
        "replicas": 3,
        "template": {
            "metadata": {
                "labels": {
                    "app": "flask-app-label"
                }
            },
            "spec": {
                "containers": [
                    {
                        "name": "flask-app",
                        "image": "aratrik99/flask_app:latest",
                        "ports": [
                            {
                                "containerPort": 5000
                            }
                        ]
                    }
                ]
            }
        }
    }
}

# Define the namespace and deployment name
namespace = expected_deployment_values["metadata"]["namespace"]
deployment_name = expected_deployment_values["metadata"]["name"]

# Get the deployment details
try:
    deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    print(f"Deployment {deployment_name} is properly created.")
    
    # Save deployment details to a file
    with open('deployment_details.json', 'w') as f:
        json.dump(deployment.to_dict(), f, indent=4, default=str)
    
    # Load deployment details from the file
    with open('deployment_details.json', 'r') as f:
        deployment_details = json.load(f)
    
    # Extract relevant information
    extracted_info = {
        "apiVersion": deployment_details.get('api_version'),
        "kind": deployment_details.get('kind'),
        "metadata": {
            "name": deployment_details['metadata'].get('name'),
            "namespace": deployment_details['metadata'].get('namespace'),
            "annotations": deployment_details['metadata'].get('annotations')
        },
        "spec": {
            "replicas": deployment_details['spec'].get('replicas'),
            "template": {
                "metadata": deployment_details['spec']['template']['metadata'].get('labels'),
                "spec": {
                    "containers": [
                        {
                            "name": deployment_details['spec']['template']['spec']['containers'][0].get('name'),
                            "image": deployment_details['spec']['template']['spec']['containers'][0].get('image'),
                            "ports": [
                                {
                                    "containerPort": deployment_details['spec']['template']['spec']['containers'][0]['ports'][0].get('containerPort')
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }

    # Parse the JSON string from the annotation
    last_applied_config_str = deployment_details['metadata']['annotations']['kubectl.kubernetes.io/last-applied-configuration']
    last_applied_config = json.loads(last_applied_config_str)
    
    # Debugging: Print the containerPort value from the last applied configuration
    container_port_applied = last_applied_config['spec']['template']['spec']['containers'][0]['ports'][0]['containerPort']
    # print(f"Extracted containerPort from last applied configuration: {container_port_applied}")
    
    # Verify the deployment details
    def verify_deployment_details(extracted_info, expected_deployment_values):
        mismatches = []
        if extracted_info['apiVersion'] != expected_deployment_values['apiVersion']:
            mismatches.append(f"Expected apiVersion: {expected_deployment_values['apiVersion']}, but got: {extracted_info['apiVersion']}")
        if extracted_info['kind'] != expected_deployment_values['kind']:
            mismatches.append(f"Expected kind: {expected_deployment_values['kind']}, but got: {extracted_info['kind']}")
        if extracted_info['metadata']['name'] != expected_deployment_values['metadata']['name']:
            mismatches.append(f"Expected metadata.name: {expected_deployment_values['metadata']['name']}, but got: {extracted_info['metadata']['name']}")
        if extracted_info['metadata']['namespace'] != expected_deployment_values['metadata']['namespace']:
            mismatches.append(f"Expected metadata.namespace: {expected_deployment_values['metadata']['namespace']}, but got: {extracted_info['metadata']['namespace']}")
        if extracted_info['spec']['replicas'] != expected_deployment_values['spec']['replicas']:
            mismatches.append(f"Expected spec.replicas: {expected_deployment_values['spec']['replicas']}, but got: {extracted_info['spec']['replicas']}")
        if extracted_info['spec']['template']['metadata']['app'] != expected_deployment_values['spec']['template']['metadata']['labels']['app']:
            mismatches.append(f"Expected spec.template.metadata.labels.app: {expected_deployment_values['spec']['template']['metadata']['labels']['app']}, but got: extracted_info['spec']['template']['metadata']['app']")
        if extracted_info['spec']['template']['spec']['containers'][0]['image'] != expected_deployment_values['spec']['template']['spec']['containers'][0]['image']:
            mismatches.append(f"Expected spec.template.spec.containers[0].image: {expected_deployment_values['spec']['template']['spec']['containers'][0]['image']}, but got: {extracted_info['spec']['template']['spec']['containers'][0]['image']}")
        if container_port_applied != expected_deployment_values['spec']['template']['spec']['containers'][0]['ports'][0]['containerPort']:
            mismatches.append(f"Expected spec.template.spec.containers[0].ports[0].containerPort: {expected_deployment_values['spec']['template']['spec']['containers'][0]['ports'][0]['containerPort']}, but got: {container_port_applied}")
        return mismatches
    
    mismatches = verify_deployment_details(extracted_info, expected_deployment_values)
    if not mismatches:
        print("Deployment details match the expected values.")
    else:
        print("Deployment details do not match the expected values.")
        for mismatch in mismatches:
            print(mismatch)
    
except client.exceptions.ApiException as e:
    if e.status == 404:
        print(f"Deployment {deployment_name} not found in namespace {namespace}.")
    else:
        print(f"An error occurred: {e}")
