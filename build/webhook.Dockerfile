FROM python:3.8

COPY k8spin_webhook/requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

COPY k8spin_common /src/k8spin_common
RUN pip install -e /src/k8spin_common

COPY k8spin_webhook /app/k8spin_webhook

EXPOSE 443

VOLUME ["/certs"]

ENTRYPOINT [ "python" ]
CMD ["/app/k8spin_webhook/app.py"]
