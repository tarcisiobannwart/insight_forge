/**
 * JavaScript example for InsightForge testing
 * Demonstrates classes, methods, properties, and inheritance
 */

/**
 * Base class representing a generic Shape
 * @class
 */
class Shape {
  /**
   * Create a shape
   * @param {string} color - The color of the shape
   */
  constructor(color) {
    this.color = color;
    this._privateField = 'internal';
  }

  /**
   * Get the color of the shape
   * @return {string} The color
   */
  getColor() {
    return this.color;
  }

  /**
   * Set the color of the shape
   * @param {string} color - The new color
   */
  setColor(color) {
    this.color = color;
  }

  /**
   * Calculate the area of the shape - abstract method to be implemented by subclasses
   * @abstract
   * @return {number} The area of the shape
   */
  calculateArea() {
    throw new Error('Method calculateArea() must be implemented by subclasses');
  }

  /**
   * Static method to create a default shape
   * @static
   * @return {Shape} A default shape instance
   */
  static createDefault() {
    return new Shape('black');
  }
}

/**
 * Class representing a Circle, extends Shape
 * @class
 * @extends Shape
 */
class Circle extends Shape {
  /**
   * Create a circle
   * @param {string} color - The color of the circle
   * @param {number} radius - The radius of the circle
   */
  constructor(color, radius) {
    super(color);
    this.radius = radius;
  }

  /**
   * Calculate the area of the circle
   * @override
   * @return {number} The area of the circle
   */
  calculateArea() {
    return Math.PI * this.radius * this.radius;
  }

  /**
   * Calculate the circumference of the circle
   * @return {number} The circumference
   */
  calculateCircumference() {
    return 2 * Math.PI * this.radius;
  }
}

/**
 * Class representing a Rectangle, extends Shape
 * @class
 * @extends Shape
 */
class Rectangle extends Shape {
  /**
   * Create a rectangle
   * @param {string} color - The color of the rectangle
   * @param {number} width - The width of the rectangle
   * @param {number} height - The height of the rectangle
   */
  constructor(color, width, height) {
    super(color);
    this.width = width;
    this.height = height;
  }

  /**
   * Calculate the area of the rectangle
   * @override
   * @return {number} The area of the rectangle
   */
  calculateArea() {
    return this.width * this.height;
  }

  /**
   * Calculate the perimeter of the rectangle
   * @return {number} The perimeter
   */
  calculatePerimeter() {
    return 2 * (this.width + this.height);
  }
}

/**
 * Factory for creating shapes
 */
const ShapeFactory = {
  /**
   * Create a shape of the specified type
   * @param {string} type - The type of shape to create ('circle' or 'rectangle')
   * @param {Object} options - The options for the shape
   * @return {Shape} The created shape
   */
  createShape(type, options) {
    switch (type) {
      case 'circle':
        return new Circle(options.color || 'blue', options.radius || 1);
      case 'rectangle':
        return new Rectangle(options.color || 'red', options.width || 1, options.height || 1);
      default:
        throw new Error(`Unknown shape type: ${type}`);
    }
  }
};

// Export the classes and factory
module.exports = {
  Shape,
  Circle,
  Rectangle,
  ShapeFactory
};