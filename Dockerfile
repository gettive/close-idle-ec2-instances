FROM amazonlinux:2

RUN yum install -y python3 python3-pip \
    && pip3 install boto3

COPY app.py /var/task/app.py
COPY bootstrap /var/task/bootstrap

RUN chown -R root:root /var/task \
    && chmod 775 /var/task/bootstrap \
    && chmod +x /var/task/bootstrap

ENTRYPOINT ["/var/task/bootstrap"]