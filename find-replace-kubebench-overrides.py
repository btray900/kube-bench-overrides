#!/usr/bin/env python3

# This script is used to update the kube-bench checks with the overrides
# Create override yaml files of the same name (node.yaml, etcd.yaml) with the format:
# overrides:
#   - id: 1.1.1
#     description: "This is a test override"
#     [..snip]
# Name the file to match the upstream source file name such as node.yaml

import sys
import glob
import ruamel.yaml
from ruamel.yaml.comments import CommentedSeq, CommentedMap

# Path to kube-bench files
kubebench_path = sys.argv[1]

# Add as needed per the ./README.md
benchmark_versions = ["cis-1.7","cis-1.8","cis-1.20","cis-1.23","cis-1.24"]

yaml = ruamel.yaml.YAML(typ="rt")
yaml.preserve_quotes = True
yaml.width = 512
yaml.indent(mapping=2, sequence=4, offset=2)

def get_overrides(file_path):
    with open(file_path, "r") as file:
        data = yaml.load(file)
    return data.get("overrides", [])

def load_yaml(file_path):
    with open(file_path, "r") as file:
        return yaml.load(file)

def update_checks(source_data, overrides_data):
    for source_group in source_data["groups"]:
        for source_check in source_group["checks"]:
            for override_check in overrides_data:
                if source_check["id"] == override_check["id"]:
                    print(f"Updating override for {source_check['id']}")
                    source_check.update(override_check)
    return source_data

def dump_yaml(data, file_path):
    with open(file_path, "w") as file:
        yaml.dump(data, file)

def main():
    for benchmark_version in benchmark_versions:
        print(f"Processing benchmark version {benchmark_version}")

        # Loop through all the files in the overrides directories per benchmark version
        # Modify glob path as needed
        for override_file_name in glob.glob(f"{kubebench_path}/{benchmark_version}_overrides/*.yaml"):

            # Get the source file name only
            yaml_file_name = override_file_name.split("/")[-1]

            # Load the override checks
            override_checks = get_overrides(override_file_name)

            # Load source data
            source_check_file = f"{kubebench_path}/cfg/{benchmark_version}/{yaml_file_name}"
            source_checks = load_yaml(source_check_file)

            print(f"Processing override file {override_file_name} for benchmark file {source_check_file}")

            # Update the source checks with the overrides
            updated_source_checks = update_checks(source_checks, override_checks)

            # Dump the updated source checks
            dump_yaml(updated_source_checks, source_check_file)

if __name__ == "__main__":
    main()
