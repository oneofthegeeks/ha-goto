#!/bin/bash

# GoTo SMS Integration Installation Script
# This script helps you install the integration on your Home Assistant instance

echo "🚀 GoTo SMS Integration Installation"
echo "===================================="

# Function to detect Home Assistant installation type
detect_ha_install() {
    echo "Detecting Home Assistant installation..."
    
    # Check for Home Assistant OS
    if [ -d "/config" ] && [ -f "/config/configuration.yaml" ]; then
        echo "✅ Detected: Home Assistant OS"
        HA_CONFIG="/config"
        return 0
    fi
    
    # Check for common config locations
    if [ -d "$HOME/.homeassistant" ]; then
        echo "✅ Detected: Home Assistant Core (user directory)"
        HA_CONFIG="$HOME/.homeassistant"
        return 0
    fi
    
    if [ -d "/opt/homeassistant" ]; then
        echo "✅ Detected: Home Assistant Core (system directory)"
        HA_CONFIG="/opt/homeassistant"
        return 0
    fi
    
    echo "❌ Could not automatically detect Home Assistant installation"
    return 1
}

# Main installation function
install_integration() {
    local config_dir="$1"
    
    echo ""
    echo "📁 Installing to: $config_dir"
    
    # Create custom_components directory if it doesn't exist
    if [ ! -d "$config_dir/custom_components" ]; then
        echo "📂 Creating custom_components directory..."
        mkdir -p "$config_dir/custom_components"
    fi
    
    # Copy the integration
    echo "📋 Copying GoTo SMS integration..."
    cp -r custom_components/goto_sms "$config_dir/custom_components/"
    
    # Set proper permissions
    echo "🔐 Setting permissions..."
    chmod -R 755 "$config_dir/custom_components/goto_sms"
    
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "Next steps:"
    echo "1. Restart Home Assistant"
    echo "2. Go to Settings → Devices & Services"
    echo "3. Click 'Add Integration'"
    echo "4. Search for 'GoTo SMS'"
    echo "5. Follow the configuration wizard"
    echo ""
    echo "📖 For detailed instructions, see: https://github.com/oneofthegeeks/ha-goto"
}

# Main script
main() {
    # Try to auto-detect
    if detect_ha_install; then
        echo ""
        read -p "Install to $HA_CONFIG? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_integration "$HA_CONFIG"
            exit 0
        fi
    fi
    
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
        install_integration "$config_path"
    else
        echo "❌ Directory not found: $config_path"
        echo "Please check the path and try again."
        exit 1
    fi
}

# Run the script
main 