from kubernetes import client, config, watch
import time

# Load kubeconfig
config.load_kube_config()

# Create API client
v1 = client.CoreV1Api()

# Define the namespace
namespace = 'flask-app-namespace'

# Get the list of all pods
pods = v1.list_namespaced_pod(namespace=namespace).items
pod_names = [pod.metadata.name for pod in pods]

if not pod_names:
    print("No pods found in the namespace.")
else:
    # Delete the first pod
    pod_to_delete = pod_names[0]
    v1.delete_namespaced_pod(name=pod_to_delete, namespace=namespace)
    print(f"Deleted pod {pod_to_delete}")

    # Wait for 60 seconds
    time.sleep(60)

    # Get the list of all pods again
    new_pods = v1.list_namespaced_pod(namespace=namespace).items
    new_pod_names = [pod.metadata.name for pod in new_pods]

    # Check if the deleted pod name is not present and a new pod is created
    if pod_to_delete not in new_pod_names:
        print(f"Pod {pod_to_delete} is not present anymore.")
        new_pod_created = any(pod_name not in pod_names for pod_name in new_pod_names)
        if new_pod_created:
            print("A new pod has been created as part of the self-healing feature.")
        else:
            print("No new pod has been created.")
    else:
        print(f"Pod {pod_to_delete} is still present.")
