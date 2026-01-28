import { BedrockAgentRuntimeClient, InvokeAgentCommand } from "@aws-sdk/client-bedrock-agent-runtime";
import { NextRequest, NextResponse } from "next/server";
import { getAWSCredentials, getAWSRegion, CredentialsValidator } from "@/utils/aws-credentials";

// Initialize Bedrock Agent Runtime Client
const getClient = () => {
  return new BedrockAgentRuntimeClient({
    region: getAWSRegion(),
    credentials: getAWSCredentials(),
  });
};

export async function POST(request: NextRequest) {
  try {
    // Validate credentials first
    const credentialValidation = CredentialsValidator.validate();
    if (!credentialValidation.valid) {
      return NextResponse.json(
        { error: credentialValidation.error },
        { status: 500 }
      );
    }

    const { message } = await request.json();

    if (!message) {
      return NextResponse.json(
        { error: "Message is required" },
        { status: 400 }
      );
    }

    const agentId = process.env.BEDROCK_AGENT_ID;
    const agentAliasId = process.env.BEDROCK_AGENT_ALIAS_ID;

    if (!agentId || !agentAliasId) {
      return NextResponse.json(
        { error: "Bedrock Agent configuration missing. Please set BEDROCK_AGENT_ID and BEDROCK_AGENT_ALIAS_ID in your .env.local file." },
        { status: 500 }
      );
    }

    // Generate a unique session ID
    const sessionId = `session-${Date.now()}-${Math.random().toString(36).substring(7)}`;

    const client = getClient();

    const command = new InvokeAgentCommand({
      agentId,
      agentAliasId,
      sessionId,
      inputText: message,
    });

    console.log(`Invoking Bedrock Agent: ${agentId} (Alias: ${agentAliasId})`);
    console.log(`Session ID: ${sessionId}`);
    console.log(`Using ${CredentialsValidator.isTemporary() ? 'temporary' : 'permanent'} credentials`);

    const response = await client.send(command);

    // Process the streaming response
    let fullResponse = "";
    let trace: any[] = [];

    if (response.completion) {
      for await (const event of response.completion) {
        if (event.chunk) {
          const chunk = event.chunk;
          
          // Extract text from chunk
          if (chunk.bytes) {
            const decodedChunk = new TextDecoder().decode(chunk.bytes);
            fullResponse += decodedChunk;
          }
        }

        // Collect trace information
        if (event.trace) {
          trace.push(event.trace);
        }
      }
    }

    console.log(`Response received: ${fullResponse.length} characters`);

    return NextResponse.json({
      response: fullResponse,
      trace,
      sessionId,
      credentialType: CredentialsValidator.isTemporary() ? 'temporary' : 'permanent',
    });

  } catch (error: any) {
    console.error("Bedrock Agent Error:", error);
    
    // Provide more specific error messages
    let errorMessage = error.message || "Failed to invoke Bedrock Agent";
    let suggestion = "";
    
    // Check for common AWS errors
    if (error.name === "InvalidSignatureException") {
      errorMessage = "Invalid AWS credentials signature";
      suggestion = "Please check that your AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN (if using temporary credentials) are correct.";
    } else if (error.name === "ExpiredTokenException") {
      errorMessage = "AWS session token has expired";
      suggestion = "Your temporary credentials have expired. Please refresh them from your AWS SSO portal or by running 'aws sts get-session-token' and update your .env.local file.";
    } else if (error.name === "AccessDeniedException") {
      errorMessage = "Access denied to Bedrock Agent";
      suggestion = "Please verify that your IAM user/role has the 'bedrock:InvokeAgent' permission for this agent.";
    } else if (error.name === "ResourceNotFoundException") {
      errorMessage = "Bedrock Agent not found";
      suggestion = "Please verify that your BEDROCK_AGENT_ID and BEDROCK_AGENT_ALIAS_ID are correct and the agent exists in your AWS account.";
    } else if (error.name === "ValidationException") {
      errorMessage = "Invalid request parameters";
      suggestion = "Please check that your Agent ID and Alias ID are in the correct format.";
    }

    return NextResponse.json(
      { 
        error: errorMessage,
        suggestion,
        errorType: error.name,
        details: error.toString(),
        credentialType: CredentialsValidator.isTemporary() ? 'temporary' : 'permanent',
      },
      { status: 500 }
    );
  }
}
