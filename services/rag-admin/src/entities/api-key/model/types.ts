// file: src/entities/api-key/model/types.ts

/**
 * Represents the core structure of an API Key as stored in the database
 * and returned by the API (without the raw key).
 */
export interface ApiKey {
  id: number;
  name: string;
  comment: string | null;
  is_active: boolean;
  key_hash: string;
  created_at: string; // ISO 8601 date string
  created_by: number;
}

/**
 * Defines the shape of the data required to create a new API key.
 * This is the payload sent to the backend.
 */
export type NewApiKey = Pick<ApiKey, 'name' | 'comment' | 'is_active'>;

/**
 * Represents the server's response immediately after creating a new API key.
 * It includes the raw, unhashed `api_key` which should be shown to the user once.
 */
export interface ApiKeyGenerated extends ApiKey {
  api_key: string;
}

/**
 * Defines the shape of the data for updating an existing API key.
 * All fields are optional.
 */
export interface ApiKeyUpdate {
  name?: string;
  comment?: string | null;
  is_active?: boolean;
}

/**
 * Describes the structure of a paginated API response for API keys.
 * This is the expected response from the server-side paginated GET endpoint.
 */
export interface PaginatedApiResponse {
  items: ApiKey[];
  total: number;
  page: number;
  size: number;
}