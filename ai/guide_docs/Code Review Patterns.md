# Code Review Patterns for AI Assistants

This guide provides specific patterns and frameworks for AI assistants to conduct effective code reviews, structure suggestions, and handle conflicts between different style guides.

## 1. Suggestion Structure

### Standard Suggestion Format
```
**Issue**: [Clear description of the problem]
**Impact**: [Why this matters - performance, security, maintainability, etc.]
**Solution**: [Specific, actionable fix]
**Reasoning**: [Why this approach is preferred]
```

### Example Suggestion
```
**Issue**: Magic number `5.0` used in performance assertion
**Impact**: Reduces code readability and makes maintenance harder
**Solution**: Define `MAX_PROCESSING_TIME_SECONDS = 5.0` at module level
**Reasoning**: Follows Python Style Guide principle of avoiding magic numbers
```

### Multi-Issue Reviews
When multiple issues exist, structure them by priority:

```
## Critical Issues
[Critical issues first]

## High Priority Issues
[Style guide violations, performance issues]

## Medium Priority Issues
[Code organization, documentation]

## Suggestions for Future
[Optional improvements]
```

## 2. Conflict Resolution

### When Guides Conflict
1. **Identify the conflict**: Clearly state what the guides say differently
2. **Assess context**: Consider the specific situation and user's needs
3. **Recommend approach**: Suggest which guide to follow and why
4. **Explain trade-offs**: Help user understand the implications

### Priority-Based Resolution
1. **Security/Data Integrity**: Always follow strictest guidance
2. **Project Consistency**: Follow established project patterns
3. **Performance**: Use performance-focused guidance when relevant
4. **Style**: Follow style guide unless there's a compelling reason not to

### Common Conflict Scenarios
```
**Scenario**: User wants to use pathlib in new code
**Conflict**: Python Style Guide specifies os.path preference
**Resolution**: Follow Python Style Guide - use os.path for consistency
**Reasoning**: Project consistency takes priority over personal preference

**Scenario**: User wants to use datetime.utcnow() in new code
**Conflict**: Python Style Guide specifies datetime.now(datetime.UTC)
**Resolution**: Follow Python Style Guide - use modern datetime approach
**Reasoning**: Modern Python best practices take priority

**Scenario**: User wants to use magic numbers in tests
**Conflict**: Python Style Guide prohibits magic numbers, Testing Guide shows examples
**Resolution**: Follow Python Style Guide - define constants for all magic numbers
**Reasoning**: Consistency across all code (including tests) is important

**Scenario**: User wants to use complex CSS selectors for HTML parsing
**Conflict**: Web Scraping Patterns prefer simple, semantic selectors
**Resolution**: Follow Web Scraping Patterns - use simple, resilient selectors
**Reasoning**: Maintainability and resilience take priority over convenience

**Scenario**: User wants to load configuration in each function
**Conflict**: Python Style Guide specifies loading once at module level
**Resolution**: Follow Python Style Guide - load configuration once at module level
**Reasoning**: Performance and consistency take priority over convenience
```

### Conflict Resolution Process
```
1. **Identify the specific conflict** between guides
2. **Apply the priority system**: Security → Project Consistency → Performance → Style
3. **Explain the reasoning** behind the recommendation
4. **Provide specific guidance** on how to implement the preferred approach
5. **Acknowledge trade-offs** and explain why the chosen approach is better
```

## 3. Context-Aware Suggestions

### File Type Context
- **Configuration files**: Focus on clarity and maintainability
- **Test files**: Focus on reliability and coverage
- **API files**: Focus on security and performance
- **Utility files**: Focus on reusability and documentation

### User Context
- **Junior developers**: Provide more explanation and educational context
- **Senior developers**: Focus on technical details and trade-offs
- **New to project**: Emphasize project-specific patterns
- **Experienced with project**: Focus on improvements and optimizations

### Task Context
- **Bug fixes**: Focus on correctness and preventing regressions
- **New features**: Focus on maintainability and future-proofing
- **Refactoring**: Focus on consistency and established patterns
- **Performance work**: Focus on measurable improvements

## 4. Communication Patterns

### Positive Reinforcement
- **Acknowledge good practices**: "Good use of type hints here"
- **Recognize progress**: "This is much cleaner than the previous version"
- **Highlight improvements**: "The error handling is now more robust"

### Constructive Criticism
- **Focus on code, not person**: "This approach could be improved" vs "You're doing this wrong"
- **Provide alternatives**: Always suggest specific improvements
- **Explain reasoning**: Help user understand why changes are beneficial

### Educational Moments
- **Explain patterns**: "This follows the [pattern name] which is preferred because..."
- **Share knowledge**: "In Python, it's better to use X because..."
- **Provide context**: "This is important because it affects..."

## 5. Handling Different Types of Issues

### Style Violations
```
**Issue**: Inconsistent import organization
**Impact**: Reduces code readability and maintainability
**Solution**: Reorganize imports following Python Style Guide order
**Reasoning**: Consistent import organization makes code easier to scan and maintain
```

### Performance Issues
```
**Issue**: Redundant configuration loading in each function
**Impact**: Unnecessary overhead and potential performance degradation
**Solution**: Load configuration once at module level
**Reasoning**: Reduces function call overhead and improves performance
```

### Security Concerns
```
**Issue**: Potential SQL injection vulnerability
**Impact**: Security risk that could lead to data compromise
**Solution**: Use parameterized queries with SQLAlchemy
**Reasoning**: Parameterized queries prevent SQL injection attacks
```

### Maintainability Issues
```
**Issue**: Duplicated logic across multiple functions
**Impact**: Makes maintenance harder and increases bug risk
**Solution**: Extract common logic into a shared function
**Reasoning**: DRY principle reduces code duplication and maintenance burden
```

## 6. Review Scope Management

### When to Expand Scope
- **Related issues**: If fixing one issue reveals related problems
- **Pattern violations**: If the issue suggests a broader pattern problem
- **User requests**: If user asks for broader review
- **Critical issues**: If the issue affects multiple areas

### When to Stay Focused
- **User's explicit scope**: Respect user's stated boundaries
- **Unrelated issues**: Don't suggest changes outside current context
- **Minor improvements**: Don't overwhelm with too many suggestions
- **Future considerations**: Don't suggest premature optimizations

### Scope Communication
- **Current focus**: "Focusing on the error handling in this function"
- **Related issues**: "This also affects the similar function in X"
- **Broader implications**: "This pattern appears in several other files"
- **Future considerations**: "Consider applying this pattern elsewhere"

## 7. Follow-up Patterns

### Checking Implementation
- **Verify changes**: Confirm that suggestions were implemented correctly
- **Test integration**: Ensure changes work with the rest of the codebase
- **Validate assumptions**: Check that the reasoning still applies
- **Provide feedback**: Acknowledge good implementations

### Iterative Improvement
- **Build on progress**: Use previous improvements as foundation
- **Incremental suggestions**: Don't suggest everything at once
- **Learning opportunities**: Help user understand patterns for future use
- **Confidence building**: Acknowledge improvements and progress

### Documentation Updates
- **Update guides**: If patterns evolve, update relevant guides
- **Share learnings**: Document new patterns that work well
- **Improve examples**: Update examples based on real usage
- **Refine guidance**: Improve guidance based on user feedback
