# React Style Guide

> **For AI Assistants**: This guide outlines best practices for React/TypeScript development, including component patterns, state management, and UI implementation. All patterns include validation rules and implementation guidance for modern React development.

## AI Metadata

**Template Version:** 2.0
**AI Processing Level:** High
**Required Context:** React, TypeScript, Tailwind CSS, modern frontend development
**Validation Required:** Yes
**Code Generation:** Supported

**Dependencies:**
- `../Core%20Principles.md` - Decision-making frameworks
- `../Language-Specific/Python%20Testing%20Guide.md` - Testing patterns
- `../../project_context/Architecture%20Overview.md` - System architecture
- `../../project_context/Common%20Patterns.md` - Project-specific patterns

**Validation Rules:**
- All components must use TypeScript with proper type definitions
- Components must follow single responsibility principle
- State management must use appropriate React patterns
- Styling must use Tailwind CSS with proper organization
- All components must include proper error handling and loading states

## Overview

**Document Purpose:** React/TypeScript development standards and best practices for the CreamPie project
**Scope:** Component development, state management, styling, testing, and performance optimization
**Target Users:** AI assistants and developers building React applications
**Last Updated:** Current

**AI Context:** This guide provides the foundational React patterns that must be followed for all frontend development in the project. It ensures maintainable, performant, and accessible React applications.

## 1. Component Structure

### File Organization
- Place components in the `src/components` directory
- Place pages in the `src/pages` directory
- Use PascalCase for component file names (e.g., `Navbar.tsx`, `LandingPage.tsx`)

**Code Generation Hint**: This organization will inform all component file placement and naming conventions.

**Validation**: All components must follow this file organization structure.

### Component Naming
- Use PascalCase for component names
- Use descriptive names that indicate the component's purpose
- Prefix page components with the page name (e.g., `LandingPage`)

**Code Generation Hint**: This naming convention will inform all component naming decisions.

**Validation**: All component names must follow PascalCase and be descriptive.

### Component Structure Patterns
```tsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { OtherComponent } from "../components/OtherComponent";

interface ComponentNameProps {
  title: string;
  isActive?: boolean;
  onAction?: (value: string) => void;
}

export function ComponentName({ title, isActive = false, onAction }: ComponentNameProps) {
  const [localState, setLocalState] = useState<string>("");

  useEffect(() => {
    // Component initialization logic
    console.log("Component mounted");

    return () => {
      // Cleanup logic
      console.log("Component unmounted");
    };
  }, []);

  const handleClick = () => {
    if (onAction) {
      onAction(localState);
    }
  };

  return (
    <div className="
      // Layout
      flex items-center justify-between

      // Box model
      p-4 m-2

      // Visual
      bg-white shadow-sm rounded-lg

      // Typography
      text-gray-900

      // Transitions
      transition-colors duration-200

      // Conditional styling
      hover:bg-gray-50
      ${isActive ? 'border-blue-500' : 'border-gray-200'}
    ">
      <h2 className="text-xl font-semibold">{title}</h2>
      <button
        onClick={handleClick}
        className="
          px-4 py-2
          bg-blue-500 text-white
          rounded-md
          hover:bg-blue-600
          transition-colors duration-200
        "
      >
        Action
      </button>
    </div>
  );
}
```

**Code Generation Hint**: This component pattern will inform all React component implementation with proper TypeScript and styling.

**Validation**: All components must include proper TypeScript interfaces, error handling, and Tailwind CSS organization.

### Import Considerations
- @import must precede all other statements (besides @charset or empty @layer)
- The first import should always be `import * as React from "react";`, if needed.
- `// @ts-expect-error - React is needed for JSX` should always be above it.

**Code Generation Hint**: This import pattern will inform all component import organization.

**Validation**: All imports must follow this organization pattern.

## 2. TypeScript Patterns

### Type Definitions
```tsx
// Common type definitions
export interface User {
  id: number;
  email: string;
  username: string;
  isActive: boolean;
  createdAt: string;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  perPage: number;
  totalPages: number;
}

// Component prop types
export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  className?: string;
}

// Form types
export interface FormData {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}
```

**Code Generation Hint**: This type pattern will inform all TypeScript type definition implementation.

**Validation**: All components must include proper TypeScript interfaces and type definitions.

### Hook Patterns
```tsx
import { useState, useEffect, useCallback, useMemo } from 'react';

// Custom hook for API calls
export function useApiCall<T>(
  apiFunction: () => Promise<T>,
  dependencies: React.DependencyList = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

// Custom hook for form management
export function useForm<T extends Record<string, any>>(initialValues: T) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});

  const handleChange = useCallback((name: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  }, [errors]);

  const handleSubmit = useCallback((onSubmit: (values: T) => void) => {
    return (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit(values);
    };
  }, [values]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
  }, [initialValues]);

  return {
    values,
    errors,
    handleChange,
    handleSubmit,
    reset,
    setErrors
  };
}
```

**Code Generation Hint**: This hook pattern will inform all custom hook implementation with proper TypeScript and error handling.

**Validation**: All custom hooks must include proper TypeScript types and error handling.

## 3. State Management

### Component State
```tsx
import React, { useState, useReducer, useCallback } from 'react';

// Simple state management
export function SimpleStateComponent() {
  const [count, setCount] = useState<number>(0);
  const [isVisible, setIsVisible] = useState<boolean>(true);

  const increment = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);

  const toggleVisibility = useCallback(() => {
    setIsVisible(prev => !prev);
  }, []);

  return (
    <div className="p-4">
      {isVisible && (
        <div className="text-center">
          <h2 className="text-2xl font-bold">Count: {count}</h2>
          <button
            onClick={increment}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Increment
          </button>
        </div>
      )}
      <button
        onClick={toggleVisibility}
        className="mt-4 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
      >
        {isVisible ? 'Hide' : 'Show'}
      </button>
    </div>
  );
}

// Complex state management with useReducer
interface TodoState {
  todos: Todo[];
  filter: 'all' | 'active' | 'completed';
  loading: boolean;
}

interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

type TodoAction =
  | { type: 'ADD_TODO'; payload: string }
  | { type: 'TOGGLE_TODO'; payload: number }
  | { type: 'SET_FILTER'; payload: 'all' | 'active' | 'completed' }
  | { type: 'SET_LOADING'; payload: boolean };

function todoReducer(state: TodoState, action: TodoAction): TodoState {
  switch (action.type) {
    case 'ADD_TODO':
      return {
        ...state,
        todos: [...state.todos, {
          id: Date.now(),
          text: action.payload,
          completed: false
        }]
      };
    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload
            ? { ...todo, completed: !todo.completed }
            : todo
        )
      };
    case 'SET_FILTER':
      return { ...state, filter: action.payload };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
}

export function TodoList() {
  const [state, dispatch] = useReducer(todoReducer, {
    todos: [],
    filter: 'all',
    loading: false
  });
  const [newTodo, setNewTodo] = useState<string>('');

  const addTodo = useCallback(() => {
    if (newTodo.trim()) {
      dispatch({ type: 'ADD_TODO', payload: newTodo.trim() });
      setNewTodo('');
    }
  }, [newTodo]);

  const filteredTodos = useMemo(() => {
    switch (state.filter) {
      case 'active':
        return state.todos.filter(todo => !todo.completed);
      case 'completed':
        return state.todos.filter(todo => todo.completed);
      default:
        return state.todos;
    }
  }, [state.todos, state.filter]);

  return (
    <div className="max-w-md mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Todo List</h1>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addTodo()}
          placeholder="Add new todo..."
          className="flex-1 px-3 py-2 border rounded"
        />
        <button
          onClick={addTodo}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Add
        </button>
      </div>

      <div className="flex gap-2 mb-4">
        {(['all', 'active', 'completed'] as const).map(filter => (
          <button
            key={filter}
            onClick={() => dispatch({ type: 'SET_FILTER', payload: filter })}
            className={`px-3 py-1 rounded ${
              state.filter === filter
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {filter.charAt(0).toUpperCase() + filter.slice(1)}
          </button>
        ))}
      </div>

      <ul className="space-y-2">
        {filteredTodos.map(todo => (
          <li
            key={todo.id}
            className="flex items-center gap-2 p-2 border rounded"
          >
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => dispatch({ type: 'TOGGLE_TODO', payload: todo.id })}
              className="rounded"
            />
            <span className={todo.completed ? 'line-through text-gray-500' : ''}>
              {todo.text}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**Code Generation Hint**: This state management pattern will inform all React state implementation with proper TypeScript and performance optimization.

**Validation**: All state management must use appropriate React patterns and include proper TypeScript types.

## 4. Styling with Tailwind CSS

### Class Organization
- Group related classes together
- Use consistent spacing between class groups
- Follow this order:
  1. Layout (display, position, etc.)
  2. Box model (margin, padding, etc.)
  3. Visual (colors, backgrounds, etc.)
  4. Typography
  5. Transitions/Animations

**Code Generation Hint**: This class organization will inform all Tailwind CSS implementation.

**Validation**: All Tailwind classes must follow this organization pattern.

### Component Styling Patterns
```tsx
// Reusable style components
const buttonVariants = {
  primary: "bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-500",
  secondary: "bg-gray-500 text-white hover:bg-gray-600 focus:ring-gray-500",
  danger: "bg-red-500 text-white hover:bg-red-600 focus:ring-red-500",
  outline: "border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500"
};

const buttonSizes = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-base",
  lg: "px-6 py-3 text-lg"
};

interface ButtonProps {
  children: React.ReactNode;
  variant?: keyof typeof buttonVariants;
  size?: keyof typeof buttonSizes;
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  className?: string;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  className = ''
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        // Layout
        inline-flex items-center justify-center

        // Box model
        ${buttonSizes[size]}

        // Visual
        ${buttonVariants[variant]}
        rounded-md font-medium

        // Typography
        font-medium

        // Transitions
        transition-colors duration-200

        // States
        focus:outline-none focus:ring-2 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed

        // Custom classes
        ${className}
      `}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )}
      {children}
    </button>
  );
}
```

**Code Generation Hint**: This styling pattern will inform all component styling implementation with reusable variants.

**Validation**: All component styling must use consistent patterns and include proper state handling.

### Responsive Design
```tsx
// Responsive component example
export function ResponsiveCard() {
  return (
    <div className="
      // Layout - responsive grid
      grid grid-cols-1
      sm:grid-cols-2
      lg:grid-cols-3
      xl:grid-cols-4

      // Box model - responsive spacing
      gap-4
      p-4
      sm:p-6
      lg:p-8

      // Visual
      bg-white shadow-lg rounded-lg

      // Typography - responsive text sizes
      text-sm
      sm:text-base
      lg:text-lg
    ">
      <div className="
        // Layout
        flex flex-col

        // Box model
        p-4
        sm:p-6

        // Visual
        bg-gray-50 rounded-lg

        // Typography
        text-center
      ">
        <h3 className="
          text-lg
          sm:text-xl
          lg:text-2xl
          font-bold
          text-gray-900
          mb-2
        ">
          Card Title
        </h3>
        <p className="
          text-sm
          sm:text-base
          text-gray-600
        ">
          Responsive content that adapts to different screen sizes
        </p>
      </div>
    </div>
  );
}
```

**Code Generation Hint**: This responsive pattern will inform all responsive design implementation.

**Validation**: All responsive components must use mobile-first design principles.

## 5. Form Handling

### Form Components
```tsx
import React, { useState } from 'react';

interface FormFieldProps {
  label: string;
  name: string;
  type?: 'text' | 'email' | 'password' | 'number';
  value: string;
  onChange: (name: string, value: string) => void;
  error?: string;
  required?: boolean;
  placeholder?: string;
}

export function FormField({
  label,
  name,
  type = 'text',
  value,
  onChange,
  error,
  required = false,
  placeholder
}: FormFieldProps) {
  return (
    <div className="mb-4">
      <label htmlFor={name} className="
        block
        text-sm
        font-medium
        text-gray-700
        mb-1
      ">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <input
        id={name}
        type={type}
        value={value}
        onChange={(e) => onChange(name, e.target.value)}
        placeholder={placeholder}
        className={`
          // Layout
          block w-full

          // Box model
          px-3 py-2

          // Visual
          border rounded-md
          ${error ? 'border-red-500' : 'border-gray-300'}
          focus:outline-none focus:ring-2
          ${error ? 'focus:ring-red-500' : 'focus:ring-blue-500'}
          focus:border-transparent

          // Typography
          text-sm

          // Transitions
          transition-colors duration-200
        `}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}

// Form validation
export function useFormValidation<T extends Record<string, any>>(
  initialValues: T,
  validationRules: Record<keyof T, (value: any) => string | undefined>
) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});

  const validate = (name: keyof T, value: any): string | undefined => {
    const rule = validationRules[name];
    return rule ? rule(value) : undefined;
  };

  const handleChange = (name: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    const error = validate(name, value);
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  const validateAll = (): boolean => {
    const newErrors: Partial<Record<keyof T, string>> = {};
    let isValid = true;

    Object.keys(validationRules).forEach(key => {
      const name = key as keyof T;
      const error = validate(name, values[name]);
      if (error) {
        newErrors[name] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  return {
    values,
    errors,
    handleChange,
    validateAll,
    setValues
  };
}

// Usage example
export function LoginForm() {
  const validationRules = {
    email: (value: string) => {
      if (!value) return 'Email is required';
      if (!/\S+@\S+\.\S+/.test(value)) return 'Email is invalid';
      return undefined;
    },
    password: (value: string) => {
      if (!value) return 'Password is required';
      if (value.length < 6) return 'Password must be at least 6 characters';
      return undefined;
    }
  };

  const { values, errors, handleChange, validateAll } = useFormValidation(
    { email: '', password: '' },
    validationRules
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateAll()) {
      console.log('Form submitted:', values);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>

      <FormField
        label="Email"
        name="email"
        type="email"
        value={values.email}
        onChange={handleChange}
        error={errors.email}
        required
        placeholder="Enter your email"
      />

      <FormField
        label="Password"
        name="password"
        type="password"
        value={values.password}
        onChange={handleChange}
        error={errors.password}
        required
        placeholder="Enter your password"
      />

      <Button
        type="submit"
        variant="primary"
        size="lg"
        className="w-full"
      >
        Login
      </Button>
    </form>
  );
}
```

**Code Generation Hint**: This form pattern will inform all form implementation with proper validation and error handling.

**Validation**: All forms must include proper validation, error handling, and accessibility features.

## 6. Error Handling and Loading States

### Error Boundary
```tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="
          // Layout
          flex flex-col items-center justify-center

          // Box model
          p-8

          // Visual
          bg-red-50 border border-red-200 rounded-lg

          // Typography
          text-center
        ">
          <h2 className="text-xl font-semibold text-red-800 mb-2">
            Something went wrong
          </h2>
          <p className="text-red-600 mb-4">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**Code Generation Hint**: This error boundary pattern will inform all error handling implementation.

**Validation**: All applications must include proper error boundaries and error handling.

### Loading States
```tsx
// Loading component
export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  return (
    <div className="flex justify-center items-center">
      <svg
        className={`animate-spin ${sizeClasses[size]} text-blue-500`}
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
}

// Loading wrapper component
export function LoadingWrapper({
  loading,
  error,
  children,
  fallback
}: {
  loading: boolean;
  error?: string | null;
  children: ReactNode;
  fallback?: ReactNode;
}) {
  if (loading) {
    return fallback || (
      <div className="flex justify-center items-center p-8">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="
        // Layout
        flex flex-col items-center justify-center

        // Box model
        p-8

        // Visual
        bg-red-50 border border-red-200 rounded-lg

        // Typography
        text-center
      ">
        <h3 className="text-lg font-semibold text-red-800 mb-2">
          Error Loading Content
        </h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return <>{children}</>;
}
```

**Code Generation Hint**: This loading pattern will inform all loading state implementation.

**Validation**: All components must include proper loading states and error handling.

## Implementation Guidelines

### For AI Assistants
1. **Follow these patterns** for all React component implementation
2. **Use TypeScript** with proper type definitions
3. **Implement proper error handling** with error boundaries
4. **Include loading states** for all async operations
5. **Use Tailwind CSS** with proper organization
6. **Follow responsive design** principles
7. **Implement proper form validation** and error handling
8. **Use appropriate state management** patterns

### For Human Developers
1. **Reference these patterns** when building React components
2. **Use TypeScript** for type safety and better development experience
3. **Implement error boundaries** for robust error handling
4. **Include loading states** for better user experience
5. **Follow Tailwind CSS** organization patterns
6. **Test components** thoroughly with different scenarios
7. **Optimize performance** with proper React patterns

## Quality Assurance

### Component Standards
- All components must use TypeScript with proper interfaces
- Components must follow single responsibility principle
- Error handling must be comprehensive with error boundaries
- Loading states must be implemented for async operations
- Accessibility features must be included

### Performance Standards
- Components must use proper React optimization techniques
- Bundle size must be optimized with code splitting
- Images and assets must be optimized
- Lazy loading must be implemented where appropriate
- Performance must be monitored and measured

### Accessibility Standards
- Semantic HTML elements must be used
- ARIA attributes must be properly implemented
- Keyboard navigation must be supported
- Color contrast must meet WCAG guidelines
- Screen reader compatibility must be tested

### Testing Standards
- Unit tests must be written for all components
- Integration tests must cover component interactions
- Accessibility tests must be included
- Performance tests must be implemented
- Visual regression tests must be maintained

---

**AI Quality Checklist**: Before implementing React components, ensure:
- [x] TypeScript interfaces are properly defined
- [x] Components follow single responsibility principle
- [x] Error boundaries are implemented
- [x] Loading states are included for async operations
- [x] Tailwind CSS classes are properly organized
- [x] Responsive design principles are followed
- [x] Form validation and error handling are implemented
- [x] Accessibility features are included
- [x] Performance optimization techniques are applied
