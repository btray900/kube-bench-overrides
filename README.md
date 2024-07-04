# Kube Bench Overrides for CIS Kubernetes Benchmark Tests

This repository contains a helper scrip to create overrides for the kube-bench tool.
The kube-bench tool is a Go application that checks whether Kubernetes
is deployed securely by running the checks documented in the CIS
Kubernetes Benchmark.

## Overview

In some instances it may be necessary to override the default kube-bench CIS benchmark tests
results due to the specific configuration of your cluster. This repository
contains a script to find and replace CIS benchmarks. Use this kube bench override tool
to modify the default test results for the CIS Kubernetes Benchmark with expected pass/fail
results based on your specific environment.

### Usage

To use the overrides, clone this repository and setup the override yaml
files as desired for any number of tests.

The script assumes a directory structure as follows:

```
./kube-bench
./kube-bench/cfg
./kube-bench/<benchmark>_overrides
./kube-bench/<benchmark>_overrides/<node_name>.yaml
```

Create the overrides in the `<benchmark>_overrides` directory with the
`<node_name>.yaml` file name.

Where `<benchmark>` could be `cis-1.20` or `cis-1.7` and `<node_name>.yaml`
files would be `master.yaml` or `node.yaml` or `worker.yaml` etc.

Modify the `tests` section of the yaml file to include the pass/fail results
you want to override.

The script will look for the overrides in the script's list of `benchmark_versions`
overrides directories and replace the pre-exiting control test in the `cfg/<benchmark>/<node_name>.yaml` file.

*Execute*

```
git clone https://github.com/aquasecurity/kube-bench.git
```

Create overrides per the examples below and run the script:

```
./find-replace-kubebench-overrides.py ../kube-bench
```


#### Examples

`cis-1.20_overrides/master.yaml`

Parent level objec should be `overrides` and each override should be a list item with the following fields:

Bracketed info is for reporting purposes to easily identify the override.

```yaml
---
overrides:
  - id: 1.1.12
    text: "[MY OVERRIDE] Ensure that the etcd data directory ownership is set to etcd:etcd (OVERRIDE root:root) (Automated)"
    audit: |
      DATA_DIR=''
      for d in $(ps -ef | grep $etcdbin | grep -- --data-dir | sed 's%.*data-dir[= ]\([^ ]*\).*%\1%'); do
        if test -d "$d"; then DATA_DIR="$d"; fi
      done
      if ! test -d "$DATA_DIR"; then DATA_DIR=$etcddatadir; fi
      stat -c %U:%G "$DATA_DIR"
    tests:
      test_items:
        # - flag: "etcd:etcd" # kubeadm does not have etcd:etcd user/group
        - flag: "root:root"
    remediation: |
      On the etcd server node, get the etcd data directory, passed as an argument --data-dir,
      from the command 'ps -ef | grep etcd'.
      Run the below command (based on the etcd data directory found above).
      For example, chown etcd:etcd /var/lib/etcd
    scored: true

  - id: 1.2.5
    text: "[MY OVERRIDE] Ensure that the --kubelet-certificate-authority argument is set as appropriate (OVERRIDE not set) (Automated)"
    audit: "/bin/ps -ef | grep $apiserverbin | grep -v grep"
    tests:
      test_items:
        - flag: "--kubelet-certificate-authority"
          set: false # kubeadm kubelet cert SANS is hostname only, set to false to pass in my environment
    remediation: |
      Follow the Kubernetes documentation and setup the TLS connection between
      the apiserver and kubelets. Then, edit the API server pod specification file
      $apiserverconf on the control plane node and set the
      --kubelet-certificate-authority parameter to the path to the cert file for the certificate authority.
      --kubelet-certificate-authority=<ca-string>
    scored: true
```

#### Test artifacts

*Directory Structure*

Your directory should look like this by default to use the helper script.

![Alt text](./images/dir.png?raw=true "Directory Structure")

*Override Example*

Update the test pass/fail criteris as needed. Add annotations to the text for easy reporting identification.

```
./kube-bench/cis-1.20_overrides/master.yaml
```

![Alt text](./images/override.png?raw=true "Override Example")

*Updated `cfg` File*

The script will modify the upstream test file with your override.

```
./kube-bench/cfg/cis-1.20/master.yaml
```

![Alt text](./images/cis.png?raw=true "Updated `cfg` File")

*Test Result*

Test result should pass (or fail) based on your override.

![Alt text](./images/run.png?raw=true "Test result")