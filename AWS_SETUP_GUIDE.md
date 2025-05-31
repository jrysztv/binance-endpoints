# AWS Setup Guide for GitHub Actions CI/CD

## 🎯 Overview
This guide will help you set up AWS CLI permissions for GitHub Actions to deploy your Binance Endpoints API to EC2.

## 🔑 AWS IAM Setup Options

### Option 1: IAM User with Access Keys (Recommended for Learning)

#### Step 1: Create IAM User
1. Go to AWS Console → IAM → Users
2. Click "Create user"
3. User name: `github-actions-binance-endpoints`
4. Select "Programmatic access"
5. Click "Next"

#### Step 2: Attach Policies
Attach these managed policies:
- `AmazonEC2FullAccess` (or create custom policy below)

#### Step 3: Custom Policy (More Secure)
Instead of full EC2 access, create a custom policy:

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
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupIngress"
            ],
            "Resource": "arn:aws:ec2:eu-west-1:*:security-group/sg-0d4bddfc2a85814d2"
        }
    ]
}
```

#### Step 4: Get Access Keys
1. After creating user, click on the user
2. Go to "Security credentials" tab
3. Click "Create access key"
4. Choose "Application running outside AWS"
5. **Save the Access Key ID and Secret Access Key** (you won't see the secret again)

### Option 2: IAM Role with OIDC (Advanced, More Secure)

#### Step 1: Create IAM Role
1. Go to AWS Console → IAM → Roles
2. Click "Create role"
3. Select "Web identity"
4. Identity provider: `token.actions.githubusercontent.com`
5. Audience: `sts.amazonaws.com`

#### Step 2: Add Condition
In the trust policy, add:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:jrysztv/binance-endpoints:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

## 🔧 GitHub Repository Setup

### Step 1: Create GitHub Repository
```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/jrysztv/binance-endpoints.git
git branch -M main
git push -u origin main
```

### Step 2: Configure GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

#### Required Secrets:
1. **AWS Credentials** (if using IAM User):
   - `AWS_ACCESS_KEY_ID`: Your AWS access key ID
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
   - `AWS_REGION`: `eu-west-1`

2. **EC2 Configuration**:
   - `EC2_HOST`: `63.35.236.42`
   - `EC2_USERNAME`: `ubuntu`
   - `EC2_APP_PATH`: `/opt/binance-endpoints`
   - `EC2_SECURITY_GROUP_ID`: `sg-0d4bddfc2a85814d2`

3. **SSH Key**:
   - `EC2_SSH_KEY_B64`: Base64 encoded private key (from your `ssh-key-base64.txt` file)

#### How to Set Up SSH Key Secret:
```bash
# Your base64 encoded key is already in ssh-key-base64.txt
# Copy the contents of that file to the EC2_SSH_KEY_B64 secret
cat ssh-key-base64.txt
```

### Step 3: Create Production Environment
1. Go to repository → Settings → Environments
2. Click "New environment"
3. Name: `production`
4. Add protection rules if desired (required reviewers, etc.)

## 🚀 EC2 Setup Commands

### Prepare EC2 for Deployment
SSH into your EC2 instance and run:

```bash
# SSH to EC2
ssh -i ~/.ssh/binance-endpoints.pem ubuntu@63.35.236.42

# Create application directory
sudo mkdir -p /opt/binance-endpoints
sudo chown ubuntu:ubuntu /opt/binance-endpoints

# Clone repository (you'll need to set up git credentials or use HTTPS)
cd /opt/binance-endpoints
git clone https://github.com/jrysztv/binance-endpoints.git .

# Make sure Docker and Docker Compose are working
docker --version
docker compose version
```

### Set up Git Credentials on EC2
Option A - HTTPS with Personal Access Token:
```bash
# Configure git with your credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# When prompted for password, use a Personal Access Token
# Create one at: https://github.com/settings/tokens
```

Option B - SSH Key:
```bash
# Generate SSH key on EC2
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add public key to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy this to GitHub → Settings → SSH and GPG keys

# Test SSH connection
ssh -T git@github.com
```

## 🧪 Testing the Setup

### 1. Test Local Docker Build
```bash
# In your local project directory
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Test endpoints
curl http://localhost/health
curl http://localhost/docs

# Clean up
docker-compose -f docker-compose.prod.yml down
```

### 2. Test GitHub Actions Locally (Optional)
Install `act` to test GitHub Actions locally:
```bash
# Install act (macOS)
brew install act

# Or download from: https://github.com/nektos/act

# Run tests locally
act -j test
```

### 3. Test AWS CLI Access
```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure set aws_access_key_id YOUR_ACCESS_KEY
aws configure set aws_secret_access_key YOUR_SECRET_KEY
aws configure set default.region eu-west-1

# Test EC2 access
aws ec2 describe-instances --instance-ids i-YOUR_INSTANCE_ID
```

## 🔒 Security Best Practices

1. **Principle of Least Privilege**: Only grant minimum required permissions
2. **Regular Key Rotation**: Rotate access keys every 90 days
3. **Monitor Usage**: Set up CloudTrail to monitor API usage
4. **Use IAM Roles**: Prefer IAM roles over access keys when possible
5. **Secure Secrets**: Never commit secrets to git

## 🐛 Troubleshooting

### Common Issues:

1. **SSH Permission Denied**:
   ```bash
   # Check key permissions
   chmod 600 ~/.ssh/binance-endpoints.pem
   
   # Verify key fingerprint
   ssh-keygen -l -f ~/.ssh/binance-endpoints.pem
   ```

2. **AWS Access Denied**:
   - Verify IAM policies are correctly attached
   - Check if access keys are correct
   - Ensure region matches (eu-west-1)

3. **Security Group Issues**:
   - Verify security group ID is correct
   - Check if GitHub Actions can modify security groups
   - Ensure the security group exists in the correct region

4. **Docker Issues on EC2**:
   ```bash
   # Restart Docker service
   sudo systemctl restart docker
   
   # Check Docker status
   sudo systemctl status docker
   
   # Add user to docker group
   sudo usermod -aG docker ubuntu
   newgrp docker
   ```

## 📋 Deployment Checklist

- [ ] AWS IAM User/Role created with correct permissions
- [ ] GitHub repository created and code pushed
- [ ] GitHub secrets configured
- [ ] EC2 instance accessible via SSH
- [ ] Application directory created on EC2 (/opt/binance-endpoints)
- [ ] Git repository cloned on EC2
- [ ] Docker and Docker Compose working on EC2
- [ ] Security group allows GitHub Actions IP ranges
- [ ] Local testing completed successfully

## 🎉 Ready to Deploy!

Once all the above is complete, push to the `main` branch to trigger your first deployment:

```bash
git add .
git commit -m "feat: add CI/CD pipeline"
git push origin main
```

Monitor the deployment in GitHub Actions: https://github.com/jrysztv/binance-endpoints/actions 