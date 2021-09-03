# Build with PyCaret, Deploy to Kubernetes with FastAPI and Bodywork

<div align="center">
<img src="https://bodywork-media.s3.eu-west-2.amazonaws.com/pycaret-mlops/pycaret_with_bodywork.png"/>
</div>

This short post follows-on from [Moez Ali's tutorial](https://towardsdatascience.com/build-with-pycaret-deploy-with-fastapi-333c710dc786) on how to train a model with [PyCaret](https://pycaret.org) and serve predictions using [FastAPI](https://fastapi.tiangolo.com). We're going to take this one step further and add some MLOps magic by deploying the FastAPI prediction service to a [Kubernetes](https://kubernetes.io) cluster using [Bodywork](https://github.com/bodywork-ml/bodywork-core).

[Bodywork](https://github.com/bodywork-ml/bodywork-core) is a Python package that exposes a CLI for configuring Kubernetes to orchestrate your ML pipelines and deploy your prediction services, without having to build Docker images or learn how to configure Kubernetes.

## 👉🏼 Create a GitHub Repo for the Project

In the [original post](https://towardsdatascience.com/build-with-pycaret-deploy-with-fastapi-333c710dc786) Moez Ali guides us through the process of training and saving a model using PyCaret and then demonstrates how to use FastAPI to develop a Python module that serves predictions from the model. If you work through the post you should end-up with a project directory that looks something like this,

```text
- pycaret-mlops/
|-- diamond-pipeline.pkl
|-- serve_predictions.py
```

Create a GitHub repo and commit **all** of these file to it. We've worked through this for you and you can find our project repo at [https://github.com/AlexIoannides/pycaret-mlops](https://github.com/AlexIoannides/pycaret-mlops), where we've reproduced all of the training code in the [train_model.ipynb](https://github.com/AlexIoannides/pycaret-mlops/blob/master/train_model.ipynb) notebook, to make life simpler.

## 👉🏼 Install Bodywork

[Bodywork](https://github.com/bodywork-ml/bodywork-core) is a Python package that exposes a CLI for configuring Kubernetes to orchestrate your ML pipelines and deploy your prediction services. Install it using Pip,

```text
$ pip install bodywork==2.1.7
```

## 👉🏼 Configure the Kubernetes Deployment

Create a file called `bodywork.yaml` and add the following,

```yaml
version: "1.0"
project:
  name: pycaret-diamond-prices
  docker_image: bodyworkml/bodywork-core:2.1.7
  DAG: serve-predictions
stages:
  serve-predictions:
    executable_module_path: serve_predictions.py
    requirements:
      - fastapi==0.68.1
      - pycaret[full]==2.3.3
      - uvicorn==0.15.0
    cpu_request: 0.5
    memory_request_mb: 250
    service:
      max_startup_time_seconds: 120
      replicas: 2
      port: 8000
      ingress: true
logging:
  log_level: INFO
```

This requests that two containers (or replicas) running the FastAPI prediction service are created, with automatic load-balancing between them - nice! For more info on what this all these configuration parameters mean, head to the [Bodywork docs](https://bodywork.readthedocs.io/en/latest/).

Commit this file to your Git repo and push to GitHub,

```text
$ git add bodywork.yaml
$ git commit -m "Add bodywork deployment config"
$ git push origin master
```

## 👉🏼 Start a Kubernetes Cluster

If you don't have a Kubernetes cluster handy, then [download Minikube](https://minikube.sigs.k8s.io/docs/start/) so you can test locally. Then, start and configure a cluster as follows,

```text
$ minikube start --kubernetes-version=v1.17.17
$ minikube addons enable ingress-dns
```

You'll need the IP address of your local cluster for testing the prediction service, which you can get with,

```text
$ minikube profile list

|----------|-----------|---------|--------------|------|----------|---------|-------|
| Profile  | VM Driver | Runtime |      IP      | Port | Version  | Status  | Nodes |
|----------|-----------|---------|--------------|------|----------|---------|-------|
| minikube | hyperkit  | docker  | 192.168.64.6 | 8443 | v1.17.17 | Stopped |     1 |
|----------|-----------|---------|--------------|------|----------|---------|-------|
```

## 👉🏼 Deploy the Prediction Service to Kubernetes

<div align="center">
<img src="https://bodywork-media.s3.eu-west-2.amazonaws.com/pycaret-mlops/deploy_pycaret_service.png"/>
</div>

Create a dedicated and secure space on your cluster for the deployment,

```text
$ bodywork setup-namespace pipelines
```

Then deploy!

```text
$ bodywork deployment create \
    --namespace=pipelines \
    --name=initial-deployment \
    --git-repo-url=https://github.com/AlexIoannides/pycaret-mlops.git \
    --git-repo-branch=master \
    --local-workflow-controller
```

This will stream the logs to your terminal so you can keep track of progress.

## 👉🏼 Test the Service

Use the [test_prediction_service.ipynb](https://github.com/AlexIoannides/pycaret-mlops/blob/master/train_model.ipynb) notebook to test the service using Python.

![jupyter](https://bodywork-media.s3.eu-west-2.amazonaws.com/pycaret-mlops/test_service.png)

## 👉🏼 Where to go from Here

- [Continuous training pipelines with Bodywork](https://bodywork.readthedocs.io/en/latest/quickstart_ml_pipeline/)
- [Bodywork + MLflow](https://github.com/bodywork-ml/bodywork-pipeline-with-mlflow)
- [Best practices for engineering ML pipelines](https://github.com/bodywork-ml/ml-pipeline-engineering)
