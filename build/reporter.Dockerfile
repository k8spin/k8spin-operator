FROM python:3.9

COPY k8spin_reporter/requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

COPY k8spin_common /src/k8spin_common
RUN pip install -e /src/k8spin_common

COPY k8spin_reporter /app/k8spin_reporter

ENTRYPOINT [ "python" ]
CMD ["/app/k8spin_reporter/app.py"]
