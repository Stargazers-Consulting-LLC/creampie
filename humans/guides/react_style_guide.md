# React Style Guide

> This guide provides best practices and standards for writing React code in the CreamPie project. It covers component structure, naming, state management, styling, testing, accessibility, and more.

## Table of Contents
1. [General Principles](#general-principles)
2. [Project Structure](#project-structure)
3. [File and Folder Naming Conventions](#file-and-folder-naming-conventions)
4. [Component Patterns](#component-patterns)
5. [Styling](#styling)
6. [State Management](#state-management)
7. [Form Validation Patterns](#form-validation-patterns)
8. [UX Design Principles](#ux-design-principles)
9. [Testing](#testing)
10. [Performance](#performance)
11. [Accessibility](#accessibility)
12. [Code Review Checklist](#code-review-checklist)
13. [Example Patterns](#example-patterns)

---

## General Principles
- Use [function components](https://react.dev/reference/react/FunctionComponent) and [React Hooks](https://react.dev/reference/react/hooks) for all new code.
- **Check the existing component library in `cream_ui/src/components` before creating new components.**
- Prefer composition over inheritance.
- Keep components small, focused, and reusable.
- Write declarative code: describe what you want, not how to do it.
- Co-locate related files (component, styles, tests) together.
- Use TypeScript for type safety and better developer experience.
- Write self-documenting code; use comments only for non-obvious logic.

## Project Structure
- Organize by feature/domain, not by type (e.g., `components/`, `pages/`, `hooks/`, `lib/`).
- Place each component in its own folder if it has related files (styles, tests, subcomponents).
- Example structure:

```
cream_ui/
├── src/
│   ├── components/
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.test.tsx
│   │   │   └── button.module.css
│   │   └── ...
│   ├── hooks/
│   │   └── useMobile.ts
│   ├── pages/
│   │   └── LandingPage.tsx
│   ├── App.tsx
│   └── main.tsx
└── ...
```

## File and Folder Naming Conventions
- Use **PascalCase** for component and page files/folders (e.g., `Button.tsx`, `SignUpPage.tsx`).
- Use **camelCase** for hooks and utility files (e.g., `useMobile.ts`, `fetchData.ts`).
- Use **kebab-case** or **camelCase** for CSS/SCSS files (e.g., `button.module.css`).
- Use **index.tsx** for default exports in a folder, but prefer explicit filenames for clarity.
- Avoid spaces, special characters, or uppercase in non-component filenames.

## Component Patterns
- Use function components with ES6+ syntax.
- Use [TypeScript](https://www.typescriptlang.org/) for all components and props.
- Define prop types with TypeScript interfaces or types.
- Use [React.FC](https://react-typescript-cheatsheet.netlify.app/docs/basic/getting-started/function_components/) only if you need children; otherwise, prefer explicit typing.
- Prefer [arrow functions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions) for component definitions.
- Keep components pure and side-effect free; use hooks for side effects.
- Use [custom hooks](https://react.dev/reference/react/hooks#using-the-state-hook) to encapsulate reusable logic.
- Destructure props at the top of the component.
- Use default values for optional props.

### React Import Pattern

**Problem**: ESLint flags `import * as React from 'react';` as unused even though it's required for JSX compilation.

**Solution**: Use the preferred import pattern based on your needs:

```tsx
// ✅ Preferred - Explicit namespace import (use when you need React for JSX)
import * as React from 'react';

// ✅ Also acceptable - Specific imports (use when you only need certain hooks)
import { useState, useEffect } from 'react';

// ❌ Less preferred - Default import (can be confusing)
import React from 'react';
```

**When to use each pattern:**
- **`import * as React from 'react';`** - Use in components that render JSX (most components)
- **`import { useState, useEffect } from 'react';`** - Use in hooks or utilities that only need specific React exports
- **`import React from 'react';`** - Avoid this pattern for consistency

**Why this pattern?**
- JSX requires React to be in scope (even if not explicitly used)
- ESLint may flag it as unused import
- The namespace import is more explicit and consistent
- This pattern is consistent across the codebase

- Example:

```tsx
import React from "react";

type ButtonProps = {
  label: string;
  onClick?: () => void;
  disabled?: boolean;
};

export const Button: React.FC<ButtonProps> = ({ label, onClick, disabled = false }) => (
  <button onClick={onClick} disabled={disabled}>
    {label}
  </button>
);
```

## Styling
- Use [CSS Modules](https://github.com/css-modules/css-modules), [Tailwind CSS](https://tailwindcss.com/), or [styled-components](https://styled-components.com/) for component styles.
- Co-locate styles with their components.
- Use utility-first CSS (e.g., Tailwind) for rapid prototyping and consistent design.
- Avoid global styles except for resets and base typography.
- Use BEM or similar conventions if using plain CSS.
- Prefer className over inline styles for maintainability.
- Example (Tailwind):

```tsx
<button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
  Click me
</button>
```

## State Management
- Use React's built-in state and context for local and shared state.
- Use [useState](https://react.dev/reference/react/useState) for local state.
- Use [useContext](https://react.dev/reference/react/useContext) for global/shared state.
- Use [useReducer](https://react.dev/reference/react/useReducer) for complex state logic.
- For larger apps, consider [Redux Toolkit](https://redux-toolkit.js.org/) or [Zustand](https://zustand-demo.pmnd.rs/) for global state.
- Keep state as close to where it is used as possible.
- Avoid prop drilling by using context or hooks.

## Form Validation Patterns

### Choose Validation Mode Based on UX Goals

**Problem**: Using `mode: 'onChange'` for form validation shows errors immediately as users type, creating a poor user experience where users are "yelled at" while still typing valid data.

**Solution**: Use `mode: 'onBlur'` for better UX:
- ✅ No errors while typing
- ✅ Errors show when user leaves field with invalid data
- ✅ Errors show when user tries to submit with invalid data
- ✅ Empty field only shows error when user attempts to submit

```typescript
const form = useForm<FormData>({
  resolver: zodResolver(schema),
  mode: 'onBlur', // Better UX than 'onChange'
  defaultValues: { symbol: '' }
});
```

### Avoid Over-Validation During Input

**Problem**: Using `shouldValidate: true` in `setValue` calls causes validation to trigger on every keystroke, interfering with the form's validation mode.

**Solution**: Let React Hook Form handle validation timing:
```typescript
// ✅ Good: Let form handle validation timing
const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const value = e.target.value.toUpperCase();
  form.setValue('symbol', value); // No shouldValidate parameter

  // Clear API error messages when user starts typing
  if (errorMessage) {
    setErrorMessage(null);
  }
};
```

### Keep Validation Schemas Simple

**Problem**: Complex validation schemas with multiple `refine` methods are hard to debug and maintain.

**Solution**: Use simple, sequential validation rules:
```typescript
// ✅ Good: Simple, clear validation order
const schema = z.object({
  symbol: z
    .string()
    .min(1, 'Stock symbol is required')
    .min(2, 'Stock symbol must be at least 2 characters')
    .max(10, 'Stock symbol must be 10 characters or less')
    .regex(/^[A-Za-z][A-Za-z0-9]*$/, 'Stock symbol must be 2-10 characters, start with a letter')
    .transform((value) => value.trim().toUpperCase())
});
```

### Separate Concerns Clearly

**Problem**: Mixing validation logic, API calls, and UI state makes code hard to test and maintain.

**Solution**: Separate concerns:
```typescript
// ✅ Good: Clear separation of concerns
const form = useForm<FormData>({
  resolver: zodResolver(schema), // Validation
  mode: 'onBlur',
  defaultValues: { symbol: '' }
});

const [errorMessage, setErrorMessage] = useState<string | null>(null); // API errors
const [isSubmitting, setIsSubmitting] = useState(false); // UI state

const onSubmit = async (data: FormData) => {
  setIsSubmitting(true);
  setErrorMessage(null);

  try {
    await trackStock(data.symbol);
    // Handle success
  } catch (error) {
    setErrorMessage(getErrorMessage(error));
  } finally {
    setIsSubmitting(false);
  }
};
```

## UX Design Principles

### Don't Interrupt User Flow

**Problem**: Immediate validation errors interrupt users while they're still typing valid data.

**Solution**: Design validation to support user flow:
- **Don't show errors while typing** - Let users complete their input
- **Show errors on blur** - When user leaves field with invalid data
- **Show errors on submit** - When user attempts to submit invalid data
- **Clear errors when user starts fixing** - Provide immediate positive feedback

### Make Submit Button Always Clickable

**Problem**: Disabling submit button when form is invalid prevents users from triggering validation.

**Solution**: Keep submit button enabled and let validation handle errors:
```typescript
// ✅ Good: Button always clickable
<Button type="submit" disabled={isSubmitting} className="w-full">
  Request Tracking
</Button>

// ❌ Bad: Button disabled prevents validation
<Button
  type="submit"
  disabled={!form.formState.isValid || isSubmitting}
  className="w-full"
>
  Request Tracking
</Button>
```

### Provide Clear Feedback

**Problem**: Users don't know what's happening during form submission.

**Solution**: Provide comprehensive feedback:
- **Loading states** - Show when form is submitting
- **Success messages** - Confirm when action completes
- **Error messages** - Explain what went wrong and how to fix it
- **Progress indicators** - Show multi-step processes

## Testing
- Use [Jest](https://jestjs.io/) and [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) for all component and hook tests.
- Co-locate tests with the components they test.
- Use descriptive test names and group related tests with `describe`.
- Prefer testing user interactions and behavior over implementation details.
- Mock external dependencies and APIs.
- Example:

```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "./Button";

test("calls onClick when clicked", () => {
  const handleClick = jest.fn();
  render(<Button label="Click me" onClick={handleClick} />);
  fireEvent.click(screen.getByText("Click me"));
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

## Performance
- Use [React.memo](https://react.dev/reference/react/memo) to memoize pure components.
- Use [useCallback](https://react.dev/reference/react/useCallback) and [useMemo](https://react.dev/reference/react/useMemo) to avoid unnecessary re-renders.
- Avoid anonymous functions and objects in JSX when possible.
- Split large components into smaller, focused ones.
- Use code-splitting and lazy loading for large pages or components.
- Avoid unnecessary state and props.

## Accessibility
- Use semantic HTML elements (e.g., `<button>`, `<nav>`, `<main>`, `<form>`).
- Always provide `aria-*` attributes and labels for interactive elements.
- Ensure all interactive elements are keyboard accessible.
- Use [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) to catch accessibility issues.
- Test with screen readers and keyboard navigation.
- Provide alt text for all images.

## Code Review Checklist
- [ ] Component and file naming follows conventions
- [ ] TypeScript types are used for all props and state
- [ ] Components are pure and side-effect free
- [ ] State is managed appropriately (local, context, or global)
- [ ] Form validation follows UX best practices
- [ ] Submit buttons are always clickable (except during submission)
- [ ] Loading and error states are properly handled
- [ ] Styles are co-located and follow project conventions
- [ ] Tests are present and cover key behaviors
- [ ] Accessibility best practices are followed
- [ ] React import pattern is followed (with ESLint comment when needed)
- [ ] No unused code, variables, or imports
- [ ] No direct DOM manipulation (use refs or effects if needed)
- [ ] No hardcoded values (use constants or config)
- [ ] Code is self-documenting and maintainable

## Example Patterns

### Simple Function Component
```tsx
// @ts-expect-error - React is needed for JSX
import * as React from 'react';

type GreetingProps = { name: string };

export function Greeting({ name }: GreetingProps) {
  return <h1>Hello, {name}!</h1>;
}
```

### Custom Hook
```tsx
import { useState, useEffect } from 'react';

export function useWindowWidth() {
  const [width, setWidth] = useState(window.innerWidth);
  useEffect(() => {
    const handleResize = () => setWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);
  return width;
}
```

### Component with Tailwind CSS
```tsx
// @ts-expect-error - React is needed for JSX
import * as React from 'react';

export function Alert({ message }: { message: string }) {
  return (
    <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4">
      {message}
    </div>
  );
}
```

### Form Component with Proper Validation
```tsx
// @ts-expect-error - React is needed for JSX
import * as React from 'react';
import { useState } from 'react';
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  symbol: z
    .string()
    .min(1, 'Stock symbol is required')
    .min(2, 'Stock symbol must be at least 2 characters')
    .regex(/^[A-Za-z][A-Za-z0-9]*$/, 'Stock symbol must be 2-10 characters, start with a letter')
    .transform((value) => value.trim().toUpperCase())
});

type FormData = z.infer<typeof schema>;

export function StockRequestForm() {
  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    mode: 'onBlur', // Better UX
    defaultValues: { symbol: '' }
  });

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await trackStock(data.symbol);
      // Handle success
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <input
        {...form.register('symbol')}
        placeholder="Enter stock symbol"
        className="w-full p-2 border rounded"
      />
      {form.formState.errors.symbol && (
        <p className="text-red-500 text-sm">
          {form.formState.errors.symbol.message}
        </p>
      )}
      {errorMessage && (
        <p className="text-red-500 text-sm">{errorMessage}</p>
      )}
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full p-2 bg-blue-600 text-white rounded disabled:opacity-50"
      >
        {isSubmitting ? 'Submitting...' : 'Request Tracking'}
      </button>
    </form>
  );
}
```

---

This style guide provides a foundation for writing robust, maintainable, and accessible React code. Follow these patterns to ensure consistency and quality across the codebase.
