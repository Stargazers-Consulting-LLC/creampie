# React Style Guide

## Structure

### File Organization

- Place components in the `src/components` directory
- Place pages in the `src/pages` directory
- Use PascalCase for component file names (e.g., `Navbar.tsx`, `LandingPage.tsx`)

### Component Naming

- Use PascalCase for component names
- Use descriptive names that indicate the component's purpose
- Prefix page components with the page name (e.g., `LandingPage`)

### Component Structure

```tsx
import { Link } from "react-router-dom";
import { OtherComponent } from "../components/OtherComponent";

export function ComponentName() {
  return <div className="...">{/* Component content */}</div>;
}
```

### Import Considerations

- @import must precede all other statements (besides @charset or empty @layer)
- The first import should always be `import * as React from "react";`, if needed.
- - `// @ts-expect-error - React is needed for JSX` should always be above it.

### Security

- Never hardcode sensitive information
- Use environment variables for secrets
- Implement proper CORS configuration
- Validate all input data
- Use secure database connection strings

## Styling with Tailwind CSS

### Class Organization

- Group related classes together
- Use consistent spacing between class groups
- Follow this order:
  1. Layout (display, position, etc.)
  2. Box model (margin, padding, etc.)
  3. Visual (colors, backgrounds, etc.)
  4. Typography
  5. Transitions/Animations

Example:

```tsx
<div className="
  // Layout
  flex items-center justify-between

  // Box model
  p-4 m-2

  // Visual
  bg-white shadow-sm

  // Typography
  text-gray-900

  // Transitions
  transition-colors duration-200
">
```

### Responsive Design

- Use Tailwind's responsive prefixes consistently
- Start with mobile-first design
- Use the following breakpoint order:
  - Default (mobile)
  - `sm:` (640px)
  - `md:` (768px)
  - `lg:` (1024px)
  - `xl:` (1280px)

Example:

```tsx
<div className="
  text-sm
  sm:text-base
  md:text-lg
  lg:text-xl
">
```

### Component Composition

- Break down complex components into smaller, reusable pieces
- Use semantic HTML elements
- Maintain consistent spacing and layout patterns

## Navigation

### Routing

- Use `react-router-dom` for navigation
- Keep routes organized and maintainable
- Use descriptive route names

Example:

```tsx
<Link to="/about" className="text-gray-500 hover:text-gray-700">
  About
</Link>
```

## State Management

### Component State

- Use React hooks for local state
- Keep state as close as possible to where it's used
- Use descriptive state variable names

Example:

```tsx
const [isOpen, setIsOpen] = useState(false);
```

## Best Practices

### Code Organization

- Keep components focused and single-responsibility
- Extract reusable logic into custom hooks
- Use TypeScript for type safety

### Performance

- Use React.memo for expensive components
- Implement proper loading states
- Optimize images and assets

### Accessibility

- Use semantic HTML elements
- Include proper ARIA attributes
- Ensure keyboard navigation works
- Maintain sufficient color contrast

### Error Handling

- Implement proper error boundaries
- Show user-friendly error messages
- Log errors appropriately

## Naming Conventions

### Variables and Functions

- Use camelCase for variables and functions
- Use descriptive names that indicate purpose
- Prefix boolean variables with 'is', 'has', or 'should'

Example:

```tsx
const isMenuOpen = false;
const handleClick = () => {};
const shouldShowModal = true;
```

### CSS Classes

- Use Tailwind's utility classes
- Group related classes with comments
- Keep class names consistent across components

## Comments and Documentation

### Component Documentation

- Document complex components
- Explain non-obvious logic
- Include prop types and usage examples

Example:

```tsx
/**
 * Navbar component that provides main navigation
 * @param {boolean} isAuthenticated - Whether the user is logged in
 * @returns {JSX.Element} Navigation bar component
 */
```

### Code Comments

- Use comments to explain why, not what
- Keep comments up to date
- - If a comment is to be updated, explain the history of the code for additional context.
- Remove commented-out code
- linting directives, such as `// @ts-expect-error - React is needed for JSX` are exempt from these rules.

## Testing

### Component Testing

- Write tests for complex components
- Test user interactions
- Ensure accessibility compliance

## Resources

### Useful Links

- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [React Router Documentation](https://reactrouter.com)
