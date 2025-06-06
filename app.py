import boto3
from datetime import datetime, timedelta

INSTANCE_IDS = os.environ["INSTANCE_IDS"]
REGION = os.environ.get("REGION", "us-east-1")
CPU_THRESHOLD = float(os.environ.get("CPU_THRESHOLD", 5.0))

ec2 = boto3.client('ec2', region_name=REGION)
cloudwatch = boto3.client('cloudwatch', region_name=REGION)

def stop_instance(instance_id):
    pass

def get_idle_instances(instance_ids):
    idle_instances = []

    for instance_id in instance_ids:
        instance_idle = False

        metrics = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average']
        )

        datapoints = metrics.get('Datapoints', [])

        if not datapoints:
            instance_idle = True
        else:
            avg_cpu = datapoints[0]['Average']
            instance_idle = avg_cpu < CPU_THRESHOLD   

        if instance_idle:
            idle_instances.push(instance_id)

    return idle_instances


def lambda_handler(event, context):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)

    instance_ids = ''.join(INSTANCE_IDS.split()).split(",")
    idle_instances = get_idle_instances(InstanceIds)

    print(f"Stopping these due to low CPU usage; {INSTANCE_IDS}")
    ec2.stop_instances(InstanceIds=idle_instances)



if __name__ == "__main__":
    AWS_LAMBDA_RUNTIME_API = os.environ["AWS_LAMBDA_RUNTIME_API"]
    while True:
        url = f"http://{AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/next"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            headers = dict(response.getheaders())
            event_body = json.loads(response.read().decode())

        request_id = headers["Lambda-Runtime-Aws-Request-Id"]
        result = lambda_handler(event_body)

        payload = json.dumps(result).encode('utf-8')
        post_url = f"http://{AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/{request_id}/response"
        post_req = urllib.request.Request(
                post_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
        with urllib.request.urlopen(post_req) as _:
            pass


