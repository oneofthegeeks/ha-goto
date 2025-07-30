# Changelog

All notable changes to the GoTo SMS Home Assistant integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.10] - 2025-01-XX

### Fixed
- **Final Async/Await Issues**: Fixed remaining runtime warnings and thread safety issues
- **Thread Safety**: Fixed "Detected code that calls hass.config_entries.async_update_entry from a thread" error
- **Unawaited Coroutines**: Eliminated all "coroutine was never awaited" warnings
- **Config Entry Updates**: Properly handled async operations using callbacks
- **Re-authentication Flow**: Fixed async flow using proper callback approach

### Technical Changes
- Updated `save_tokens()` to use `async_add_job()` with callbacks instead of `async_create_task()`
- Fixed `_trigger_reauth()` to use `async_add_job()` with callbacks
- Improved thread safety by ensuring all async operations run in the main event loop
- Enhanced error handling for async operations
- Eliminated all unawaited coroutines

## [1.2.9] - 2025-01-XX

### Fixed
- **Additional Async/Await Issues**: Fixed remaining runtime warnings from unawaited coroutines
- **Config Entry Updates**: Improved async handling using executor jobs instead of unawaited tasks
- **Re-authentication Flow**: Fixed async flow to avoid creating unawaited coroutines
- **Runtime Warnings**: Eliminated remaining "coroutine was never awaited" warnings

### Technical Changes
- Updated `save_tokens()` to use `async_add_executor_job` instead of `async_create_task`
- Fixed `_trigger_reauth()` to use executor jobs for async operations
- Improved error handling for async operations
- Enhanced logging for async operation debugging

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
- Enhanced debugging to `