/**
 * Date utility functions for handling travel dates
 * Ensures dates are parsed correctly without timezone issues
 */

/**
 * Parse a YYYY-MM-DD date string as a local date (not UTC)
 * This prevents the "day before" issue when displaying dates
 */
export function parseLocalDate(dateString: string): Date {
  if (!dateString || dateString === 'TBD') {
    return new Date(); // fallback to current date
  }
  
  // Handle YYYY-MM-DD format
  const [year, month, day] = dateString.split('-').map(Number);
  if (year && month && day) {
    return new Date(year, month - 1, day); // month is 0-indexed
  }
  
  // Fallback to standard parsing if format is different
  return new Date(dateString);
}

/**
 * Format a date string for display
 */
export function formatTravelDate(dateString: string, options?: Intl.DateTimeFormatOptions): string {
  if (!dateString || dateString === 'TBD') {
    return 'TBD';
  }
  
  const date = parseLocalDate(dateString);
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  };
  
  return date.toLocaleDateString('en-US', options || defaultOptions);
}

/**
 * Calculate duration between two date strings
 */
export function calculateTripDuration(startDate: string, endDate: string): string {
  if (!startDate || !endDate || startDate === 'TBD' || endDate === 'TBD') {
    return 'Duration TBD';
  }
  
  const start = parseLocalDate(startDate);
  const end = parseLocalDate(endDate);
  const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
  
  return days === 1 ? '1 day' : `${days} days`;
}

/**
 * Check if a date string is valid
 */
export function isValidDate(dateString: string): boolean {
  if (!dateString || dateString === 'TBD') {
    return false;
  }
  
  const date = parseLocalDate(dateString);
  return !isNaN(date.getTime());
}