#!/usr/bin/env python3

from contextlib import contextmanager
import json
import os
from pathlib import Path
from subprocess import check_call
import sys

@contextmanager
def chdir(newdir):
    curdir = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(curdir)

def header_source(component):
    return "#include <{}.h>".format(component["name"])

def initializer_source(component):
    # If there is no initialization step, return an empty string.
    if "initialize" in component and component["initialize"] == False:
        return ""

    name = component["name"]
    args = ", ".join(component["initializeArgs"])

    return "    {}_init({});".format(name, args)

def runner_source(repo):
    name = repo["name"]

    if repo["run"] is False:
        return None

    return "    {}_run();".format(name)

def kernel_source(components, config):
    headers = map(header_source, components)
    initializers = map(initializer_source, components)
    runners = map(runner_source, components)
    runners = filter(lambda x: x is not None, runners)

    source = ""
    source += "\n".join(headers) + "\n\n"
    source += "void tinker_kernel_main(void)\n"
    source += "{\n"
    source += "\n".join(initializers) + "\n"
    source += "\n".join(runners) + "\n"
    source += "}\n"

    return source

def makefile_ldflags_source(component):
    return "-l :{}.a".format(Path(tinker_repo_dir(component)).name)

def makefile_include_source(component):
    return "-I {}/include".format(tinker_repo_dir(component))

def makefile_source(components, config, output_file):
    dir_path = Path(__file__).parent
    with Path(dir_path, "..", "data", "Makefile.kernel.template").open() as f:
        template = f.read()

    data = {
        "os_name": config["os_name"],
        "default_target": config["default_target"],
        "output_file": output_file,
        "output_file_obj": str(Path(output_file).with_suffix(".o")),
        "kernel_ldflags": " ".join(map(makefile_ldflags_source, components)),
        "includes": " ".join(map(makefile_include_source, components)),
    }

    return template.format(**data)

def try_split(string, separator, minimum_size, default=None):
    parts = string.split(separator)
    diff = minimum_size - len(parts)

    if diff > 0:
        parts += [default] * diff

    return parts

def tinker_dir(folder=""):
    return os.path.normpath(os.path.join(os.getcwd(), "deps", folder))

# ASSUMPTION: A directory with an @ symbol in it won't break things.
# ASSUMPTION: A directory with an @ symbol at the end won't break things.
# ASSUMPTION: Nobody cares if they have a directory ending with @ in ./tinker/.
def tinker_repo_dir(component):
    if component["origin"][0] == "." or component["origin"][0] == "/":
        return component["origin"]

    component_name = component["name"]
    _, branch = try_split(component["origin"], "#", 2, default="")

    return tinker_dir("{}@{}".format(component_name, branch))

def ensure_tinker_root_exists():
    tinker_dir_ = tinker_dir()
    if not os.path.exists(tinker_dir_):
        # If it doesn't exist, create it.
        os.mkdir(tinker_dir_)
    elif not os.path.isdir(tinker_dir_):
        raise NotADirectoryError("expected {} to be a directory.".format(tinker_dir_))

def git_clone(dependency):
    origin = dependency["origin"]

    repo, branch = try_split(origin, "#", 2)

    if branch:
        branch_args = ["--branch", branch]
    else:
        branch_args = []

    destination = tinker_repo_dir(dependency)
    with chdir(tinker_dir()):
        check_call(["git", "clone", *branch_args, "--", repo, destination])

def git_pull(dependency):
    with chdir(tinker_repo_dir(dependency)):
        check_call(["git", "pull"])

def clone_or_pull(dependency):
    ensure_tinker_root_exists()
    repo_dir = tinker_repo_dir(dependency)

    if os.path.isdir(repo_dir):
        git_pull(dependency)
    else:
        git_clone(dependency)

    return repo_dir

# ASSUMPTIONS: Dependencies are either git repos or local files.
def fetch_dependency(dependency):
    origin = dependency["origin"]

    if origin[0] == "/" or origin[0] == ".":
        root = origin
    else:
        root = clone_or_pull(dependency)

    dependency["root"] = root

    return dependency

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2 or argv[1] == "--help" or argv[1] == "-h":
        print("Usage: genkern.py output_file.c [kernel.json] [Makefile.kernel]")
        return 1

    output_file = argv[1]
    config_file = argv[2] if len(argv) > 2 else "kernel.json"
    makefile_file = argv[3] if len(argv) > 3 else "Makefile.kernel"

    with open(config_file, "r") as f:
        config = json.load(f)
    raw_dependencies = config["dependencies"]

    dependencies = list(map(fetch_dependency, raw_dependencies))

    with open(output_file, "w") as f:
        f.write(kernel_source(dependencies, config))

    print("Generated kernel with:")
    for dep in dependencies:
        print(" - {} ({})".format(dep["name"], dep["origin"]))

    print("")
    print("")

    print("Output file: {}".format(output_file))

    with open(makefile_file, "w") as f:
        f.write(makefile_source(dependencies, config, output_file))

    print("Makefile:    {}".format(makefile_file))

    return 0

if __name__ == "__main__":
    exit(main())
