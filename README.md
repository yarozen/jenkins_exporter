# Jenkins Exporter

Jenkins Exporter for Prometheus written in Python3.

It collects and expose last build metrics (result, duration, timestamp) for every Repository & Branch from the provided Jenkins URL.

## Usage

    usage: jenkins_exporter.py [-h] [-p {1..65535}] [-v] JENKINS_URL

    Jenkins Exporter for Prometheus

    positional arguments:
    JENKINS_URL           Jenkins Server URL (e.g. http://jenkins:8080 or http://jenkins:8080/view/MYPRODUCT)

    optional arguments:
    -h, --help            show this help message and exit
    -p {1..65535}, --port {1..65535}
                            Jenkins Exporter listening port (Default is 9789)
    -v, --verbose         Increase output verbosity (DEBUG)

## Produced Metrics

|Metric|Description|Value|
|---|---|---|
|`jenkins_job_build_timestamp`|The time which the build was completed|epoch ms (milliseconds passed since 00:00:00 UTC on 1 January 1970)
|`jenkins_job_build_duration`|The time it took the build to complete| ms (millieconds)
|`jenkins_job_build_result`|Build result| <ul><li>FAILURE = 0</li><li>ABORTED = 0.5</li><li>UNSTABLE = 0.7</li><li>STABLE = 1</li><li>SUCCESS = 1</li></ul>

## Output Sample

    # HELP jenkins_job_build_timestamp 
    # TYPE jenkins_job_build_timestamp gauge
    jenkins_job_build_timestamp{branch="dev",build="1",repo="my_repo"} 1.611744014484e+012
    # HELP jenkins_job_build_duration 
    # TYPE jenkins_job_build_duration gauge
    jenkins_job_build_duration{branch="dev",build="1",repo="my_repo"} 507379.0
    # HELP jenkins_job_build_result 
    # TYPE jenkins_job_build_result gauge
    jenkins_job_build_result{branch="dev",build="1",repo="my_repo"} 1.0

## Running in Docker

    docker run -p 9789:9789 yarozen/jenkins_exporter -p 9789 http://jenkins:8081/view/MYPRODUCT

## Running in Kubernetes

The `jenkins_exporter_k8s_manifest.yaml` will deploy everything needed to collect your Jenkins metrics:

- Jenkins Exporter Deployment
- Jenkins Exporter Service
- Prometheus Deployment
- Prometheus ConfigMap containing prometheus.yaml to scrape from the Jenkins Exporter Service
- Prometheus Service
- Prometheus PVC (Persistent Volume Claim) - for persistenting the data collected by Prometheus to survive Prometheus Pod restart/crash (alrenatively, omit this section and use emptyDir in the Prometheus Deployment)
- Grafana Deployment
- Grafana Service
- Grafana Data Sources ConfigMap - to connect to Prometheus service as Data Source
- Grafana Dashboards ConfigMap - to point grafana to the path were the Jenknis Jobs dashboard resides
- Grafana Jenkins Job Dashboard ConfigMap - the actual Jenkins Jobs Dashboard

Replace the args section in the Jenkins Exporter Deployment with your Jenkins URL (e.g. `args: ["http://jenkins:8081/view/MYPRODUCT/"]`) and run the following:

    kubectl apply -f jenkins_exporter_k8s_manifest.yaml [--namespace jenkins_exporter]

## Grafana Dashboard

![Demo!](https://i.imgur.com/ABiB53r.png)
