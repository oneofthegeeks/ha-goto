# Changelog

All notable changes to the GoTo SMS Home Assistant integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.8] - 2025-11-19

### Fixed
- **OAuth Flow**: Fixed authorization URL not displaying in config flow
- **Reauth Context**: Fixed missing `entry_id` in reauth flow context causing KeyError
- **Config Flow Display**: Simplified OAuth form to properly display authorization URL using translation file
- **Redirect URI**: Updated documentation to use local callback URL instead of public URL

### Technical Improvements
- **Config Flow**: Removed unused description variable and properly use `description_placeholders`
- **Translation Strings**: Updated to use plain text formatting for better UI compatibility
- **Reauth Flow**: Added required `entry_id` to all reauth context initializations
- **Documentation**: Updated README with local callback URL guidance for OAuth setup

### What This Fixes
- ✅ **Authorization URL now displays** properly during initial setup
- ✅ **No more `'entry_id'` KeyError** during re-authentication
- ✅ **Clearer OAuth instructions** with local callback URL examples
- ✅ **Better user experience** during OAuth configuration

## [1.3.7] - 2025-01-04

### Fixed
- **Thread Safety**: Fixed "Detected code that calls hass.config_entries.async_update_entry from a thread" error
- **Async Config Entry Updates**: Converted save_tokens to async to avoid thread safety issues
- **Async Token Fetching**: Converted fetch_token to async for proper async/await patterns
- **Config Flow Updates**: Updated config flow to handle async fetch_token calls

### Technical Improvements
- **Async save_tokens**: `save_tokens()` method now properly async and updates config entries in main event loop
- **Async fetch_token**: `fetch_token()` method now async and uses Home Assistant's HTTP client
- **Config Flow**: Updated to call async methods directly instead of using executor jobs
- **Thread Safety**: All config entry updates now happen in the main event loop

### What This Fixes
- ✅ **No more thread safety warnings** in Home Assistant logs
- ✅ **Proper async/await patterns** for all token operations
- ✅ **Thread-safe config entry updates** that won't cause Home Assistant crashes
- ✅ **Consistent async behavior** throughout the integration

## [1.3.6] - 2025-01-04

### Fixed
- **Async Coroutine Warning**: Fixed "coroutine was never awaited" warning in load_tokens method
- **Async Consistency**: Made load_tokens method async to properly handle async refresh_tokens calls
- **Startup Validation**: Fixed async calls in startup token validation
- **Periodic Refresh**: Fixed async calls in periodic token refresh

### Technical Improvements
- **Async load_tokens**: `load_tokens()` method now properly async
- **Consistent Async Pattern**: All token-related methods now follow proper async/await patterns
- **Startup Robustness**: Startup validation now properly handles async token loading
- **Periodic Refresh**: Periodic refresh now properly handles async token loading

### What This Fixes
- ✅ **No more "coroutine was never awaited" warnings**
- ✅ **Proper async/await patterns throughout the integration**
- ✅ **Consistent async behavior** for all token operations
- ✅ **Reliable startup and periodic refresh** operations

## [1.3.5] - 2025-01-04

### Fixed
- **Event Loop Blocking**: Fixed blocking HTTP requests that were causing event loop warnings
- **Async HTTP Client**: Converted all HTTP requests to use Home Assistant's async HTTP client
- **Token Refresh**: Fixed async/await patterns in token refresh operations
- **SMS Sending**: Converted SMS sending to use async HTTP requests
- **Thread Safety**: Eliminated all blocking operations in async contexts

### Technical Improvements
- **Async Token Refresh**: `refresh_tokens()` method now properly async
- **Async SMS Sending**: `_send_sms()` method now uses async HTTP client
- **Async Headers**: `get_headers()` method now properly async
- **Async Token Validation**: `get_valid_token()` method now properly async
- **Home Assistant HTTP Client**: Using `async_get_clientsession()` instead of `requests`

### Performance Improvements
- **No More Blocking**: Eliminated all blocking HTTP requests in async contexts
- **Better Error Handling**: Improved error handling for network operations
- **Proper Async Patterns**: All async operations now follow Home Assistant best practices
- **Event Loop Friendly**: Integration no longer blocks the Home Assistant event loop

## [1.3.4] - 2025-01-04

### Fixed
- **Authentication Persistence**: Significantly improved token refresh reliability and persistence
- **Token Validation**: Reduced aggressive token validation from 15 minutes to 5 minutes before expiry
- **Thread Safety**: Fixed async/sync mixing issues in token saving operations
- **Refresh Token Handling**: Improved handling of refresh token updates during token refresh
- **Error Recovery**: Better error handling and recovery for authentication failures
- **Startup Robustness**: Improved startup token validation to not fail integration loading

### Technical Improvements
- **Less Aggressive Validation**: Token validation now checks 5 minutes before expiry instead of 15 minutes
- **Better Token Saving**: Fixed async operations in save_tokens() to avoid thread safety issues
- **Improved Refresh Logic**: Better handling of refresh token updates during token refresh operations
- **Enhanced Error Handling**: More robust error handling throughout the authentication flow
- **Startup Resilience**: Startup validation errors no longer prevent integration from loading

### Authentication Reliability
- **Proactive Refresh**: Tokens are refreshed 5 minutes before expiry for better reliability
- **Better Persistence**: Improved token saving mechanism ensures tokens persist properly
- **Reduced Re-authentication**: Less frequent re-authentication prompts due to better token management
- **Robust Recovery**: Better handling of network errors and API failures during token refresh

## [1.3.3] - 2025-01-04

### Fixed
- **Thread Safety Issues**: Removed automatic SMS tracking to eliminate thread safety conflicts
- **Async/Thread Conflicts**: Eliminated RuntimeError caused by calling async operations from sync context
- **Simplified Architecture**: Removed complex tracking logic that was causing Home Assistant crashes
- **Manual Tracking**: Users can now manually track SMS counts in their automations for better control

### Technical Improvements
- **Removed sensor.py**: Eliminated automatic sensor tracking that was causing thread safety issues
- **Simplified notify.py**: Removed all tracking methods and async/thread boundary complications
- **Better Error Handling**: No more thread safety violations or async_add_job deprecation warnings
- **Cleaner Code**: Reduced complexity and potential failure points

### User Experience
- **Manual Control**: Users have full control over when and how to track SMS messages
- **No More Crashes**: Eliminated the thread safety issues that were causing Home Assistant errors
- **Simple Setup**: Easy to set up manual tracking with input_number entities
- **Reliable Operation**: Integration now focuses solely on SMS sending without tracking complications

## [1.3.2] - 2025-01-04

### Fixed
- **Authentication Persistence**: Significantly improved token refresh and authentication persistence
- **Proactive Token Refresh**: Added periodic token refresh every 30 minutes to keep tokens fresh
- **Startup Token Validation**: Added startup validation to ensure tokens are valid when integration loads
- **Retry Logic**: Enhanced retry logic with exponential backoff for both token refresh and SMS sending
- **Token Validation**: More aggressive token validation (refreshes when within 15 minutes of expiry)
- **Error Handling**: Improved error handling and logging for authentication failures

### Technical Improvements
- **Periodic Refresh**: Added `async_track_time_interval` to refresh tokens every 30 minutes
- **Startup Validation**: Added startup token validation with 5-second delay for proper initialization
- **Enhanced Retry Logic**: Implemented 3-retry logic with exponential backoff for token refresh
- **Better Logging**: Improved debug logging for token validation and refresh operations
- **Rate Limiting**: Added handling for 429 rate limit responses with exponential backoff

### Authentication Robustness
- **Proactive Refresh**: Tokens are now refreshed 15 minutes before expiry instead of 5 minutes
- **Multiple Retry Attempts**: Token refresh now retries up to 3 times with exponential backoff
- **Startup Validation**: Integration validates and refreshes tokens on startup
- **Periodic Maintenance**: Automatic token refresh every 30 minutes ensures tokens stay fresh
- **Better Error Recovery**: Improved handling of network errors and API failures

## [1.3.1] - 2025-01-XX

### Fixed
- **SMS Counter Tracking**: Fixed issue where SMS message counters weren't updating when messages were sent
- **Async Service Calls**: Fixed async service calls using `async_add_job` instead of `async_create_task`
- **Sensor State Updates**: Improved sensor state updates for better counter tracking
- **Error Logging**: Enhanced error logging for better debugging of counter issues
- **Code Quality**: Added comprehensive testing scripts for validation without Home Assistant

### Technical Improvements
- Updated `_track_message_sent()` method with proper async patterns
- Added helper methods `_get_sensor_current_value()` and `_get_sensor_attr()`
- Improved error handling for counter updates
- Added `test_integration.py` for validation without Home Assistant dependencies
- Added `release_checklist.py` for release preparation

### Testing
- Added comprehensive validation script that tests file structure, syntax, and logic
- Added release checklist to ensure all components are ready for release
- Improved code formatting and quality checks

## [1.3.0] - 2025-01-XX

### Added
- **SMS Message Tracking**: Added automatic tracking of sent SMS messages
- **Dual Tracking Methods**: Support for both simple input_number and advanced sensor tracking
- **Dashboard Integration**: Easy integration with Home Assistant dashboards
- **Automatic Counter Management**: Daily/weekly/monthly tracking with automatic resets
- **Persistent Storage**: Message counts persist across Home Assistant restarts

### Features
- **Simple Input Number Tracking**: Easy setup with manual tracking
- **Advanced Sensor Tracking**: Automatic sensor with detailed attributes
- **Automatic Incrementing**: Counters increment automatically on successful SMS sends
- **Failed Message Handling**: Counters only increment for successful sends
- **Dashboard Compatibility**: Works with all Home Assistant dashboard cards

### Technical Improvements
- Added `sensor.py` for advanced SMS tracking capabilities
- Enhanced `notify.py` with dual tracking support
- Updated `__init__.py` to include sensor platform
- Added comprehensive documentation for tracking features
- Improved error handling for tracking operations

### Documentation
- Added detailed SMS tracking documentation
- Included dashboard examples and use cases
- Added troubleshooting guide for tracking features
- Updated README with tracking feature overview

## [1.2.11] - 2025-01-XX

### Fixed
- **Async Pattern Issues**: Fixed deprecated `async_add_job` usage with proper async patterns
- **Thread Safety**: Fixed "Detected code that calls hass.config_entries.async_update_entry from a thread" error
- **Authentication Robustness**: Improved automatic token refresh and re-authentication handling
- **Automatic Re-authentication**: Integration now automatically triggers re-authentication when tokens fail
- **Better Error Handling**: Enhanced error handling for authentication failures

### Technical Changes
- Updated `save_tokens()` to use proper async patterns with `async_create_task()`
- Fixed `_trigger_reauth()` to use proper async patterns
- Improved `refresh_tokens()` with automatic re-authentication on failure
- Enhanced `get_valid_token()` with better error handling and automatic re-authentication
- Eliminated deprecated `async_add_job` usage
- Improved authentication robustness with automatic retry logic

### Authentication Improvements
- **Automatic Token Refresh**: Tokens are automatically refreshed when they expire
- **Automatic Re-authentication**: When token refresh fails, re-authentication is automatically triggered
- **Better Error Recovery**: Integration handles authentication failures gracefully
- **Reduced Manual Intervention**: Users should rarely need to manually re-authenticate

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