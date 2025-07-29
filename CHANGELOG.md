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

## [1.1.0] - 2024-01-XX

### Added
- **Modern UI Interface**: Updated service to use form-based interface with selectors
- **Enhanced Service**: Changed from `notify.goto_sms` to `goto_sms.send_sms` for better integration
- **Phone Number Validation**: Added E.164 format validation for phone numbers
- **Multiline Message Support**: Added support for longer SMS messages with multiline text input
- **Enhanced Logging**: Added comprehensive debug logging throughout the OAuth2 process
- **HACS Support**: Added HACS configuration and quality scale improvements
- **Improved Error Handling**: Better error messages and debugging information
- **Updated Documentation**: Comprehensive updates to README, examples, and configuration files

### Changed
- Service name from `notify.goto_sms` to `goto_sms.send_sms`
- Made `sender_id` parameter required (must be in E.164 format)
- Enhanced OAuth2 token management with better error handling
- Updated all documentation and examples to reflect new service name

### Fixed
- Improved OAuth2 authorization code parsing to handle multiple input formats
- Enhanced token validation and refresh logic
- Better error messages for authentication issues

### Technical Improvements
- Added proper service schema with form interface
- Enhanced async token saving to prevent blocking
- Improved token validation with detailed logging
- Better integration with Home Assistant's service system

## [1.1.1] - 2025-01-28

### Fixed
- **GitHub Actions**: Fixed missing dependencies (`oauthlib`, `requests-oauthlib`) in CI/CD pipeline
- **Import Formatting**: Resolved import sorting issues across all Python files
- **Documentation**: Enhanced update instructions and repository cleanup

### Added
- **Update Script**: Added `update.sh` for easier user updates
- **Formatting Configuration**: Added `pyproject.toml` for consistent code formatting
- **Enhanced Documentation**: Comprehensive update instructions in README, INSTALL.md, and QUICKSTART.md

### Changed
- **Repository Cleanup**: Removed development files for clean release
- **GitHub Actions**: Streamlined dependency management
- **Documentation**: Added multiple update methods and troubleshooting guides

### Technical Improvements
- Consistent code formatting across environments
- Better CI/CD pipeline reliability
- Improved user experience with automated update scripts

## [Unreleased]

### Planned
- Support for multiple GoTo Connect accounts
- SMS delivery status tracking
- Template support for dynamic messages
- Additional language translations
- Unit tests and automated testing 