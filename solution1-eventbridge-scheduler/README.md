# Solution 1: Direct EventBridge Scheduler

This solution uses **EventBridge Scheduler** to directly start/stop an RDS instance.

- Start RDS every Monday at 07:00 IST
- Stop RDS every Friday at 22:00 IST

IAM role is secured with least privilege: it can only call `StartDBInstance` and `StopDBInstance` on your specific RDS ARN.

Files:
- `iam-role-policy.json` → IAM role + inline policy
- `start-scheduler.json` / `stop-scheduler.json` → EventBridge schedules
