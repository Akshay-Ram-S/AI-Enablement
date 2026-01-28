# Web Scraper Demo - AWS Bedrock Agent

A Next.js application that demonstrates web scraping using AWS Bedrock Agent and Lambda functions.

## 🚀 Features

- **Modern UI**: Clean, responsive interface built with Next.js and Tailwind CSS
- **AWS Bedrock Agent Integration**: Leverages AWS Bedrock Agent for intelligent scraping
- **Lambda Backend**: Uses AWS Lambda for serverless web scraping
- **Real-time Processing**: Live scraping with loading states and error handling
- **Export Capabilities**: Copy to clipboard or download scraped content

## 📋 Prerequisites

- Node.js 18+ installed
- AWS Account with:
  - Bedrock Agent created and configured
  - Lambda function deployed with web scraper code
  - IAM user with appropriate permissions
- AWS Access Key and Secret Key

## 🛠️ Setup Instructions

### 1. Clone and Install Dependencies

```bash
cd web-scraper-demo
npm install
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your AWS credentials:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_SESSION_TOKEN=your_session_token_here  # Optional: Only needed for temporary credentials
AWS_REGION=us-east-1

# Bedrock Agent Configuration
BEDROCK_AGENT_ID=your_agent_id_here
BEDROCK_AGENT_ALIAS_ID=your_agent_alias_id_here
```

**Note on AWS Credentials:**
- **Permanent Credentials**: If using IAM user credentials, only `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are required
- **Temporary Credentials**: If using AWS STS, AWS SSO, or temporary credentials, you must also provide `AWS_SESSION_TOKEN`
- **Session Token Expiry**: Temporary credentials typically expire after 1-12 hours. You'll need to refresh them when they expire.

### 3. Test Your AWS Credentials

Before running the application, validate your AWS credentials:

```bash
npm install  # Install dependencies first
npm run test:credentials
```

This script will:
- ✓ Verify all required environment variables are set
- ✓ Validate credential format (AKIA for permanent, ASIA for temporary)
- ✓ Check for session token if using temporary credentials
- ✓ Test connectivity to AWS Bedrock
- ✓ Display a configuration summary

If the test passes, you'll see: **"All checks passed! ✓"**

### 4. Find Your Bedrock Agent Details

**To get your Agent ID and Alias ID:**

1. Go to AWS Console → Bedrock → Agents
2. Click on your agent
3. Copy the **Agent ID** (format: `XXXXXXXXXX`)
4. Go to **Aliases** tab
5. Copy the **Alias ID** (usually `TSTALIASID` for test or a custom alias)

### 5. Run the Application

Development mode:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

Production build:
```bash
npm run build
npm start
```

## 🏗️ Project Structure

```
web-scraper-demo/
├── app/
│   ├── api/
│   │   └── scrape/
│   │       └── route.ts          # API endpoint for Bedrock Agent
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Main page component
├── .env.local.example            # Environment template
├── .gitignore
├── next.config.js
├── package.json
├── postcss.config.js
└── tsconfig.json
```

## 🔑 AWS IAM Permissions

Your IAM user needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeAgent",
        "bedrock:InvokeAgentRuntime"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:agent/*",
        "arn:aws:bedrock:*:*:agent-alias/*"
      ]
    }
  ]
}
```

## 📝 How It Works

1. **User Input**: User enters a URL in the frontend
2. **API Request**: Frontend sends POST request to `/api/scrape`
3. **Bedrock Agent**: API route invokes AWS Bedrock Agent with the scraping request
4. **Lambda Execution**: Bedrock Agent triggers your Lambda function
5. **Web Scraping**: Lambda fetches and cleans the HTML content
6. **Response**: Cleaned text is returned through the chain back to the UI

## 🧪 Testing

Try these example URLs:
- `https://en.wikipedia.org/wiki/Portugal`
- `https://en.wikipedia.org/wiki/Artificial_intelligence`
- `https://www.python.org`

## 🐛 Troubleshooting

### "AWS session token has expired" error
- Temporary credentials (session tokens) expire after a set period
- Get fresh credentials from your AWS SSO portal or by running `aws sts get-session-token`
- Update all three values: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN`
- Restart the dev server after updating credentials

### "Invalid AWS credentials" error
- Verify all credentials are correct in `.env.local`
- If using temporary credentials, ensure `AWS_SESSION_TOKEN` is included
- Check for extra spaces or quotes in the `.env.local` file
- Verify the credentials haven't expired

### "Bedrock Agent configuration missing" error
- Check that all environment variables are set in `.env.local`
- Restart the dev server after changing environment variables

### "Failed to invoke Bedrock Agent" error
- Verify your AWS credentials are correct
- Check that your IAM user has the necessary permissions
- Ensure the Agent ID and Alias ID are correct
- Check that your Bedrock Agent is in "Prepared" state

### Scraping timeout or errors
- Some websites block scrapers - try different URLs
- Check your Lambda function logs in CloudWatch
- Verify the Lambda has proper permissions and timeout settings

### Environment variables not loading
- Make sure the file is named `.env.local` (not `.env.local.example`)
- Restart your Next.js dev server
- Verify variables don't have quotes around values

## 🔒 Security Notes

- **Never commit** `.env.local` to version control
- Use IAM roles instead of access keys in production
- Consider using AWS Secrets Manager for credentials
- Implement rate limiting for production deployments
- Add authentication/authorization for public deployments

## 🚀 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project in Vercel
3. Add environment variables in Vercel dashboard
4. Deploy

### AWS Amplify

1. Push code to GitHub
2. Connect repository in AWS Amplify
3. Add environment variables
4. Deploy

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t web-scraper-demo .
docker run -p 3000:3000 --env-file .env.local web-scraper-demo
```

## 📦 Dependencies

- **Next.js 15**: React framework
- **@aws-sdk/client-bedrock-agent-runtime**: AWS Bedrock SDK
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Type safety

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this project for your own purposes.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review CloudWatch logs for Lambda errors
3. Verify Bedrock Agent configuration
4. Check AWS service health status

## 🎯 Next Steps

- Add user authentication
- Implement caching for frequently scraped URLs
- Add support for multiple concurrent scraping requests
- Create a history/favorites feature
- Add data extraction patterns (emails, phone numbers, etc.)
- Implement webhook notifications for long-running scrapes
