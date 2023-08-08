import base64

from kubernetes.client import api_client
from kubernetes.client.exceptions import ApiException
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.resource import Resource, Subresource
from kubernetes import config, dynamic, watch

from src.core.logger import get_logger
from src.settings import settings

log = get_logger("api.kubernetes")


class KubeApi():
    # TODO move to async https://github.com/tomplus/kubernetes_asyncio
    def __init__(
            self,
            namespace: str,
            image: str,
            name: str,
            config_path: str = None,
    ) -> None:
        """
        Args:
            namespace (str): Namespace name.
            image (str): Image name for deployment.
            name (str): Service name.
            config_path (str, optional): Path to kube config. If no argument provided, the config will be loaded from default location (~/.kube/config). Defaults to None.
        """
        self.namespace = namespace
        self.image = image
        self.compile_image = settings.compiler_image
        self.name = name
        self.config_path = config_path
        self.client: DynamicClient = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config(config_path))
        )
        self.service_api: Resource = self.client.resources.get(api_version="v1", kind="Service")
        self.deployment_api: Resource = self.client.resources.get(api_version="apps/v1", kind="Deployment")
        self.secret_api: Resource = self.client.resources.get(api_version="v1", kind="Secret")
        self.job_api: Resource = self.client.resources.get(api_version="batch/v1", kind="Job")

    def delete_service(self, name, body: dict = {}) -> Subresource:
        return self.service_api.delete(name=name, body=body, namespace=self.namespace)

    def delete_deployment(self, name, body: dict = {}) -> Subresource:
        return self.deployment_api.delete(name=name, body=body, namespace=self.namespace)

    def delete_secret(self, name, body: dict = {}) -> Subresource:
        return self.secret_api.delete(name=name, body=body, namespace=self.namespace)

    def delete_job(self, client_id: str) -> Subresource:
        try:
            watcher = watch.Watch()
            job = self.job_api.delete(name=f'compiler-{client_id}',
                                      namespace=self.namespace)
            for event in self.job_api.watch(namespace=self.namespace, timeout=60, watcher=watcher):
                if event["type"] == "DELETED":
                    print("stopped")
                    watcher.stop()
            log.info(f"job compiler-{client_id} - deleted")
            return job
        except ApiException as ex:
            log.exception(f"there is no job compiler-{client_id}", exc_info=ex)

    def get_service(self, name: str) -> Subresource:
        return self.service_api.get(name=name, namespace=self.namespace)

    def get_deployment(self, name: str) -> Subresource:
        return self.deployment_api.get(name=name, namespace=self.namespace)

    def get_secret(self, name: str) -> Subresource:
        return self.secret_api.get(name=name, namespace=self.namespace)

    def get_job(self, name: str) -> Subresource:
        return self.job_api.get(name=name, namespace=self.namespace)

    def create_job(self, login: str, client_id: str):
        container_template = {
            "name": f"compiler-{client_id}",
            "image": self.compile_image,
            "env": [
                {
                    "name": "clientLogin",
                    "value": f"{login}"
                },
                {
                    "name": "clientID",
                    "value": f"{client_id}"
                }
            ]
        }

        job_template = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"compiler-{client_id}",
                "namespace": self.namespace
            },
            "spec": {

                "template": {
                    "metadata": {
                        "labels": {"app": f'compiler-{client_id}'}
                    },
                    "spec": {
                        "containers": [container_template],
                        "restartPolicy": "Never"
                    }
                }
            }
        }

        self.delete_job(client_id=client_id)
        try:
            print(job_template)
            job = self.job_api.create(body=job_template, namespace=self.namespace)
            return job
        except ApiException as ex:
            log.exception(f"cant create job {self.name}-{client_id}", exc_info=ex)

    def create_service(self, client_id: str) -> Subresource:
        """create service for user

        Args:
            client_id (str): [description]

        Returns:
            Subresource: Created service description from k8s
        """
        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.name}-{client_id}",
                "namespace": self.namespace
            },
            "spec": {
                "ports": [
                    {
                        "name": "port",
                        "port": 2222,
                        "protocol": "TCP",
                        "targetPort": 2222
                    },
                    {
                        "name": "port8080",
                        "port": 8080,
                        "protocol": "TCP",
                        "targetPort": 8080
                    }
                ],
                "selector": {"app": f"{self.name}-{client_id}"},
            },
        }

        for port in range(1111, 1123):
            port_template = {
                "name": f"port{port}",
                "port": port,
                "protocol": "TCP",
                "targetPort": port
            }
            service_manifest["spec"]["ports"].append(port_template)

        try:
            service = self.service_api.create(body=service_manifest, namespace=self.namespace)
            return service
        except ApiException as ex:
            log.exception(f"Can't create service {self.name}-{client_id}", exc_info=ex)

    def create_deployment(
            self,
            client_id: str,
            limits_memory: str,
            limits_cpu: str,
            requests_memory: str,
            requests_cpu: str
    ) -> Subresource:
        """[summary]

        Args:
            client_id (str): Client id from keycloak
            limits_memory (str, optional): Limit of RAM. Defaults to "1000Mi".
            limits_cpu (str, optional): Limit of CPU. Defaults to "1000m".
            requests_memory (str, optional): Request of RAM. Defaults to "1000Mi".
            requests_cpu (str, optional):  Request of CPU. Defaults to "1000m".

        Returns:
            Subresource: Creaated deployment description from k8s
        """

        contaiter_template = {
            "name": f"{self.name}-{client_id}",
            "image": self.image,
            "resources": {
                "limits": {
                    "memory": limits_memory,
                    "cpu": limits_cpu
                },
                "requests": {
                    "memory": requests_memory,
                    "cpu": requests_cpu
                }
            },
            # "readinessProbe": {
            #     "tcpSocket": {"port": 1110},
            #     "initialDelaySeconds": 70,
            #     "periodSeconds": 20,
            #     "timeoutSeconds": 20,
            #     "failureThreshold": 5,
            #     "successThreshold": 1
            # },
            "livenessProbe": {
                "tcpSocket": {"port": 2222},
                "initialDelaySeconds": 50,
                "timeoutSeconds": 30,
                "failureThreshold": 5,
                "successThreshold": 1
            },
            "ports": [
                {
                    "containerPort": 2222,
                    "protocol": "TCP"
                },
                {
                    "containerPort": 8080,
                    "protocol": "TCP"
                }
            ],
            "volumeMounts": [
                {
                    "mountPath": "/root/config.ini",
                    "name": f"{self.name}-{client_id}",
                    "subPath": "config.ini"
                }
            ]
        }

        volume_template = {
            "name": f"{self.name}-{client_id}",
            "secret": {"secretName": f"{self.name}-{client_id}"}
        }

        deployment_manifest_template = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.name}-{client_id}",
                "namespace": self.namespace
            },
            "spec": {
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxSurge": 1,
                        "maxUnavailable": 0
                    }
                },
                "selector": {
                    "matchLabels": {"app": f'{self.name}-{client_id}'}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": f'{self.name}-{client_id}'}
                    },
                    "spec": {
                        "containers": [contaiter_template],
                        "volumes": [volume_template]
                    },
                },
            },
        }

        for port in range(1111, 1123):
            port_template = {
                "containerPort": port,
                "protocol": "TCP"
            }
            contaiter_template["ports"].append(port_template)

        try:
            deployment = self.deployment_api.create(body=deployment_manifest_template, namespace=self.namespace)
            return deployment
        except ApiException as ex:
            log.exception(f"Can't create deployment {self.name}-{client_id}", exc_info=ex)

    def create_secret(
            self,
            client_id: str,
            login: int,
            password: str,
            server: str,
    ) -> Subresource:
        """[summary]

        Args:
            client_id (str): [description]
            login (str): [description]
            password (str): [description]
            server (str, optional): [description]

        Returns:
            Subresource: Creaated secrete description from k8s
        """
        data = f"[Common]\nLogin={login}\nPassword={password}\nServer={server}\nKeepPrivate=1\nNewsEnable=0\nCertInstall=1\n\n[Experts]\nAllowLiveTrading=1\nAllowDllImport=1\nEnabled=1\nAccount=0\nProfile=0\n\n[Profile]\nProfileLast=12charts\n".encode(
            'ascii')
        data = base64.b64encode(data).decode('ascii')
        secret_manifast = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{self.name}-{client_id}",
                "namespace": self.namespace,
            },
            "type": "Opaque",
            "data": {
                "config.ini": data
            }
        }
        try:
            secret = self.secret_api.create(body=secret_manifast, namespace=self.namespace)
            return secret
        except ApiException as ex:
            log.exception(f"Can't create secret {self.name}-{client_id}", exc_info=ex)


class MetatraderService(KubeApi):
    def __init__(self, namespace: str, image: str, name: str, config_path: str = None) -> None:
        super().__init__(namespace, image, name, config_path)

    def create_user_services(
            self,
            client_id: str,
            login: int,
            password: str,
            server: str = "RoboForex-ECN",
            limits_memory: str = "2000Mi",
            limits_cpu: str = "2000m",
            requests_memory: str = "500Mi",
            requests_cpu: str = "500m"
    ):
        """[summary]

        Args:
            client_id (str): [description]
            login (str): [description]
            password (str): [description]
            server (str, optional): [description]. Defaults to "RoboForex-ECN".
            limits_memory (str, optional): Limit of RAM. Defaults to "1000Mi".
            limits_cpu (str, optional): Limit of CPU. Defaults to "1000m".
            requests_memory (str, optional): Request of RAM. Defaults to "1000Mi".
            requests_cpu (str, optional):  Request of CPU. Defaults to "1000m".
        """
        service_name = f"{self.name}-{client_id}"
        # check if kube services is exist
        try:
            service = self.get_service(service_name)
        except Exception as ex:
            log.warn(f"Can't find service {service_name}; error from k8s: {str(ex)}")
            service = self.create_service(client_id=client_id)
            log.info(f"Create service: {service_name}")

        # check if kube secrets is exist
        try:
            secret = self.get_secret(service_name)
        except Exception as ex:
            log.warn(f"Can't find secrete {service_name}; error from k8s: {str(ex)}")
            secret = self.create_secret(
                client_id=client_id,
                login=login,
                password=password,
                server=server,
            )
            log.info(f"Create secret: {service_name}")

        # check if kube deployments is exist
        try:
            deployment = self.get_deployment(service_name)
        except Exception as ex:
            log.warn(f"Can't find deployment {service_name}; error from k8s: {str(ex)}")
            deployment = self.create_deployment(
                client_id=client_id,
                limits_memory=limits_memory,
                limits_cpu=limits_cpu,
                requests_memory=requests_memory,
                requests_cpu=requests_cpu,
            )
            log.info(f"Create deployment: {service_name}")

        return service, secret, deployment

    def delete_user_services(self, client_id):
        service_name = f"{self.name}-{client_id}"
        try:
            service = self.delete_service(service_name)
            secrets = self.delete_secret(service_name)
            deployments = self.delete_deployment(service_name)
            return service, secrets, deployments
        except Exception as ex:
            log.warn(f"Can't delete users services, error: {str(ex)}")


metatrader_service = MetatraderService(
    namespace=settings.namespace,
    image=settings.image,
    name=settings.k8s_name,
    config_path=settings.config_path
)
