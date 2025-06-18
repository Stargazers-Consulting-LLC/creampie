# AI Development Guides

This directory contains comprehensive guides for AI assistants to provide effective code development assistance, following a hierarchical structure from core principles to language-specific patterns.

## Guide Structure

### 📁 Core Principles
- **[Core Principles.md](Core%20Principles.md)** - Fundamental decision-making frameworks and philosophies
- **[Code Review Patterns.md](Code%20Review%20Patterns.md)** - How to structure suggestions and handle conflicts

### 📁 Project Context
- **[Architecture Overview.md](../project_context/Architecture%20Overview.md)** - High-level system design and component relationships
- **[Development Workflow.md](../project_context/Development%20Workflow.md)** - How features flow from idea to deployment
- **[Common Patterns.md](../project_context/Common%20Patterns.md)** - Project-specific patterns and conventions

### 📁 Language-Specific
- **[Python Style Guide.md](Language-Specific/Python%20Style%20Guide.md)** - Pure Python style rules
- **[Python Testing Guide.md](Language-Specific/Python%20Testing%20Guide.md)** - Pure testing patterns
- **[FastAPI Development Guide.md](Language-Specific/FastAPI%20Development%20Guide.md)** - General FastAPI patterns

### 📁 Domain-Specific
- **[Database Management Guide.md](Domain-Specific/Database%20Management%20Guide.md)** - Database patterns and migrations
- **[Frontend Style Guide.md](Domain-Specific/Frontend%20Style%20Guide.md)** - React and frontend patterns
- **[Shell Style Guide.md](Domain-Specific/Shell%20Style%20Guide.md)** - Shell script patterns
- **[Web Scraping Patterns.md](Domain-Specific/Web%20Scraping%20Patterns.md)** - Project-specific web scraping patterns (HTML parsing, background tasks, file processing)

### 📁 Technical Details
- **[Technical Summaries](../technical_summaries/)** - Detailed module summaries and implementation details
- **[Decisions](../decisions/)** - Architecture decisions and technology choices

## How to Use These Guides

### For AI Assistants

1. **Start with Core Principles** - Understand the fundamental frameworks for decision-making
2. **Understand Project Context** - Learn about the specific project architecture and patterns
3. **Apply Language-Specific Rules** - Use the appropriate language guide for the code you're working with
4. **Consider Domain Context** - Apply domain-specific patterns when relevant
5. **Use Code Review Patterns** - Structure your suggestions and handle conflicts appropriately

### Decision-Making Flow

```
User Request → Core Principles → Project Context → Language-Specific → Domain-Specific → Code Review Patterns
```

### Example Workflow

1. **User asks for code review**
   - Check Core Principles for decision-making framework
   - Review Project Context for established patterns
   - Apply Python Style Guide for style violations
   - Use Code Review Patterns to structure suggestions

2. **User asks for new feature**
   - Check Core Principles for context awareness
   - Review Architecture Overview for system design
   - Apply FastAPI Guide for general API patterns
   - Consider Web Scraping Patterns for data processing needs
   - Consider Database Guide for data modeling

3. **User encounters conflict**
   - Use Code Review Patterns for conflict resolution
   - Apply Core Principles for priority assessment
   - Check Common Patterns for established conventions
   - Explain reasoning using appropriate guides

## Guide Relationships

### Hierarchy
- **Core Principles** → **Project Context** → **Language-Specific** → **Domain-Specific**
- Each level builds on the previous level
- Conflicts are resolved using priority systems from Core Principles

### Cross-References
- Guides reference each other when appropriate
- Core Principles provide the foundation for all other guides
- Project Context provides project-specific understanding
- Code Review Patterns provide frameworks for applying all guides

### Maintenance
- Update Core Principles when fundamental patterns change
- Update Project Context when architecture evolves
- Update Language-Specific guides when language patterns evolve
- Update Domain-Specific guides when domain requirements change
- Keep guides consistent and avoid duplication

## Best Practices for AI Assistants

### When Using These Guides
1. **Always start with context** - Understand what the user is trying to accomplish
2. **Apply principles hierarchically** - Core → Project Context → Language → Domain
3. **Explain your reasoning** - Help users understand why you're suggesting changes
4. **Be consistent** - Apply the same patterns across similar situations
5. **Learn and adapt** - Update your approach based on user feedback

### When Guides Conflict
1. **Identify the conflict** - Clearly state what the guides say differently
2. **Assess context** - Consider the specific situation and user's needs
3. **Apply priority system** - Security/Data Integrity → Project Consistency → Performance → Style
4. **Explain trade-offs** - Help user understand the implications of your recommendation

### When Suggesting Changes
1. **Structure suggestions** - Use the standard format from Code Review Patterns
2. **Prioritize issues** - Critical → High → Medium → Low
3. **Provide context** - Explain why changes are beneficial
4. **Be educational** - Help users understand patterns for future use

## Guide Evolution

These guides should evolve based on:
- **User feedback** - What works well and what doesn't
- **Pattern recognition** - Common issues and successful solutions
- **Technology changes** - New tools, libraries, and best practices
- **Project growth** - New requirements and architectural decisions

Keep the guides updated and relevant to ensure they remain valuable for both AI assistants and human developers.
