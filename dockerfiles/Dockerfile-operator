FROM python:3.8

COPY k8spin_operator/requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

COPY k8spin_common /src/k8spin_common
RUN pip install -e /src/k8spin_common

COPY k8spin_operator /app/k8spin_operator

ENTRYPOINT [ "kopf", "run" ]
CMD ["/app/k8spin_operator/operator.py"]
