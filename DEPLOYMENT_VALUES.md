# Deployment Values Reference

## 🔧 GitHub Secrets Configuration

Based on your PROJECT_STATUS.md, here are the exact values to use when setting up GitHub secrets:

### AWS Configuration
```
AWS_REGION=eu-west-1
```

### EC2 Configuration  
```
EC2_HOST=63.35.236.42
EC2_USERNAME=ubuntu
EC2_APP_PATH=/opt/binance-endpoints
EC2_SECURITY_GROUP_ID=sg-0d4bddfc2a85814d2
```

### SSH Key
```
EC2_SSH_KEY_B64=[contents of your ssh-key-base64.txt file]
```

## 🚀 Commands to Run

### 1. Get SSH Key Content
```bash
# Copy this to GitHub Secret EC2_SSH_KEY_B64
cat ssh-key-base64.txt
```

### 2. Create GitHub Repository
```bash
# If not already created
git remote add origin https://github.com/jrysztv/binance-endpoints.git
git branch -M main
git push -u origin main
```

### 3. Test EC2 Connection
```bash
# From WSL/Linux
ssh -i binance-endpoints-key ubuntu@63.35.236.42
```

### 4. Prepare EC2 for First Deployment
```bash
# On EC2 instance
sudo mkdir -p /opt/binance-endpoints
sudo chown ubuntu:ubuntu /opt/binance-endpoints
cd /opt/binance-endpoints

# Clone repository (use HTTPS with Personal Access Token)
git clone https://github.com/jrysztv/binance-endpoints.git .
```

## 📋 AWS IAM Setup

### Minimal IAM Policy for GitHub Actions
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

## 🎯 Next Steps
1. Create IAM User in AWS Console
2. Get AWS Access Key ID and Secret Access Key  
3. Create GitHub repository
4. Add all secrets to GitHub repository settings
5. Push code to trigger first deployment 