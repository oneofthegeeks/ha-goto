#!/bin/bash

# GoTo SMS Integration Update Script
# This script helps you update the integration on your Home Assistant instance

set -e  # Exit on any error

echo "🔄 GoTo SMS Integration Update"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect Home Assistant installation type
detect_ha_install() {
    print_status "Detecting Home Assistant installation..."
    
    # Check for Home Assistant OS (most common)
    if [ -d "/config" ] && [ -f "/config/configuration.yaml" ]; then
        print_success "Detected: Home Assistant OS"
        HA_CONFIG="/config"
        return 0
    fi
    
    # Check for Home Assistant Container
    if [ -d "/config" ] && [ -d "/config/custom_components" ]; then
        print_success "Detected: Home Assistant Container"
        HA_CONFIG="/config"
        return 0
    fi
    
    # Check for common config locations
    if [ -d "$HOME/.homeassistant" ]; then
        print_success "Detected: Home Assistant Core (user directory)"
        HA_CONFIG="$HOME/.homeassistant"
        return 0
    fi
    
    if [ -d "/opt/homeassistant" ]; then
        print_success "Detected: Home Assistant Core (system directory)"
        HA_CONFIG="/opt/homeassistant"
        return 0
    fi
    
    print_error "Could not automatically detect Home Assistant installation"
    return 1
}

# Function to backup existing installation
backup_integration() {
    local config_dir="$1"
    local backup_dir="$config_dir/custom_components/goto_sms.backup.$(date +%Y%m%d_%H%M%S)"
    
    if [ -d "$config_dir/custom_components/goto_sms" ]; then
        print_status "Creating backup of current installation..."
        cp -r "$config_dir/custom_components/goto_sms" "$backup_dir"
        print_success "Backup created: $backup_dir"
    else
        print_warning "No existing installation found to backup"
    fi
}

# Function to update the integration
update_integration() {
    local config_dir="$1"
    
    print_status "Updating GoTo SMS integration..."
    
    # Check if we're in the right directory
    if [ ! -d "custom_components/goto_sms" ]; then
        print_error "Please run this script from the ha-goto directory"
        print_error "Current directory: $(pwd)"
        print_error "Expected files: custom_components/goto_sms/"
        exit 1
    fi
    
    # Create custom_components directory if it doesn't exist
    if [ ! -d "$config_dir/custom_components" ]; then
        print_status "Creating custom_components directory..."
        mkdir -p "$config_dir/custom_components"
    fi
    
    # Remove old version if it exists
    if [ -d "$config_dir/custom_components/goto_sms" ]; then
        print_status "Removing old version..."
        rm -rf "$config_dir/custom_components/goto_sms"
    fi
    
    # Copy the new integration
    print_status "Installing updated integration..."
    cp -r custom_components/goto_sms "$config_dir/custom_components/"
    
    # Set proper permissions
    print_status "Setting permissions..."
    chmod -R 755 "$config_dir/custom_components/goto_sms"
    
    print_success "Update complete!"
}

# Function to check for git repository
check_git_repo() {
    if [ -d ".git" ]; then
        print_status "Git repository detected, pulling latest changes..."
        git pull origin main
        print_success "Latest changes pulled from repository"
    else
        print_warning "Not a git repository. Please ensure you have the latest version."
    fi
}

# Main update function
main() {
    # Check for git repository and pull updates
    check_git_repo
    
    # Try to auto-detect Home Assistant installation
    if detect_ha_install; then
        print_status "Found Home Assistant installation at: $HA_CONFIG"
        
        # Backup existing installation
        backup_integration "$HA_CONFIG"
        
        # Update the integration
        update_integration "$HA_CONFIG"
        
        echo ""
        print_success "Update completed successfully!"
        echo ""
        echo "📋 Next steps:"
        echo "1. Restart Home Assistant"
        echo "2. Check the CHANGELOG for any breaking changes"
        echo "3. Test the integration with a simple SMS"
        echo "4. Review your automations if there were major changes"
        echo ""
        echo "📖 For detailed instructions, see: https://github.com/oneofthegeeks/ha-goto"
        echo ""
        echo "🔧 If you encounter issues, you can restore from backup:"
        echo "   rm -rf $HA_CONFIG/custom_components/goto_sms"
        echo "   cp -r $HA_CONFIG/custom_components/goto_sms.backup.* $HA_CONFIG/custom_components/goto_sms"
        
    else
        # Manual installation
        echo ""
        echo "Please provide your Home Assistant configuration directory:"
        echo "Common locations:"
        echo "  - Home Assistant OS: /config"
        echo "  - Docker: /path/to/config"
        echo "  - Core: ~/.homeassistant or /opt/homeassistant"
        echo ""
        read -p "Enter your config directory path: " config_path
        
        if [ -d "$config_path" ]; then
            backup_integration "$config_path"
            update_integration "$config_path"
            
            echo ""
            print_success "Update completed successfully!"
            echo ""
            echo "📋 Next steps:"
            echo "1. Restart Home Assistant"
            echo "2. Check the CHANGELOG for any breaking changes"
            echo "3. Test the integration with a simple SMS"
            
        else
            print_error "Directory not found: $config_path"
            echo "Please check the path and try again."
            exit 1
        fi
    fi
}

# Run the script
main 