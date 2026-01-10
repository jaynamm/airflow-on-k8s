# airflow-on-k8s
airflow cluster on k8s, kind cluster

## Setup

Before creating the kind cluster, you must configure the host paths in `kind-cluster-config.yaml`:

1. Open `kind-cluster-config.yaml`
2. Replace all instances of `<ABSOLUTE_PATH_TO_PROJECT>` with the full absolute path to this project directory
   - macOS example: `/Users/yourname/workspace/airflow-on-k8s`
   - Linux example: `/home/yourname/workspace/airflow-on-k8s`

Then create the cluster:
```bash
kind create cluster --config kind-cluster-config.yaml
```
