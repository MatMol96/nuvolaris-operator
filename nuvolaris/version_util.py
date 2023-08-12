# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import logging
import nuvolaris.openwhisk as openwhisk
import nuvolaris.kube as kube

def annotate_operator_components_version():
    """
    This functions scans for pod matching the annotations whisks.nuvolaris.org/annotate-version: "true"
    and uses pod metadata.labels.name and spec.containers.image to annotate the global config map cm/config
    """
    try:
        logging.info("**** annotating nuvolaris operator component versions")
        pods = kube.kubectl("get","pods",jsonpath="{.items[?(@.metadata.annotations.whisks\.nuvolaris\.org\/annotate-version)]}",debugresult=False)

        for pod in pods:
            if(pod['metadata'].get('labels') and pod['metadata']['labels'].get('name')):
                pod_name = pod['metadata']['labels']['name']
                pod_image = pod['spec']['containers'][0]['image']

                if(pod_name):
                    openwhisk.annotate(f"{pod_name}_version={pod_image}")
            else:
                logging.warn("**** found a pod with whisks.nuvolaris.org/annotate-version without metadata.labels.name attribute")
                logging.warn(pod)
        
        logging.info("**** completed annotation of nuvolaris operator component versions")       
    except Exception as e:
        logging.error(e)