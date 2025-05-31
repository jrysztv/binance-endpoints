# AWS & GitHub Actions Setup Guide

## 🎯 Overview
Complete reference for setting up AWS CLI permissions and GitHub Actions CI/CD for FastAPI deployment to EC2.

**Status:** ✅ COMPLETE - This project has successfully implemented this setup.

## 🔑 AWS IAM Setup

### Create IAM User
1. **AWS Console** → IAM → Users → Create user
2. **Username:** `github-actions-binance-endpoints`
3. **Permissions:** Attach `AmazonEC2FullAccess` policy
4. **Access Keys:** Create access key for "Application running outside AWS"
5. **Save:** Access Key ID and Secret Access Key

### Minimal Security Policy (Alternative)
For production, use this limited policy instead of full EC2 access:

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

## 🔧 GitHub Repository Setup

### 1. Create Repository
```bash
# Create repository on GitHub, then:
git remote add origin https://github.com/username/project-name.git
git branch -M main
git push -u origin main
```

### 2. Configure GitHub Secrets
**Repository → Settings → Secrets and variables → Actions**

Required secrets:
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xxx...
AWS_REGION=eu-west-1
EC2_HOST=your-instance-ip
EC2_USERNAME=ubuntu
EC2_APP_PATH=/opt/your-app
EC2_SECURITY_GROUP_ID=sg-xxx
EC2_SSH_KEY_B64=[base64-encoded-private-key]
```

### 3. Create Production Environment
**Repository → Settings → Environments → New environment: `production`**

## 🚀 EC2 Setup

### Prepare Instance
```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-instance-ip

# Create app directory
sudo mkdir -p /opt/your-app
sudo chown ubuntu:ubuntu /opt/your-app

# Configure git with credential storage
git config --global credential.helper store
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Clone repository (prompts for credentials once)
cd /opt/your-app
git clone https://github.com/username/project-name.git .
```

### Git Authentication Options

**Option A: Personal Access Token (Recommended)**
- Create at: GitHub → Settings → Developer settings → Personal access tokens
- Scopes: `repo`, `workflow`
- Use token as password when prompted

**Option B: SSH Key**
```bash
# Generate SSH key on EC2
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub
# Add public key to GitHub → Settings → SSH and GPG keys
```

## 🧪 Testing

### Local Testing
```bash
# Test Docker build
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
curl http://localhost/health
docker compose -f docker-compose.prod.yml down
```

### EC2 Testing
```bash
# On EC2, test git automation
cd /opt/your-app
git pull origin main  # Should work without prompting
```

## 🔒 Security Best Practices

1. **Minimal Permissions:** Use custom IAM policy instead of full EC2 access
2. **Credential Storage:** Git credentials stored securely on EC2
3. **SSH Key Security:** Base64 encode private keys for GitHub secrets
4. **Regular Rotation:** Rotate access keys every 90 days
5. **Environment Protection:** Use GitHub environment protection rules

## 🐛 Troubleshooting

### Common Issues
- **"docker-compose: command not found":** Use `docker compose` (space, not hyphen)
- **SSH Permission Denied:** Check key permissions: `chmod 600 ~/.ssh/key.pem`
- **Git Credentials:** Ensure `credential.helper store` is configured
- **AWS Access Denied:** Verify IAM policy and access keys

### Debug Commands
```bash
# Check git config
git config --list | grep credential

# Check SSH key
ssh-keygen -l -f ~/.ssh/key.pem

# Test AWS CLI
aws ec2 describe-instances --instance-ids i-xxxxx
```

## 📋 Deployment Checklist

- [ ] AWS IAM user created with access keys
- [ ] GitHub repository created and secrets configured
- [ ] EC2 instance accessible and prepared
- [ ] Git credentials stored on EC2
- [ ] Docker and Docker Compose working
- [ ] Local testing successful
- [ ] GitHub Actions workflow tested

---
**Reference Implementation:** [binance-endpoints](https://github.com/jrysztv/binance-endpoints) - Complete working example 