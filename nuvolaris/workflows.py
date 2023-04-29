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
import kopf
import logging, time, yaml, json, flatdict, os, os.path, random, string
import nuvolaris.config as cfg
import nuvolaris.kube as kube
import nuvolaris.template as tpl

def generate_job(name, spec, action, id):
    
    data = {
        'name': f"{name}-{action}-{id}",
        'image': spec['image']
    }

    if "command" in spec:
        data['command'] = json.dumps(spec['command'])

    environ = [
        { "name": "_WORKFLOW_", "value": ""}, # to be replaced with name
        { "name": "_ACTION_", "value": action },
        { "name":  "_APIHOST_", "value": cfg.get("config.apihost", defval="undefined-apihost") },
        { "name": "_AUTH_", "value": cfg.get("openwhisk.namespaces.nuvolaris",  defval="undefined-auth") }
    ]

    if "env" in spec:
        environ += [ {"name": k, "value": spec['env'][k]} for k in spec['env']]

    data['jobs'] = []

    for w in spec.get('workflows'):
        job = {}
        args = []
        job['name'] = w['name']
        params = w.get("parameters")
        for k in params:
            arg = f"{k}={params[k]}"
            args.append(arg)
        job['args'] = json.dumps(args)
        environ[0]['value'] = w['name']
        job['environ'] = json.dumps(environ)
        data['jobs'].append(job)

    return tpl.expand_template('workflow-job.yaml', data)
    
# tested by an integration test
@kopf.on.create('nuvolaris.org', 'v1', 'workflows')
def workflows_create(spec, name, **kwargs):
    logging.info(f"*** workflows_create {name}")
    id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    kube.apply(generate_job(name, spec, "create", id))

@kopf.on.delete('nuvolaris.org', 'v1', 'workflows')
def workflows_delete(spec, name, **kwargs):
    logging.info(f"*** workflows_delete {name}")
    id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    kube.apply(generate_job(name, spec, "delete", id))
