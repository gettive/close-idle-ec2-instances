import boto3
from datetime import datetime, timedelta

INSTANCE_ID = os.environ["INSTANCE_ID"]
REGION = os.environ.get("REGION", "us-east-1")
CPU_THRESHOLD = float(os.environ.get("CPU_THRESHOLD", 5.0))

ec2 = boto3.client('ec2', region_name=REGION)
cloudwatch = boto3.client('cloudwatch', region_name=REGION)

def lambda_handler(event, context):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)

    metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Average']
    )

    datapoints = metrics.get('Datapoints', [])
    if not datapoints:
        print("No CPU data, assuming idle.")
        should_stop = True
    else:
        avg_cpu = datapoints[0]['Average']
        print(f"Average CPU: {avg_cpu}%")
        should_stop = avg_cpu < CPU_THRESHOLD

    if should_stop:
        print(f"Stopping instance {INSTANCE_ID} due to low CPU usage.")
        ec2.stop_instances(InstanceIds=[INSTANCE_ID])
    else:
        print(f"Instance {INSTANCE_ID} is active.")


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


