from plano import *

image_name = "quay.io/ssorj/oscillating-ocelot"

@command
def build(no_cache=False):
    """
    Build the test image
    """

    no_cache_arg = "--no-cache" if no_cache else ""

    run(f"podman manifest rm {image_name}", check=False, quiet=True)
    run(f"podman image rm {image_name}", check=False, quiet=True)
    run(f"podman manifest create {image_name}")
    run(f"podman build {no_cache_arg} --format docker --platform linux/amd64,linux/arm64 --manifest {image_name} .")

@command
def run_():
    """
    Run the test container
    """

    clean()

    work_dir = get_absolute_path(make_dir("work"))

    make_kubeconfig_bundle(join(work_dir, ".kube"))
    copy("test.sh", "work/test.sh")

    run(f"podman run -it --rm --security-opt label=disable -v {work_dir}:/root {image_name}")

def make_kubeconfig_bundle(target):
    source = read_yaml("~/.kube/config")

    assert source["current-context"] == "minikube"

    for cluster in source["clusters"]:
        if cluster["name"] == "minikube":
            break
    else:
        assert False

    for user in source["users"]:
        if user["name"] == "minikube":
            break
    else:
        assert False

    cluster_server = cluster["cluster"]["server"]

    write(join(target, "cluster-server"), cluster_server)
    copy(cluster["cluster"]["certificate-authority"], join(target, "ca.crt"))
    copy(user["user"]["client-certificate"], join(target, "client.crt"))
    copy(user["user"]["client-key"], join(target, "client.key"))

    kubeconfig = kubeconfig_template.format(cluster_server=cluster_server).lstrip()

    write(join(target, "config"), kubeconfig)

    return get_absolute_path(target)

kubeconfig_template = """
apiVersion: v1
kind: Config
current-context: test
clusters:
  - name: test
    cluster:
      server: {cluster_server}
      certificate-authority: /root/.kube/ca.crt
users:
  - name: test
    user:
      client-certificate: /root/.kube/client.crt
      client-key: /root/.kube/client.key
contexts:
  - name: test
    context:
      cluster: test
      user: test
"""

@command
def clean():
    if exists("work"):
        run("chmod -R u+w work")

    remove("work")
    remove("__pycache__")
