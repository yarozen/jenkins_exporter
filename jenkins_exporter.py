import argparse
import json
import logging
import time
from urllib.parse import unquote

import requests
import urllib3
from prometheus_client import PLATFORM_COLLECTOR, PROCESS_COLLECTOR
from prometheus_client.core import (REGISTRY, CounterMetricFamily, GaugeMetricFamily)
from prometheus_client.exposition import start_http_server
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger('Jenkins Exporter')


class JenkinsCollector(object):
    objs = ['timestamp', 'duration', 'result']
    result_map = {
        'FAILURE': 0,
        'ABORTED': 0.5,
        'UNSTABLE': 0.7,
        'STABLE': 1,
        'SUCCESS': 1
    }

    def __init__(self, jenkins, username, password):
        self.url = jenkins.rstrip('/') + \
            '/api/json?tree=jobs[name,lastBuild[number,building,result,duration,timestamp],jobs[name,lastBuild[number,building,result,duration,timestamp]]]'
        self.auth = (username, password) if username and password else None

    def _init_metrics(self):
        self.metrics = {}
        for obj in self.objs:
            self.metrics[obj] = GaugeMetricFamily(f'jenkins_job_build_{obj}', '', labels=['repo', 'branch', 'build'])

    def collect(self):
        # initialize metrics
        self._init_metrics()
        try:
            response = requests.get(
                self.url,
                verify=False,
                auth=self.auth
            )
            response.raise_for_status()
            for main_job in response.json()["jobs"]:
                # WorkflowMultiBranchProject
                if main_job["_class"] == "org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject":
                    for branch_job in main_job["jobs"]:
                        self._get_job_metrics(branch_job, main_job["name"])
                # WorkflowJob
                elif main_job["_class"] == "org.jenkinsci.plugins.workflow.job.WorkflowJob":
                    self._get_job_metrics(main_job, main_job["name"])

            for m in self.metrics:
                yield self.metrics[m]
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
            KeyError,
            json.decoder.JSONDecodeError
        ) as e:
            logger.error('{}: {}'.format(type(e).__name__, e))

    def _get_job_metrics(self, job, repo_name):
        if "lastBuild" in job:
            if not job["lastBuild"]["building"]:
                if job["name"] == repo_name:
                    branch_name = "N/A"
                else:
                    branch_name = unquote(job["name"])
                build_number = str(job["lastBuild"]["number"])
                for obj in self.objs:
                    value = job["lastBuild"][obj]
                    if obj == 'result':
                        value = self.result_map[value]
                    labels = [repo_name, branch_name, build_number]
                    self.metrics[obj].add_metric(labels, value)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Jenkins Exporter for Prometheus'
    )
    parser.add_argument(
        'jenkins',
        help='Jenkins Server URL (e.g. http://jenkins:8080 or http://jenkins:8080/view/MYPRODUCT)',
        metavar="JENKINS_URL"
    )
    parser.add_argument(
        '-p', '--port',
        help='Jenkins Exporter listening port (Default is 9789)',
        type=int,
        default=9789,
        choices=range(1, 65535),
        metavar="{1..65535}"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Increase output verbosity (DEBUG)",
        action="store_true"
    )
    parser.add_argument(
        '-u', '--username',
        help='Jenkins Server username',
        default=None
    )
    parser.add_argument(
        '-k', '--password',
        help='Jenkins Server password',
        default=None
    )
    return parser.parse_args()


def main():
    try:
        args = parse_args()
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        logger.info(f"Jenkins Exporter started")
        REGISTRY.register(JenkinsCollector(args.jenkins, args.username, args.password))
        # Clean up irrelevant metrics
        for c in [PROCESS_COLLECTOR,
                  PLATFORM_COLLECTOR,
                  REGISTRY._names_to_collectors['python_gc_collections_total']]:
            REGISTRY.unregister(c)
        start_http_server(args.port)
        logger.info(f"Jenkins Exporter listening on port {args.port}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(" Interrupted")
        exit(0)


if __name__ == "__main__":
    main()
