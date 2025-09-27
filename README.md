# AWS RDS Scheduler (Save Costs by Automating Start/Stop)

This repository contains two approaches to automatically **start/stop Amazon RDS instances** using **Amazon EventBridge** and **AWS Lambda**.

👉 Full step-by-step guide available in my Medium blog: 
   https://medium.com/@pratipghosh.tech/how-i-automated-aws-rds-instance-scheduling-with-eventbridge-and-lambda-976bc89698a7

---

## 🚀 Solutions

### ✅ Solution 1: Direct EventBridge Scheduler
- Uses EventBridge to directly call RDS APIs (`StartDBInstance` and `StopDBInstance`).
- No Lambda required.
- Very low cost, but no safety check (DB stops even if active).
- [View Solution 1 Code](./solution1-eventbridge-scheduler)

### 🔒 Solution 2: EventBridge + Lambda with Retry
- Uses EventBridge + Lambda to safely stop RDS.
- Lambda checks CloudWatch `DatabaseConnections` before stopping.
- Retries automatically until DB is idle.
- [View Solution 2 Code](./solution2-eventbridge-lambda)

---

## 📊 Cost Comparison
- **Solution 1:** ~$0.000008/month  
- **Solution 2:** ~$0.00025/month  
Both are negligible compared to the cost savings from stopping RDS.

---

## 📂 Repo Organization
- `solution1-eventbridge-scheduler/` → JSON configs for IAM role.
- `solution2-eventbridge-lambda/` → JSON configs for IAM role and Lambda code.

---

## 🛡️ Security Note
All IAM policies in this repo are written with **least privilege**:
- Permissions are restricted to a **single RDS instance ARN**.
- Lambda role can only manage the **specific EventBridge rules** it needs.
