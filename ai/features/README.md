# Feature Documentation Hub

This directory contains comprehensive feature documentation organized by development lifecycle, from initial planning through implementation and maintenance.

## Structure

```
ai/features/
├── README.md           # This file - Workflow and organization guide
├── plans/              # Active feature planning and development
│   ├── [DRAFT]-Feature-Name.md
│   └── [IN-PROGRESS]-Feature-Name.md
└── summaries/          # Completed implementations and technical analysis
    ├── existing_module_summary.md
    └── completed_feature_summary.md
```

## Purpose

The features directory provides:
- **Unified feature lifecycle management** from planning to implementation
- **Comprehensive documentation** for both planning context and technical details
- **AI-optimized structure** for effective code generation and analysis
- **Clear progression** from concept to completed feature

## Workflow

### Feature Lifecycle

```
1. Planning Phase
   ├── Create plan in features/plans/[DRAFT]-Feature-Name.md
   ├── Use AI-optimized template from ../guide_docs/Feature Template.md
   └── Reference existing patterns and technical summaries

2. Development Phase
   ├── Move to features/plans/[IN-PROGRESS]-Feature-Name.md
   ├── Update plan as implementation progresses
   └── Reference technical summaries for integration points

3. Completion Phase
   ├── Move completed plan to features/summaries/
   ├── Create comprehensive technical summary
   ├── Preserve planning context alongside implementation details
   └── Update cross-references in other documentation

4. Maintenance Phase
   ├── Update technical summaries as features evolve
   ├── Reference completed features for new planning
   └── Maintain documentation accuracy
```

### Status Progression

| Status | Location | Purpose |
|--------|----------|---------|
| `[DRAFT]` | `features/plans/` | Initial planning and requirements gathering |
| `[IN-PROGRESS]` | `features/plans/` | Active development and implementation |
| `[COMPLETED]` | `features/summaries/` | Final implementation and technical documentation |
| `[DEPRECATED]` | `features/summaries/` | Historical reference with deprecation notes |

## Organization

### Plans Directory (`features/plans/`)

**Purpose**: Active feature planning and development tracking

**Content**:
- AI-optimized feature plans using `../guide_docs/Feature Template.md`
- Development status tracking with clear progression
- Implementation guidance and code generation hints
- Integration planning with existing systems

**File Naming**:
- `[DRAFT]-Feature-Name.md` - Initial planning phase
- `[IN-PROGRESS]-Feature-Name.md` - Active development
- Plans move to `summaries/` when completed or deprecated

### Summaries Directory (`features/summaries/`)

**Purpose**: Technical documentation of completed implementations and existing modules

**Content**:
- Technical analysis of existing modules and components
- Implementation details of completed features
- Architecture patterns and integration points
- Performance characteristics and optimization notes
- Historical planning context for completed features

**File Naming**:
- `module_name_summary.md` - Technical analysis of existing modules
- `feature_name_summary.md` - Completed feature documentation
- `deprecated_feature_summary.md` - Historical reference with deprecation notes

## Usage for AI Assistants

### When Planning New Features
1. **Check existing summaries** for relevant patterns and integration points
2. **Create plan** in `features/plans/[DRAFT]-Feature-Name.md`
3. **Use AI-optimized template** from `../guide_docs/Feature Template.md`
4. **Reference existing patterns** from `features/summaries/`
5. **Update status** as development progresses

### When Working with Existing Features
1. **Read technical summary** in `features/summaries/` for implementation details
2. **Reference planning context** for design decisions and requirements
3. **Update summary** when making significant changes
4. **Maintain cross-references** with other documentation

### When Completing Features
1. **Move completed plan** from `features/plans/` to `features/summaries/`
2. **Create comprehensive technical summary** with implementation details
3. **Preserve planning context** alongside technical documentation
4. **Update all cross-references** in other documentation

## Quality Standards

### For Plans
- **AI Metadata** with proper dependencies and validation rules
- **Specific file paths** and module references
- **Measurable requirements** with acceptance criteria
- **Code generation hints** for implementation guidance
- **Validation checkpoints** for quality assurance

### For Summaries
- **Comprehensive technical analysis** of implementation
- **Architecture patterns** and design decisions
- **Integration points** with existing systems
- **Performance characteristics** and optimization notes
- **Historical context** from original planning

## Integration with AI Documentation

### Dependencies
Features integrate with other AI documentation:
- **Project Context** (`../project_context/`) - Architecture and patterns
- **Guide Docs** (`../guide_docs/`) - Templates and principles
- **Core Principles** (`../guide_docs/Core%20Principles.md`) - Decision frameworks

### Cross-References
Each feature should reference:
- Existing architecture patterns
- Current module implementations
- Established development workflows
- Relevant technical summaries

## Maintenance

### Regular Updates
- **Update plan status** as features progress through development
- **Move completed plans** to summaries directory
- **Update technical summaries** when implementations evolve
- **Maintain cross-references** across all documentation

### Version Control
- **Template Version** - Track template version used in each plan
- **AI Processing Level** - Indicate complexity for AI tools
- **Dependencies** - Keep dependency references current
- **Validation Rules** - Update validation requirements as needed

## Best Practices

### For AI Tools
1. **Use unified structure** - Leverage both planning and implementation docs
2. **Follow lifecycle workflow** - Progress features through appropriate phases
3. **Reference existing patterns** - Use summaries for integration guidance
4. **Maintain context** - Preserve planning context in completed features
5. **Update cross-references** - Keep documentation relationships current

### For Human Developers
1. **Follow lifecycle workflow** - Use appropriate directories for each phase
2. **Preserve planning context** - Maintain design decisions and requirements
3. **Update documentation** - Keep both plans and summaries current
4. **Reference existing patterns** - Use summaries for implementation guidance
5. **Maintain quality** - Follow established standards for both plans and summaries

## Current Features

### Active Development
- **[IN-PROGRESS]-Stock Tracking Request Plan.md** - UI feature for users to request stock tracking

### Completed Implementations
- **stock_data_module_summary.md** - Technical analysis of the stock data processing pipeline

### Planned Features
- No draft plans currently

## Migration Notes

This structure consolidates the previous separate `plans/` and `technical_summaries/` directories into a unified feature documentation system. The workflow now provides clear progression from planning to implementation while preserving context and maintaining comprehensive documentation.
