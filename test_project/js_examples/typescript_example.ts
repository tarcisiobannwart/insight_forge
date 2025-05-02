/**
 * TypeScript Example for InsightForge testing
 * Demonstrates TypeScript-specific features like interfaces, types, and generics
 */

/**
 * Interface describing a user object
 */
interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  /** Creation date of the user account */
  createdAt?: Date;
}

/**
 * Enum for user roles
 */
enum UserRole {
  Admin = 'admin',
  Editor = 'editor',
  Viewer = 'viewer'
}

/**
 * Type for response status
 */
type ResponseStatus = 'success' | 'error' | 'pending';

/**
 * Generic repository interface for data access
 */
interface Repository<T> {
  findAll(): Promise<T[]>;
  findById(id: number): Promise<T | null>;
  create(item: Omit<T, 'id'>): Promise<T>;
  update(id: number, item: Partial<T>): Promise<T>;
  delete(id: number): Promise<boolean>;
}

/**
 * Implementation of the User repository
 */
class UserRepository implements Repository<User> {
  private users: User[] = [];
  private nextId: number = 1;

  /**
   * Find all users
   * @returns Promise resolving to array of users
   */
  async findAll(): Promise<User[]> {
    return [...this.users];
  }

  /**
   * Find a user by ID
   * @param id - The user ID to find
   * @returns Promise resolving to the user or null if not found
   */
  async findById(id: number): Promise<User | null> {
    const user = this.users.find(u => u.id === id);
    return user || null;
  }

  /**
   * Create a new user
   * @param item - The user data without ID
   * @returns Promise resolving to the created user with ID
   */
  async create(item: Omit<User, 'id'>): Promise<User> {
    const newUser: User = {
      ...item,
      id: this.nextId++,
      createdAt: new Date()
    };
    this.users.push(newUser);
    return newUser;
  }

  /**
   * Update a user
   * @param id - The user ID to update
   * @param item - The partial user data to update
   * @returns Promise resolving to the updated user
   */
  async update(id: number, item: Partial<User>): Promise<User> {
    const index = this.users.findIndex(u => u.id === id);
    if (index === -1) {
      throw new Error(`User with id ${id} not found`);
    }
    
    const updatedUser = {
      ...this.users[index],
      ...item
    };
    
    this.users[index] = updatedUser;
    return updatedUser;
  }

  /**
   * Delete a user
   * @param id - The user ID to delete
   * @returns Promise resolving to true if deleted, false otherwise
   */
  async delete(id: number): Promise<boolean> {
    const index = this.users.findIndex(u => u.id === id);
    if (index === -1) {
      return false;
    }
    
    this.users.splice(index, 1);
    return true;
  }
}

/**
 * Class for handling API responses
 */
class ApiResponse<T> {
  constructor(
    public readonly data: T | null,
    public readonly status: ResponseStatus,
    public readonly message?: string
  ) {}

  /**
   * Create a success response
   * @param data - The response data
   * @returns A new success ApiResponse
   */
  static success<U>(data: U): ApiResponse<U> {
    return new ApiResponse(data, 'success');
  }

  /**
   * Create an error response
   * @param message - The error message
   * @returns A new error ApiResponse
   */
  static error<U>(message: string): ApiResponse<U> {
    return new ApiResponse(null, 'error', message);
  }

  /**
   * Create a pending response
   * @returns A new pending ApiResponse
   */
  static pending<U>(): ApiResponse<U> {
    return new ApiResponse(null, 'pending', 'Operation in progress');
  }
}

/**
 * User service for handling user-related operations
 */
class UserService {
  constructor(private repository: Repository<User>) {}

  /**
   * Get all users
   * @returns Promise resolving to ApiResponse with users
   */
  async getUsers(): Promise<ApiResponse<User[]>> {
    try {
      const users = await this.repository.findAll();
      return ApiResponse.success(users);
    } catch (error) {
      return ApiResponse.error((error as Error).message);
    }
  }

  /**
   * Get a user by ID
   * @param id - The user ID
   * @returns Promise resolving to ApiResponse with user
   */
  async getUserById(id: number): Promise<ApiResponse<User>> {
    try {
      const user = await this.repository.findById(id);
      if (!user) {
        return ApiResponse.error(`User with id ${id} not found`);
      }
      return ApiResponse.success(user);
    } catch (error) {
      return ApiResponse.error((error as Error).message);
    }
  }

  /**
   * Create a new user
   * @param userData - The user data
   * @returns Promise resolving to ApiResponse with created user
   */
  async createUser(userData: Omit<User, 'id'>): Promise<ApiResponse<User>> {
    try {
      const user = await this.repository.create(userData);
      return ApiResponse.success(user);
    } catch (error) {
      return ApiResponse.error((error as Error).message);
    }
  }
}

// Export all types and classes
export {
  User,
  UserRole,
  ResponseStatus,
  Repository,
  UserRepository,
  ApiResponse,
  UserService
};