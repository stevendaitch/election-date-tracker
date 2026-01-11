/**
 * Shared utility functions for election date calculations
 */

/**
 * Calculate days until a given date
 * @param {string} dateStr - Date in YYYY-MM-DD format
 * @returns {number} Days until the date (negative if in past)
 */
export function daysUntil(dateStr) {
  const target = new Date(dateStr + 'T00:00:00')
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const diff = target - today
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}

/**
 * Format a date string for display
 * @param {string} dateStr - Date in YYYY-MM-DD format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatDate(dateStr, options = {}) {
  const defaultOptions = {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    ...options
  }
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('en-US', defaultOptions)
}

/**
 * Format date with weekday
 * @param {string} dateStr - Date in YYYY-MM-DD format
 * @returns {string} Formatted date with weekday
 */
export function formatDateLong(dateStr) {
  return formatDate(dateStr, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
}

/**
 * Format date for timeline display
 * @param {string} dateStr - Date in YYYY-MM-DD format
 * @returns {string} Formatted date with short weekday
 */
export function formatDateTimeline(dateStr) {
  return formatDate(dateStr, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

/**
 * Get color based on days until election (National Parks palette)
 * @param {number} days - Days until election
 * @returns {string} Hex color code
 */
export function getColorByDays(days) {
  if (days <= 30) return "#C65D3D"   // rust - imminent
  if (days <= 60) return "#D4A574"   // amber - soon
  if (days <= 90) return "#8B7355"   // warm brown - approaching
  if (days <= 180) return "#3D7A52"  // forest light - months away
  return "#2D5A3D"                    // forest - far out
}
