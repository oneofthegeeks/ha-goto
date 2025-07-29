# Contributing to GoTo SMS Integration

Thank you for your interest in contributing to the GoTo SMS Home Assistant integration! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Issues

Before creating bug reports, please check the existing issues to avoid duplicates. When creating an issue, please include:

- **Home Assistant version**: The version you're running
- **Integration version**: The version of this integration
- **Python version**: Your Python version
- **Description**: A clear description of the problem
- **Steps to reproduce**: Detailed steps to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Logs**: Relevant logs from Home Assistant

### Feature Requests

We welcome feature requests! Please include:

- **Description**: A clear description of the feature
- **Use case**: Why this feature would be useful
- **Implementation ideas**: Any thoughts on how it might be implemented

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow the coding standards below
4. **Test your changes**: Ensure everything works as expected
5. **Commit your changes**: Use clear, descriptive commit messages
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**: Provide a clear description of the changes

## Development Setup

### Prerequisites

- Python 3.8+
- Home Assistant (for testing)
- GoTo Connect account with API access

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/ha-goto.git
   cd ha-goto
   ```

2. **Install development tools** (optional):
   ```bash
   pip install black flake8 isort
   ```

3. **Copy to Home Assistant**:
   ```bash
   cp -r custom_components/goto_sms /path/to/homeassistant/config/custom_components/
   ```

4. **Test the integration**:
   - Restart Home Assistant
   - Configure the integration through the UI
   - Test SMS functionality

## Coding Standards

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions small and focused

### Home Assistant Integration

- Follow Home Assistant's [integration development guidelines](https://developers.home-assistant.io/docs/creating_integration_manifest/)
- Use async/await patterns
- Implement proper error handling
- Add comprehensive logging

### File Structure

```
custom_components/goto_sms/
├── __init__.py              # Integration initialization
├── manifest.json            # Integration metadata
├── const.py                # Constants and configuration
├── oauth.py                # OAuth2 token management
├── notify.py               # SMS notification service
├── config_flow.py          # Configuration flow
├── services.yaml           # Service definitions
└── translations/
    └── en/
        └── config_flow.json # UI translations
```

## Testing

### Manual Testing

1. **Install the integration** in a test Home Assistant instance
2. **Configure OAuth2 credentials** through the UI
3. **Test SMS sending** using the notification service
4. **Verify token refresh** by waiting for token expiration
5. **Test error handling** by using invalid credentials

### Automated Testing

The integration is tested through GitHub Actions. For local testing:

1. **Install development tools**:
   ```bash
   pip install black flake8 isort
   ```

2. **Run linting checks**:
   ```bash
   black --check custom_components/goto_sms/
   flake8 custom_components/goto_sms/
   isort --check-only custom_components/goto_sms/
   ```

## Release Process

1. **Update version** in `manifest.json`
2. **Update CHANGELOG.md** with new features/fixes
3. **Create a release** on GitHub
4. **Tag the release** with the version number

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

## Questions?

If you have questions about contributing, please:

1. Check the existing issues and discussions
2. Create a new issue with the "question" label
3. Join the Home Assistant community forums

Thank you for contributing to the GoTo SMS integration! 