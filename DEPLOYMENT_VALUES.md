# Quick Reference - Deployment Values

## 🎯 Project Specific Values
**Status:** ✅ COMPLETE - All values configured and working

### EC2 Instance Configuration  
```
Instance ID: i-xxxxx (Ubuntu 24.04, t2.micro)
Public IP: 63.35.236.42
Security Group: sg-0d4bddfc2a85814d2
Region: eu-west-1
```

### GitHub Secrets (Configured)
```bash
AWS_ACCESS_KEY_ID=AKIA... 
AWS_SECRET_ACCESS_KEY=xxx...
AWS_REGION=eu-west-1
EC2_HOST=63.35.236.42
EC2_USERNAME=ubuntu
EC2_APP_PATH=/opt/binance-endpoints
EC2_SECURITY_GROUP_ID=sg-0d4bddfc2a85814d2
EC2_SSH_KEY_B64=[base64-encoded-private-key]
```

## 🔑 SSH Key Setup Commands
```bash
# Convert SSH key to base64 (already done)
cd /c/Users/ijara_go12/.ssh/
cat binance-endpointss.pem | base64 -w 0 > binance-endpoints-key-base64.txt

# Test SSH connection
ssh -i binance-endpointss.pem ubuntu@63.35.236.42
```

## 🚀 EC2 Git Setup (Completed)
```bash
# Configure git with credential storage
git config --global credential.helper store
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Initial repository clone in /opt/binance-endpoints
cd /opt/binance-endpoints
git clone https://github.com/jrysztv/binance-endpoints.git .
```

## 📋 Minimal IAM Policy (Security Reference)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupIngress",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeInstances"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "ec2:Region": "eu-west-1"
                }
            }
        }
    ]
}
```

## 🔗 Live Endpoints
- **API Base:** http://63.35.236.42
- **Health Check:** http://63.35.236.42/health  
- **API Documentation:** http://63.35.236.42/docs
- **GitHub Actions:** https://github.com/jrysztv/binance-endpoints/actions

---
**Note:** This setup is complete and operational. Use as reference for similar projects. 