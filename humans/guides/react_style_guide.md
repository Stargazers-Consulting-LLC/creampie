# React Style Guide

> This guide provides best practices and standards for writing React code in the CreamPie project. It covers component structure, naming, state management, styling, testing, accessibility, and more.

## Table of Contents
1. [General Principles](#general-principles)
2. [Project Structure](#project-structure)
3. [File and Folder Naming Conventions](#file-and-folder-naming-conventions)
4. [Component Patterns](#component-patterns)
5. [Styling](#styling)
6. [State Management](#state-management)
7. [Testing](#testing)
8. [Performance](#performance)
9. [Accessibility](#accessibility)
10. [Code Review Checklist](#code-review-checklist)
11. [Example Patterns](#example-patterns)

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
- [ ] Styles are co-located and follow project conventions
- [ ] Tests are present and cover key behaviors
- [ ] Accessibility best practices are followed
- [ ] No unused code, variables, or imports
- [ ] No direct DOM manipulation (use refs or effects if needed)
- [ ] No hardcoded values (use constants or config)
- [ ] Code is self-documenting and maintainable

## Example Patterns

### Simple Function Component
```tsx
import React from "react";

type GreetingProps = { name: string };

export function Greeting({ name }: GreetingProps) {
  return <h1>Hello, {name}!</h1>;
}
```

### Custom Hook
```tsx
import { useState, useEffect } from "react";

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
export function Alert({ message }: { message: string }) {
  return (
    <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4">
      {message}
    </div>
  );
}
```

---

This style guide provides a foundation for writing robust, maintainable, and accessible React code. Follow these patterns to ensure consistency and quality across the codebase.
