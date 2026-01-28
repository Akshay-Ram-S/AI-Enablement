/**
 * AWS Credentials Helper
 * 
 * This utility helps manage AWS credentials including temporary session tokens.
 * It validates credentials and provides helpful error messages.
 */

export interface AWSCredentials {
  accessKeyId: string;
  secretAccessKey: string;
  sessionToken?: string;
  region: string;
}

export class CredentialsValidator {
  /**
   * Validates that all required AWS credentials are present
   */
  static validate(): { valid: boolean; error?: string; credentials?: AWSCredentials } {
    const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
    const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;
    const sessionToken = process.env.AWS_SESSION_TOKEN;
    const region = process.env.AWS_REGION || 'us-east-1';

    // Check required credentials
    if (!accessKeyId || !secretAccessKey) {
      return {
        valid: false,
        error: 'Missing required AWS credentials. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env.local file.'
      };
    }

    // Validate format
    if (!accessKeyId.startsWith('AKIA') && !accessKeyId.startsWith('ASIA')) {
      return {
        valid: false,
        error: 'Invalid AWS_ACCESS_KEY_ID format. It should start with AKIA (permanent) or ASIA (temporary).'
      };
    }

    // Check if temporary credentials
    const isTemporary = accessKeyId.startsWith('ASIA');
    if (isTemporary && !sessionToken) {
      return {
        valid: false,
        error: 'Temporary credentials detected (starts with ASIA) but AWS_SESSION_TOKEN is missing. Please provide the session token.'
      };
    }

    const credentials: AWSCredentials = {
      accessKeyId,
      secretAccessKey,
      region,
    };

    if (sessionToken) {
      credentials.sessionToken = sessionToken;
    }

    return {
      valid: true,
      credentials,
    };
  }

  /**
   * Gets credentials object for AWS SDK
   */
  static getCredentials(): AWSCredentials | null {
    const validation = this.validate();
    return validation.valid ? validation.credentials! : null;
  }

  /**
   * Checks if credentials are temporary (STS/SSO)
   */
  static isTemporary(): boolean {
    const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
    return accessKeyId ? accessKeyId.startsWith('ASIA') : false;
  }

  /**
   * Gets a helpful error message for credential issues
   */
  static getErrorMessage(): string | null {
    const validation = this.validate();
    return validation.valid ? null : validation.error!;
  }
}

/**
 * Helper to create AWS credentials object
 */
export function getAWSCredentials() {
  const credentials: any = {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  };

  // Add session token if available (for temporary credentials)
  if (process.env.AWS_SESSION_TOKEN) {
    credentials.sessionToken = process.env.AWS_SESSION_TOKEN;
  }

  return credentials;
}

/**
 * Helper to check if AWS credentials are configured
 */
export function hasAWSCredentials(): boolean {
  return !!(process.env.AWS_ACCESS_KEY_ID && process.env.AWS_SECRET_ACCESS_KEY);
}

/**
 * Helper to get AWS region
 */
export function getAWSRegion(): string {
  return process.env.AWS_REGION || 'us-east-1';
}

/**
 * Print credential status for debugging (without exposing secrets)
 */
export function debugCredentialStatus(): void {
  console.log('AWS Credentials Status:');
  console.log('- Access Key ID:', process.env.AWS_ACCESS_KEY_ID ? '✓ Set' : '✗ Missing');
  console.log('- Secret Access Key:', process.env.AWS_SECRET_ACCESS_KEY ? '✓ Set' : '✗ Missing');
  console.log('- Session Token:', process.env.AWS_SESSION_TOKEN ? '✓ Set (Temporary)' : '✗ Not Set (Permanent)');
  console.log('- Region:', getAWSRegion());
  console.log('- Credential Type:', CredentialsValidator.isTemporary() ? 'Temporary (STS/SSO)' : 'Permanent (IAM User)');
}
