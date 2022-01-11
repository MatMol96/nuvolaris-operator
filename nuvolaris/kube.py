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
# this module wraps kubectl
import subprocess
import json
import logging

output = ""
error = ""
returncode = -1

# execute kubectl commands
# default namespace is nuvolaris, you can change with keyword arg namespace
# default output is text
# if you specify jsonpath it will filter and parse the json output
# returns exceptions if errors
def kubectl(*args, namespace="nuvolaris", jsonpath=None, input=None):
    """Test kube
    
    >>> import nuvolaris.kube as kube
    >>> import nuvolaris.testutil as tu
    >>> tu.grep(kube.kubectl("get", "ns"), "kube-system", field=0)
    kube-system
    >>> kube.returncode
    0
    >>> "default" in kube.kubectl("get", "ns", jsonpath="{.items[*].metadata.name}")
    True
    >>> tu.catch(lambda: kube.kubectl("error"))
    <class 'Exception'> Error: flags cannot be placed before plugin name: -n
    >>> print(kube.returncode, kube.error.strip())
    1 Error: flags cannot be placed before plugin name: -n
    """
    cmd = ["kubectl", "-n", namespace]
    cmd += list(args)
    if jsonpath:
        cmd += ["-o", "jsonpath-as-json=%s" % jsonpath]
    logging.debug("command: %s", " ".join(cmd))
    # executing
 

    res = subprocess.run(cmd, capture_output=True, input=input)

    res = subprocess.run()
    global returncode, output, error
    returncode = res.returncode
    output = res.stdout.decode()
    error = res.stderr.decode()

    if res.returncode == 0:
        if jsonpath:
                parsed = json.loads(output)
                logging.debug("result: %s", json.dumps(parsed, indent=2))
                return parsed
        else:
            return output
    raise Exception(error)