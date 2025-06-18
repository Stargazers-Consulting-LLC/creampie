# Project Context

This directory contains reference documentation about the current system architecture, patterns, and development processes.

## Purpose

Project context provides:
- **System architecture** understanding and component relationships
- **Development patterns** and conventions used in the project
- **Workflow processes** for feature development and deployment
- **Historical context** for architectural decisions
- **Integration patterns** between different parts of the system

## Organization

### Core Documentation
- **[Architecture Overview.md](Architecture%20Overview.md)** - High-level system design and component relationships
- **[Common Patterns.md](Common%20Patterns.md)** - Project-specific patterns and conventions
- **[Development Workflow.md](Development%20Workflow.md)** - How features flow from idea to deployment

## Usage

### For New Features
1. **Start with Architecture Overview** - Understand how your feature fits into the system
2. **Check Common Patterns** - Follow established conventions
3. **Follow Development Workflow** - Use the established process

### For Code Reviews
1. **Reference Common Patterns** - Ensure code follows project conventions
2. **Check Architecture Overview** - Verify integration points are correct
3. **Consider Development Workflow** - Ensure process is being followed

### For System Understanding
1. **Read Architecture Overview** - Get the big picture
2. **Study Common Patterns** - Understand implementation approaches
3. **Review Development Workflow** - Understand the development process

## Key Concepts

### Architecture Principles
- **Modular Design** - Clear separation of concerns
- **API-First** - Well-defined interfaces between components
- **Background Processing** - Asynchronous data processing
- **Error Handling** - Graceful failure and recovery

### Development Patterns
- **Feature Isolation** - Keep features self-contained
- **Test-Driven** - Comprehensive testing at all levels
- **Documentation-First** - Clear documentation for all components
- **Incremental Development** - Small, focused changes

### Integration Patterns
- **RESTful APIs** - Standard HTTP-based communication
- **Background Tasks** - Asynchronous processing
- **Database Migrations** - Version-controlled schema changes
- **Frontend-Backend Separation** - Clear API boundaries

## Maintenance

- **Update Architecture Overview** when system design changes
- **Add new patterns** to Common Patterns as they emerge
- **Refine Development Workflow** based on team feedback
- **Keep documentation current** with actual implementation

## Related Documentation

- **[Technical Summaries](../technical_summaries/)** - Detailed module analysis
- **[Implementation Plans](../plans/)** - Feature development plans
- **[Style Guides](../guide_docs/)** - Language and domain-specific patterns
