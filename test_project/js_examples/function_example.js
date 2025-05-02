/**
 * JavaScript Functions Example for InsightForge testing
 * Demonstrates various function types and JSDoc documentation
 */

/**
 * Calculate the sum of two numbers
 * @param {number} a - The first number
 * @param {number} b - The second number
 * @return {number} The sum of a and b
 */
function sum(a, b) {
  return a + b;
}

/**
 * Calculate the product of two numbers
 * @param {number} a - The first number
 * @param {number} b - The second number
 * @return {number} The product of a and b
 */
const multiply = function(a, b) {
  return a * b;
};

/**
 * Divide two numbers
 * @param {number} a - The numerator
 * @param {number} b - The denominator
 * @return {number} The result of a/b
 * @throws {Error} If b is zero
 */
const divide = (a, b) => {
  if (b === 0) {
    throw new Error('Division by zero');
  }
  return a / b;
};

/**
 * Calculate power using arrow function with implicit return
 * @param {number} base - The base number
 * @param {number} exponent - The exponent
 * @return {number} base raised to the power of exponent
 */
const power = (base, exponent) => base ** exponent;

/**
 * Format a value as currency
 * @param {number} value - The value to format
 * @param {string} [currency='USD'] - The currency code
 * @param {string} [locale='en-US'] - The locale
 * @return {string} The formatted currency string
 */
function formatCurrency(value, currency = 'USD', locale = 'en-US') {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency
  }).format(value);
}

/**
 * Async function that simulates fetching data
 * @async
 * @param {string} url - The URL to fetch data from
 * @return {Promise<Object>} The fetched data
 */
async function fetchData(url) {
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: 'Sample data', source: url });
    }, 100);
  });
}

/**
 * Generator function that yields a sequence of numbers
 * @generator
 * @param {number} count - How many numbers to generate
 * @yield {number} The next number in sequence
 */
function* numberGenerator(count) {
  for (let i = 1; i <= count; i++) {
    yield i;
  }
}

// Module exports
module.exports = {
  sum,
  multiply,
  divide,
  power,
  formatCurrency,
  fetchData,
  numberGenerator
};