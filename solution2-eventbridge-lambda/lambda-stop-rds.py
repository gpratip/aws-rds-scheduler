import boto3, os
from datetime import datetime, timedelta

# AWS clients
rds = boto3.client('rds')
cloudwatch = boto3.client('cloudwatch')
events = boto3.client('events')

# Environment variables
DB_IDENTIFIER = os.environ['DB_IDENTIFIER']
PRIMARY_LAMBDA_ARN = os.environ['PRIMARY_LAMBDA_ARN']
RETRY_DELAY_MINUTES = int(os.environ.get('RETRY_DELAY_MINUTES', 60))

# Retry rule name
RETRY_RULE_NAME = f"RDSRetryRule-{DB_IDENTIFIER}"

def lambda_handler(event, context):
    # 1. Get current DB connections (last 2 minutes)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=2)
    
    metric_response = cloudwatch.get_metric_data(
        MetricDataQueries=[{
            'Id': 'dbConnections',
            'MetricStat': {
                'Metric': {
                    'Namespace': 'AWS/RDS',
                    'MetricName': 'DatabaseConnections',
                    'Dimensions': [{'Name': 'DBInstanceIdentifier', 'Value': DB_IDENTIFIER}]
                },
                'Period': 60,
                'Stat': 'Maximum'
            }
        }],
        StartTime=start_time,
        EndTime=end_time
    )
    
    values = metric_response['MetricDataResults'][0].get('Values', [])
    connections = values[0] if values else 0
    print(f"Current DB connections: {connections}")
    
    if connections == 0:
        # Stop DB if idle
        print("Stopping RDS instance...")
        rds.stop_db_instance(DBInstanceIdentifier=DB_IDENTIFIER)
        
        try:
            events.disable_rule(Name=RETRY_RULE_NAME)
            print(f"Disabled retry EventBridge rule: {RETRY_RULE_NAME}")
        except events.exceptions.ResourceNotFoundException:
            print("Retry rule not found, nothing to disable.")
    else:
        # DB busy → schedule retry
        print(f"DB is busy, scheduling retry in {RETRY_DELAY_MINUTES} minutes...")
        
        retry_time = datetime.utcnow() + timedelta(minutes=RETRY_DELAY_MINUTES)
        cron_expression = f"cron({retry_time.minute} {retry_time.hour} {retry_time.day} {retry_time.month} ? {retry_time.year})"
        
        events.put_rule(
            Name=RETRY_RULE_NAME,
            ScheduleExpression=cron_expression,
            State='ENABLED',
            Description=f"Retry stopping RDS {DB_IDENTIFIER} once"
        )
        
        events.put_targets(
            Rule=RETRY_RULE_NAME,
            Targets=[{'Id': f"RetryTarget-{DB_IDENTIFIER}", 'Arn': PRIMARY_LAMBDA_ARN}]
        )
        print(f"Retry rule {RETRY_RULE_NAME} scheduled at {retry_time} UTC.")
    
    return {"DBConnections": connections}
