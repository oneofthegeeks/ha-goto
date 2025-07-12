# Changelog

All notable changes to the GoTo SMS Home Assistant integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Initial release of GoTo SMS integration
- OAuth2 authentication with GoTo Connect API
- Automatic token refresh functionality
- SMS notification service (`notify.goto_sms`)
- Config flow for UI-based configuration
- Support for custom sender IDs
- Comprehensive error handling and logging
- English translations for the UI
- MIT License and contribution guidelines

### Features
- Send SMS messages via GoTo Connect API
- Secure credential storage using Home Assistant config entries
- User-friendly setup process through the UI
- Support for multiple phone numbers
- Detailed logging for troubleshooting

### Technical Details
- Built with async/await patterns for better performance
- Follows Home Assistant integration development guidelines
- Includes comprehensive documentation
- Modular code structure for easy maintenance

## [Unreleased]

### Planned
- Support for multiple GoTo Connect accounts
- SMS delivery status tracking
- Template support for dynamic messages
- Additional language translations
- Unit tests and automated testing
- HACS (Home Assistant Community Store) integration 