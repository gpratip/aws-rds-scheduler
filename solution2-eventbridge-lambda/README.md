# Solution 2: EventBridge + Lambda with Retry

This solution uses **EventBridge + Lambda** to safely stop RDS instances.

- Start RDS every Monday at 07:00 IST (direct scheduler)
- Stop RDS every Friday at 22:00 IST (via Lambda)
- Lambda checks `DatabaseConnections` metric in CloudWatch
- Retries every 1 hour until DB is idle

IAM role is secured with least privilege: it can only stop your specific RDS instance, read metrics, and manage retry rules.

Files:
- `iam-role-policy.json` → IAM execution role for Lambda
- `lambda-stop-rds.py` → Lambda function with retry logic
- `start-scheduler.json` / `stop-rule.json` / `retry-rule.json` → EventBridge configs
