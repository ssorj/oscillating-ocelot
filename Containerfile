FROM --platform=$BUILDPLATFORM registry.access.redhat.com/ubi9-minimal

ARG TARGETOS
ARG TARGETARCH

RUN microdnf -y install git golang openssl podman && microdnf clean all

RUN curl -L "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/$TARGETOS/$TARGETARCH/kubectl" -o /bin/kubectl
RUN chmod 755 /bin/kubectl

WORKDIR /root

CMD ["./test.sh"]
