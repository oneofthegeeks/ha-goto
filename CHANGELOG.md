# Changelog

All notable changes to the GoTo SMS Home Assistant integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.8] - 2025-01-XX

### Fixed
- **Async/Await Issues**: Fixed runtime warnings caused by unawaited coroutines
- **Token Refresh**: Properly handled async operations during token refresh
- **Re-authentication**: Fixed async flow for re-authentication triggers
- **Config Entry Updates**: Improved async handling of config entry updates
- **Runtime Warnings**: Eliminated "coroutine was never awaited" warnings

### Technical Changes
- Updated `save_tokens()` to use proper async task creation
- Fixed `_trigger_reauth()` to avoid unawaited coroutines
- Added `_async_update_config_entry()` and `_async_trigger_reauth()` methods
- Improved error handling for async operations
- Enhanced logging for async operation debugging

## [1.2.7] - 2025-01-XX

### Fixed
- **Version Display**: Updated manifest.json to show correct version 1.2.7
- **UI Consistency**: Ensures integration page displays correct version
- **Version Alignment**: Maintains consistency between manifest and release tags

## [1.2.6] - 2025-01-XX

### Fixed
- **Version Display**: Updated manifest.json to show correct version 1.2.6
- **UI Consistency**: Ensures integration page displays correct version
- **Version Alignment**: Maintains consistency between manifest and release tags

## [1.2.5] - 2025-01-XX

### Fixed
- **Code Formatting**: Applied black formatting to `__init__.py`
- **CI/CD Workflow**: Fixed workflow failures due to formatting issues
- **Code Quality**: Ensures consistent formatting across the codebase

## [1.2.4] - 2025-01-XX

### Fixed
- **Version Display**: Updated manifest.json to show correct version 1.2.4
- **Config Entry Error**: Fixed "Config entry was never loaded!" error
- **Service Cleanup**: Properly removes the service when unloading
- **Data Cleanup**: Correctly cleans up integration data
- **Error Handling**: Added proper error handling for unload process

### Technical Changes
- Removed platform unloading that was causing errors
- Added proper service removal with `hass.services.async_remove()`
- Added data cleanup with error handling
- Added logging for successful unload

## [1.2.3] - 2025-01-XX

### Fixed
- **Code Formatting**: Applied black formatting to fix CI/CD workflow
- **Formatting Issues**: Fixed formatting in notify.py, config_flow.py, and oauth.py
- **CI/CD Pipeline**: Ensures consistent code formatting across environments

## [1.2.2] - 2025-01-XX

### Added
- **Re-authentication Flow**: Added proper re-authentication support following Home Assistant best practices
- **Automatic Re-auth Trigger**: Integration automatically triggers re-authentication when tokens expire
- **UI Re-authentication**: Users can re-authenticate through the Home Assistant UI without deleting the integration
- **Enhanced Error Handling**: Better error messages and user guidance for authentication issues

### Features
- Seamless re-authentication without losing configuration
- Automatic detection of expired tokens
- User-friendly re-authentication prompts in the UI
- Preserved configuration during re-authentication

### Technical Improvements
- Added `async_step_reauth` and `async_step_reauth_oauth` methods
- Implemented `_trigger_reauth` method in OAuth manager
- Enhanced error messages with re-authentication guidance
- Updated translations for re-authentication flow

### Documentation
- Added re-authentication troubleshooting section
- Updated user guidance for authentication issues

## [1.2.1] - 2025-01-XX

### Fixed
- **OAuth Debugging**: Added comprehensive debugging to OAuth manager
- **Enhanced Error Messages**: More informative error messages for authentication failures
- **Token Refresh Handling**: Improved handling of expired tokens with automatic refresh attempts
- **User Guidance**: Clear instructions when re-authentication is needed

### Added
- **Debug Logging**: Added detailed debugging throughout the OAuth flow
- **Better Error Handling**: Enhanced error messages and debugging information
- **Token Validation**: Better handling of expired or invalid tokens
- **User Guidance**: Clear instructions when re-authentication is needed

### Technical Improvements
- Enhanced debugging to `get_headers()` method
- Improved `load_tokens()` with better error handling
- Better `get_valid_token()` debugging
- More detailed error messages suggesting re-authentication

## [1.2.0] - 2025-01-XX

### Added
- **Template Support**: Added full Home Assistant template support for dynamic SMS messages
- **Template Data**: Added optional `data` parameter for template variables
- **Template Validation**: Automatic template rendering with error handling
- **Enhanced Examples**: Updated documentation with comprehensive template examples
- **Template Logging**: Added debug logging for template rendering process

### Features
- Dynamic message content using Home Assistant templates
- Support for entity states, time functions, and custom data
- Automatic template detection and rendering
- Graceful fallback if template rendering fails
- Comprehensive template examples in documentation

### Technical Improvements
- Added `_render_template` method for template processing
- Enhanced service schema with template data support
- Improved error handling for template rendering
- Better logging for template debugging

### Documentation
- Added template usage examples
- Updated automation examples with templates
- Enhanced configuration examples
- Added template troubleshooting section

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
- Additional language translations
- Unit tests and automated testing 