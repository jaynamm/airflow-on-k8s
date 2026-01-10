# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a local development environment for running Apache Airflow on Kubernetes using kind (Kubernetes in Docker). The project uses the official Apache Airflow Helm chart (version 1.18.0) to deploy Airflow 3.0.2 on a local kind cluster.

## Architecture

### Cluster Setup
- **kind cluster**: Multi-node cluster with 1 control-plane and 2 worker nodes
- **Port mapping**: Control-plane exposes port 30080 for NodePort access to Airflow UI
- **Configuration file**: `kind-cluster-config.yaml` defines the cluster topology

### Airflow Deployment
- **Helm chart**: Official Apache Airflow chart from `airflow/` directory
- **Executor**: Configured to use `KubernetesExecutor` (see `airflow/values.yaml:376`)
- **Version**: Airflow 3.0.2 with PostgreSQL 13.2.24 as the metadata database
- **DAG sync**: Uses git-sync sidecar pattern with DAGs expected in `apps/dags` subdirectory (configurable at `airflow/values.yaml:2974`)

### Directory Structure
- `/airflow/`: Official Airflow Helm chart with customized values
  - `/templates/`: Kubernetes manifests for all Airflow components (scheduler, workers, api-server, etc.)
  - `/charts/postgresql/`: PostgreSQL subchart for metadata database
  - `values.yaml`: Helm chart configuration (main customization point)
- `/dags/`: Local DAGs directory (currently empty)
- `/apps/`: Application directory (currently empty, but referenced in git-sync config)
- `kind-cluster-config.yaml`: kind cluster configuration

### Key Components (from Helm templates)
- **Scheduler** (`templates/scheduler/`): Orchestrates task execution
- **Workers** (`templates/workers/`): Execute tasks when using CeleryExecutor (not active with KubernetesExecutor)
- **API Server** (`templates/api-server/`): REST API for Airflow 3.0+
- **DAG Processor** (`templates/dag-processor/`): Processes DAG files
- **PgBouncer** (`templates/pgbouncer/`): Connection pooling for PostgreSQL
- **Redis** (`templates/redis/`): Message broker for CeleryExecutor (not active with current config)

## Common Commands

### Cluster Management
```bash
# Create kind cluster
kind create cluster --config kind-cluster-config.yaml

# Delete kind cluster
kind delete cluster

# View cluster info
kubectl cluster-info
kubectl get nodes
```

### Helm Operations
```bash
# Install Airflow (from repository root)
helm install airflow ./airflow

# Upgrade Airflow deployment
helm upgrade airflow ./airflow

# Uninstall Airflow
helm uninstall airflow

# View values
helm get values airflow

# Dry-run to test configuration
helm install airflow ./airflow --dry-run --debug
```

### Accessing Airflow UI
```bash
# Port-forward to api-server (Airflow 3.0+)
kubectl port-forward svc/airflow-api-server 8080:8080

# Or access via NodePort on control-plane (if configured)
# http://localhost:30080
```

### DAG Development
```bash
# View DAGs
kubectl exec -it deployment/airflow-scheduler -- airflow dags list

# Trigger a DAG manually
kubectl exec -it deployment/airflow-scheduler -- airflow dags trigger <dag_id>

# View task logs
kubectl logs deployment/airflow-scheduler
```

### Debugging
```bash
# Check pod status
kubectl get pods

# View logs for specific component
kubectl logs deployment/airflow-scheduler
kubectl logs deployment/airflow-api-server

# Describe pod for troubleshooting
kubectl describe pod <pod-name>

# Execute into scheduler for debugging
kubectl exec -it deployment/airflow-scheduler -- /bin/bash
```

## Important Configuration Notes

### Executor Configuration
The deployment uses `KubernetesExecutor` (configured in `airflow/values.yaml:376`). This means:
- Each task runs in its own Kubernetes pod
- No Celery workers are deployed
- Redis is not required or used
- Task pods are created dynamically by the scheduler

To switch executors, modify the `executor` value in `airflow/values.yaml` and be aware of the implications:
- `LocalExecutor`: All tasks run in scheduler pod (not suitable for production)
- `CeleryExecutor`: Requires Redis and worker deployment
- `CeleryKubernetesExecutor`: Hybrid mode (Airflow 2.x only)

### DAG Synchronization
The Helm chart is configured to use git-sync for DAG synchronization:
- Configured at `airflow/values.yaml` under `dags.gitSync`
- Default subpath: `apps/dags` (line 2974)
- For local development, you may want to disable git-sync and use persistence or a local volume mount instead

### Database
PostgreSQL is deployed as a subchart (`airflow/charts/postgresql/`) with the following configuration:
- Bitnami PostgreSQL chart version 13.2.24
- Used as Airflow metadata database
- PgBouncer is available for connection pooling

## Development Workflow

1. **Start cluster**: Create kind cluster using `kind-cluster-config.yaml`
2. **Deploy Airflow**: Install Helm chart from `./airflow` directory
3. **Access UI**: Port-forward to api-server service or use NodePort
4. **Deploy DAGs**:
   - Either configure git-sync to pull from repository
   - Or use persistence and copy DAGs to PVC
   - Or mount local directory (requires values.yaml modification)
5. **Monitor**: Use kubectl commands to check pod status and logs
6. **Iterate**: Make changes to values.yaml and run `helm upgrade`

## File Modifications

When modifying Airflow configuration:
- Primary customization point: `airflow/values.yaml`
- For template changes: Edit files in `airflow/templates/`
- For PostgreSQL config: Edit `airflow/charts/postgresql/values.yaml`

The values.yaml file is extensive (~3000+ lines) and controls all aspects of the deployment including:
- Image versions and repositories
- Resource limits and requests
- Security contexts
- Environment variables
- Service configurations
- Storage and persistence
