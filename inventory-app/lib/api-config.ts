/**
 * API Configuration
 * Centralized API endpoint configuration for the application
 */

// Get the API URL from environment variable or fallback to localhost
export const API_URL = 
  process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:8080'
    : ''); // Will use relative URLs in production if not set

export const API_ENDPOINTS = {
  health: `${API_URL}/health`,
  processInventory: `${API_URL}/api/process-inventory`,
  generateShoppingList: `${API_URL}/api/generate-shopping-list`,
  resetGroceryList: `${API_URL}/api/reset-grocery-list`,
} as const;

// Helper function to get full API URL
export function getApiUrl(endpoint: keyof typeof API_ENDPOINTS): string {
  return API_ENDPOINTS[endpoint];
}
