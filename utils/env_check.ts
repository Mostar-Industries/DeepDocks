/**
 * DeepCAL++ Environment Validation Utility
 * This module provides functions to validate environment variables
 */

/**
 * Validate required environment variables
 * @returns Object with validation results
 */
export function validateEnv(): {
  valid: boolean
  missing: string[]
  message: string
} {
  const requiredEnvVars = ["DEEPCAL_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]

  const optionalEnvVars = ["SUPABASE_SERVICE_KEY", "VOICE_ENABLED", "DATA_DIRECTORY", "LOG_LEVEL"]

  const missing = requiredEnvVars.filter((envVar) => !process.env[envVar])

  const present = requiredEnvVars.filter((envVar) => !!process.env[envVar])

  const optional = optionalEnvVars.filter((envVar) => !!process.env[envVar])

  const valid = missing.length === 0

  return {
    valid,
    missing,
    message: valid
      ? `All required environment variables are set (${present.length}/${requiredEnvVars.length} required, ${optional.length}/${optionalEnvVars.length} optional)`
      : `Missing required environment variables: ${missing.join(", ")}`,
  }
}

/**
 * Check if environment variables are valid
 * @param throwError Whether to throw an error if validation fails
 * @returns True if all required environment variables are set, false otherwise
 */
export function checkEnv(throwError = false): boolean {
  const result = validateEnv()

  if (!result.valid && throwError) {
    throw new Error(result.message)
  }

  return result.valid
}

/**
 * Get environment variable with fallback
 * @param key Environment variable key
 * @param defaultValue Default value if environment variable is not set
 * @returns Environment variable value or default value
 */
export function getEnv(key: string, defaultValue = ""): string {
  return process.env[key] || defaultValue
}

/**
 * Get boolean environment variable
 * @param key Environment variable key
 * @param defaultValue Default value if environment variable is not set
 * @returns Boolean value of environment variable
 */
export function getBoolEnv(key: string, defaultValue = false): boolean {
  const value = process.env[key]

  if (value === undefined || value === null) {
    return defaultValue
  }

  return ["true", "1", "yes", "y"].includes(value.toLowerCase())
}

/**
 * Get numeric environment variable
 * @param key Environment variable key
 * @param defaultValue Default value if environment variable is not set
 * @returns Numeric value of environment variable
 */
export function getNumEnv(key: string, defaultValue = 0): number {
  const value = process.env[key]

  if (value === undefined || value === null) {
    return defaultValue
  }

  const num = Number(value)
  return isNaN(num) ? defaultValue : num
}

