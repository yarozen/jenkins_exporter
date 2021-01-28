# Jenkins Exporter

Jenkins Exporter for Prometheus written in Python3.

Collects and exposes last build metrics (result, duration, timestamp) for every Repository & Branch from the provided Jenkins URL.

## Usage

    usage: jenkins_exporter.py [-h] [-p {1..65535}] [-v] [-u USERNAME] [-k PASSWORD] JENKINS_URL

    Jenkins Exporter for Prometheus

    positional arguments:
    JENKINS_URL           Jenkins Server URL (e.g. http://jenkins:8080 or http://jenkins:8080/view/MYPRODUCT)

    optional arguments:
    -h, --help            show this help message and exit
    -p {1..65535}, --port {1..65535}
                            Jenkins Exporter listening port (Default is 9789)
    -v, --verbose         Increase output verbosity (DEBUG)
    -u USERNAME, --username USERNAME
                            Jenkins Server username
    -k PASSWORD, --password PASSWORD
                            Jenkins Server password

## Produced Metrics

|Metric|Description|Value|
|---|---|---|
|`jenkins_job_build_timestamp`|The time which the build was completed|epoch ms (milliseconds passed since 00:00:00 UTC on 1 January 1970)
|`jenkins_job_build_duration`|The time it took the build to complete| ms (millieconds)
|`jenkins_job_build_result`|Build result| <ul><li>FAILURE = 0</li><li>ABORTED = 0.5</li><li>UNSTABLE = 0.7</li><li>STABLE = 1</li><li>SUCCESS = 1</li></ul>

## Output Sample

    # HELP jenkins_job_build_timestamp Jenkins build completion time in epoch milliseconds 
    # TYPE jenkins_job_build_timestamp gauge
    jenkins_job_build_timestamp{branch="dev",build="1",repo="my_repo"} 1.611744014484e+012
    # HELP jenkins_job_build_duration Jenkins build duration in milliseconds 
    # TYPE jenkins_job_build_duration gauge
    jenkins_job_build_duration{branch="dev",build="1",repo="my_repo"} 507379.0
    # HELP jenkins_job_build_result Jenkins build result (1=Succces/Stable, 0.7=Unstable, 0.5=Aborted, 0=Failure)
    # TYPE jenkins_job_build_result gauge
    jenkins_job_build_result{branch="dev",build="1",repo="my_repo"} 1.0

## Running in Docker

    docker run -p 9789:9789 yarozen/jenkins_exporter -p 9789 http://jenkins:8081/view/MYPRODUCT

## Running in Kubernetes

The `jenkins_exporter_k8s_manifest.yaml` will deploy everything needed to collect and display your Jenkins metrics:

* Jenkins Exporter
  * Deployment
  * Service
* Prometheus
  * Deployment
  * Service
  * ConfigMap  - containing prometheus.yaml to scrape from the Jenkins Exporter Service
  * Persistent Volume Claim (PVC) - for persistenting the data collected by Prometheus (alternatively, you can omit this section and use emptyDir in the Prometheus Deployment)
* Grafana
  * Deployment
  * Service
  * ConfigMap Data Sources - to connect to Prometheus Service as Data Source
  * ConfigMap Dashboards - to point grafana to the path were the Jenknis Jobs dashboard resides
  * ConfigMap Jenkins Job Dashboard - the actual Jenkins Jobs Dashboard

Replace the args section in the Jenkins Exporter Deployment with your Jenkins URL (e.g. `args: ["http://jenkins:8081/view/MYPRODUCT/"]`) and run the following:

    kubectl apply -f jenkins_exporter_k8s_manifest.yaml [--namespace jenkins_exporter]

## Grafana Dashboard

![Demo!](https://i.imgur.com/ABiB53r.png)
