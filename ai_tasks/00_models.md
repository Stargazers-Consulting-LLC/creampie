Create the models associated with a user application. Use SQLAlchemy and assume the models will be interacted mostly through FastAPI.

# User Model

## Core Fields

- `id`: Unique identifier (UUID)
- `email`: User's email address (unique)
- `password`: Hashed password
- `username`: Display name (unique)
- `firstName`: User's first name
- `lastName`: User's last name
- `createdAt`: Account creation timestamp
- `updatedAt`: Last update timestamp

## Account Settings

- `isVerified`: Email verification status
- `isActive`: Account status
- `role`: User role (e.g., admin, user)
- `preferences`: User preferences object
  - `theme`: UI theme preference
  - `notifications`: Notification settings
  - `language`: Preferred language

## Security

- `lastLogin`: Last login timestamp
- `passwordResetToken`: Token for password reset
- `passwordResetExpires`: Password reset token expiry
- `twoFactorEnabled`: 2FA status
- `twoFactorSecret`: 2FA secret key

## Metadata

- `metadata`: Additional custom fields
- `tags`: User categorization tags

# Session Model

## Core Fields

- `userId`: Foreign key to User model (UUID)
- `sessionId`: Unique session identifier (UUID)
- `createdAt`: Session creation timestamp
- `expiresAt`: Session expiration timestamp
- `lastActivity`: Last activity timestamp

## Security

- `ipAddress`: IP address of session origin
- `userAgent`: Browser/client information
- `deviceId`: Unique device identifier
- `isValid`: Session validity status
- `revokedAt`: Timestamp if session was revoked

## Metadata

- `location`: Geographic location data
- `platform`: Device platform information
- `browser`: Browser information
- `metadata`: Additional session metadata

## Relationships

- `user`: One-to-one relationship with User model

# Profile Model

## Core Fields

- `userId`: Foreign key to User model (UUID)
- `displayName`: User's display name
- `avatar`: Profile picture URL
- `bio`: User biography/description
- `createdAt`: Profile creation timestamp
- `updatedAt`: Last update timestamp

## Contact Information

- `email`: Primary email address
- `phone`: Phone number
- `website`: Personal website URL
- `socialLinks`: Social media links object
  - `twitter`: Twitter handle
  - `linkedin`: LinkedIn profile
  - `github`: GitHub profile
  - `instagram`: Instagram handle

## Personal Details

- `location`: Geographic location
- `timezone`: User's timezone
- `language`: Preferred language
- `birthDate`: Date of birth
- `gender`: Gender identity

## Professional Information

- `occupation`: Current occupation
- `company`: Current company
- `skills`: Array of skills
- `interests`: Array of interests
- `education`: Education history
- `experience`: Work experience

## Metadata

- `metadata`: Additional custom fields
- `tags`: Profile categorization tags

# Notification Model

## Core Fields

- `userId`: Foreign key to User model (UUID)
- `notificationId`: Unique notification identifier (UUID)
- `type`: Notification type (e.g., system, alert, message)
- `title`: Notification title
- `message`: Notification content
- `createdAt`: Creation timestamp
- `readAt`: When notification was read
- `isRead`: Read status

## Action

- `actionType`: Type of action (e.g., link, button)
- `actionUrl`: URL for notification action
- `actionLabel`: Action button text
- `priority`: Notification priority level

## Metadata

- `category`: Notification category
- `metadata`: Additional notification data
- `tags`: Notification categorization tags

# Activity Log Model

## Core Fields

- `userId`: Foreign key to User model (UUID)
- `activityId`: Unique activity identifier (UUID)
- `type`: Activity type
- `description`: Activity description
- `createdAt`: Activity timestamp
- `ipAddress`: IP address
- `userAgent`: Browser/client information

## Context

- `resourceType`: Type of resource affected
- `resourceId`: ID of affected resource
- `changes`: Object describing changes made
- `status`: Activity status

## Metadata

- `category`: Activity category
- `metadata`: Additional activity data
- `tags`: Activity categorization tags
