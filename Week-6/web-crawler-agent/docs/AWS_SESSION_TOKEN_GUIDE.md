# AWS Session Token Guide

This guide explains how to work with AWS session tokens for temporary credentials.

## What are Session Tokens?

AWS session tokens are used with **temporary security credentials** obtained through:
- AWS Security Token Service (STS)
- AWS Single Sign-On (SSO)
- IAM Role assumptions
- Federation

Unlike permanent IAM user credentials, temporary credentials include a session token and expire after a set period.

## When Do You Need a Session Token?

### ✅ You NEED a session token if:
- Your Access Key ID starts with `ASIA` (temporary credentials)
- You're using AWS SSO
- You're assuming an IAM role
- You obtained credentials via `aws sts get-session-token`
- You're using AWS CLI profiles with role assumption

### ❌ You DON'T need a session token if:
- Your Access Key ID starts with `AKIA` (permanent credentials)
- You're using long-term IAM user credentials
- You created credentials in IAM Console → Users → Security Credentials

## How to Get Temporary Credentials

### Method 1: AWS CLI (For IAM Users with MFA)

```bash
aws sts get-session-token \
  --serial-number arn:aws:iam::ACCOUNT_ID:mfa/USERNAME \
  --token-code MFA_CODE \
  --duration-seconds 43200
```

Output:
```json
{
  "Credentials": {
    "AccessKeyId": "ASIA...",
    "SecretAccessKey": "...",
    "SessionToken": "...",
    "Expiration": "2024-01-29T12:00:00Z"
  }
}
```

### Method 2: AWS SSO

```bash
# Login to SSO
aws sso login --profile your-profile

# Get credentials
aws configure export-credentials --profile your-profile
```

### Method 3: Assume Role

```bash
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME \
  --role-session-name my-session
```

### Method 4: AWS Console (SSO)

1. Log in to AWS SSO portal
2. Click on your account
3. Click "Command line or programmatic access"
4. Copy the credentials shown (includes session token)

## Setting Up in `.env.local`

### For Temporary Credentials (with Session Token)

```env
AWS_ACCESS_KEY_ID=ASIA...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjEJ...  # Long base64 string
AWS_REGION=us-east-1
```

### For Permanent Credentials (IAM User)

```env
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
# No AWS_SESSION_TOKEN needed
AWS_REGION=us-east-1
```

## Session Token Expiration

Temporary credentials expire after:
- **Default**: 1 hour
- **Maximum**: 12 hours (for IAM users)
- **Maximum**: 1 hour (for assumed roles)

### What Happens When Credentials Expire?

You'll see errors like:
```
ExpiredTokenException: The security token included in the request is expired
```

### How to Refresh Expired Credentials

1. **AWS SSO**: Run `aws sso login --profile your-profile`
2. **STS**: Run the `aws sts get-session-token` command again
3. **Update `.env.local`**: Replace all three values (AccessKeyId, SecretAccessKey, SessionToken)
4. **Restart server**: Run `npm run dev` again

## Troubleshooting

### Error: "Session token required for temporary credentials"

Your Access Key starts with `ASIA` but no session token is provided.

**Solution:**
```env
# Add the session token to .env.local
AWS_SESSION_TOKEN=your_session_token_here
```

### Error: "Invalid signature"

Your credentials are incorrect or malformed.

**Solution:**
1. Verify you copied all three values correctly
2. Check for extra spaces or line breaks
3. Ensure the session token is complete (they're very long)

### Error: "The security token included in the request is expired"

Your temporary credentials have expired.

**Solution:**
1. Get fresh credentials (see "How to Get Temporary Credentials" above)
2. Update all three values in `.env.local`
3. Restart the server: `npm run dev`

## Best Practices

### ✅ DO:
- Use permanent IAM user credentials for development if possible (simpler)
- Set appropriate expiration times for temporary credentials
- Refresh credentials before they expire
- Use AWS SSO for production environments
- Store credentials in `.env.local` (gitignored)

### ❌ DON'T:
- Commit credentials to version control
- Share session tokens
- Use temporary credentials in automated systems without refresh logic
- Set overly long expiration times (security risk)

## Using with This Application

### Step 1: Test Your Credentials

```bash
npm run test:credentials
```

This validates:
- ✓ All required environment variables are set
- ✓ Credential format is correct
- ✓ Session token is present if needed
- ✓ Credentials can connect to AWS

### Step 2: Run the Application

```bash
npm run dev
```

### Step 3: Monitor for Expiration

Watch for these signs:
- API calls start failing
- Error messages about expired tokens
- Timestamp in AWS Console shows credentials expired

### Step 4: Refresh When Needed

1. Get new credentials
2. Update `.env.local`
3. Restart: `npm run dev`

## Production Considerations

For production deployments:

### Option 1: Use IAM Roles (Recommended)
- Deploy to AWS (ECS, Lambda, EC2)
- Attach IAM role to the resource
- No credentials needed in environment variables
- AWS automatically rotates credentials

### Option 2: Use Secrets Manager
- Store credentials in AWS Secrets Manager
- Application fetches credentials at runtime
- Automatic rotation support

### Option 3: Use Environment Variables
- For services like Vercel, Heroku, etc.
- Use permanent credentials (AKIA) if possible
- Or implement automatic credential refresh

## Example: Credential Refresh Script

For long-running applications:

```javascript
// refresh-credentials.js
const { STSClient, GetSessionTokenCommand } = require("@aws-sdk/client-sts");
const fs = require('fs');

async function refreshCredentials() {
  const sts = new STSClient({ region: "us-east-1" });
  
  const command = new GetSessionTokenCommand({
    DurationSeconds: 43200, // 12 hours
  });
  
  const response = await sts.send(command);
  
  // Update .env.local
  const envContent = `
AWS_ACCESS_KEY_ID=${response.Credentials.AccessKeyId}
AWS_SECRET_ACCESS_KEY=${response.Credentials.SecretAccessKey}
AWS_SESSION_TOKEN=${response.Credentials.SessionToken}
  `.trim();
  
  fs.writeFileSync('.env.local', envContent);
  console.log('Credentials refreshed!');
}

refreshCredentials();
```

## Additional Resources

- [AWS STS Documentation](https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html)
- [AWS SSO Documentation](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

## Quick Reference

| Credential Type | Access Key Prefix | Needs Session Token? | Expires? |
|----------------|-------------------|---------------------|----------|
| IAM User (Permanent) | AKIA | ❌ No | ❌ No |
| Temporary (STS/SSO) | ASIA | ✅ Yes | ✅ Yes (1-12 hrs) |

## Need Help?

Run the credential test script:
```bash
npm run test:credentials
```

It will diagnose common issues and provide specific guidance.
