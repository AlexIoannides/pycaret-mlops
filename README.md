# Build with PyCaret, Deploy to Kubernetes with FastAPI and Bodywork

<div align="center">
<img src="https://bodywork-media.s3.eu-west-2.amazonaws.com/pycaret-mlops/pycaret_with_bodywork.png"/>
</div>

This short post follows-on from [Moez Ali's tutorial](https://towardsdatascience.com/build-with-pycaret-deploy-with-fastapi-333c710dc786) on how to train a model with [PyCaret](https://pycaret.org) and serve predictions using [FastAPI](https://fastapi.tiangolo.com). We're going to take this one step further and add some MLOps magic by deploying the FastAPI prediction service to a [Kubernetes](https://kubernetes.io) cluster using [Bodywork](https://github.com/bodywork-ml/bodywork-core).

[Bodywork](https://github.com/bodywork-ml/bodywork-core) is a Python package that exposes a CLI for configuring Kubernetes to orchestrate your ML pipelines and deploy your prediction services, without having to build Docker images or learn how to configure Kubernetes.

## 👉🏼 Create a GitHub Repo for the Project

In the [original post](https://towardsdatascience.com/build-with-pycaret-deploy-with-fastapi-333c710dc786) Moez Ali guides us through the process of training and saving a model using PyCaret and then demonstrates how to use FastAPI to develop a Python module that serves predictions from the model. If you work through the post you should end-up with a project directory that looks something like this,

```text
|-- pycaret-mlops/
    |-- diamond-pipeline.pkl
    |-- serve_predictions.py
```

Create a GitHub repo and commit **all** of these file to it. We've worked through this for you and you can find our project repo at [https://github.com/AlexIoannides/pycaret-mlops](https://github.com/AlexIoannides/pycaret-mlops), where we've reproduced all of the training code in the [train_model.ipynb](https://github.com/AlexIoannides/pycaret-mlops/blob/master/train_model.ipynb) notebook, to make life simpler.

## 👉🏼 Install Bodywork

[Bodywork](https://github.com/bodywork-ml/bodywork-core) is a Python package that exposes a CLI for configuring Kubernetes to orchestrate your ML pipelines and deploy your prediction services. Install it using Pip,

```text
$ pip install bodywork
```

## 👉🏼 Configure the Kubernetes Deployment

Create a file called `bodywork.yaml` and add the following,

```yaml
version: "1.1"
pipeline:
  name: pycaret-diamond-prices
  docker_image: bodyworkml/bodywork-core:3.0
  DAG: serve-predictions
stages:
  serve-predictions:
    executable_module_path: serve_predictions.py
    requirements:
      - fastapi==0.68.1
      - uvicorn==0.15.0
      - pycaret==2.3.3
    cpu_request: 1.0
    memory_request_mb: 500
    service:
      max_startup_time_seconds: 600
      replicas: 1
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
$ minikube start --kubernetes-version=v1.22.6 --addons=ingress --cpus=2 --memory=4g
```

## 👉🏼 Deploy the Prediction Service to Kubernetes

<div align="center">
<img src="https://bodywork-media.s3.eu-west-2.amazonaws.com/pycaret-mlops/deploy_pycaret_service.png"/>
</div>

```text
$ bodywork create deployment https://github.com/AlexIoannides/pycaret-mlops.git
```

This will stream the logs to your terminal so you can keep track of progress.

## 👉🏼 Test the Service

First create a route to your cluster,

```text
$ minikube kubectl -- -n ingress-nginx port-forward service/ingress-nginx-controller 8080:80
```

And then use the [test_prediction_service.ipynb](https://github.com/AlexIoannides/pycaret-mlops/blob/master/train_model.ipynb) notebook to test the service using Python.

![jupyter](https://bodywork-media.s3.eu-west-2.amazonaws.com/pycaret-mlops/test_service.png)

## 👉🏼 Where to go from Here

- [Continuous training pipelines with Bodywork](https://bodywork.readthedocs.io/en/latest/quickstart_ml_pipeline/)
- [Bodywork + MLflow](https://github.com/bodywork-ml/bodywork-pipeline-with-mlflow)
- [Best practices for engineering ML pipelines](https://github.com/bodywork-ml/ml-pipeline-engineering)
