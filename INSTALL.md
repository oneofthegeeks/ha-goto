# Installation Guide for GoTo SMS Integration

This guide will help you install the GoTo SMS integration on your Home Assistant instance.

## 🚀 **Quick Installation**

### **Option 1: Automated Installation (Recommended)**

Run the installation script from your current directory:

```bash
./install.sh
```

The script will:
- Auto-detect your Home Assistant installation
- Copy the integration files
- Set proper permissions
- Guide you through the next steps

### **Option 2: Manual Installation**

#### **Step 1: Find Your Home Assistant Config Directory**

**Home Assistant OS:**
```bash
# Usually mounted at /config
ls /config
```

**Home Assistant Container (Docker):**
```bash
# Check your docker-compose.yml or docker run command
# Look for the volume mount like: -v /path/to/config:/config
```

**Home Assistant Core:**
```bash
# Common locations:
ls ~/.homeassistant
# or
ls /opt/homeassistant
```

#### **Step 2: Copy the Integration**

```bash
# Create custom_components directory (if it doesn't exist)
mkdir -p /path/to/your/config/custom_components

# Copy the integration
cp -r custom_components/goto_sms /path/to/your/config/custom_components/

# Set permissions
chmod -R 755 /path/to/your/config/custom_components/goto_sms
```

## 🔧 **Configuration Steps**

### **Step 1: Restart Home Assistant**

After copying the files, restart Home Assistant to load the new integration.

### **Step 2: Add the Integration**

1. Open Home Assistant in your browser
2. Go to **Settings** → **Devices & Services**
3. Click **Add Integration**
4. Search for **"GoTo SMS"**
5. Click on the integration

### **Step 3: Configure OAuth2**

1. **Enter your GoTo Connect credentials:**
   - Client ID: Your GoTo Connect OAuth2 Client ID
   - Client Secret: Your GoTo Connect OAuth2 Client Secret

2. **Complete the OAuth2 flow:**
   - Click the authorization URL provided
   - Authorize the application in your browser
   - Copy the authorization response
   - Paste it back into the configuration form

3. **Test the integration:**
   - Use Developer Tools → Services
   - Call the `notify.goto_sms` service
   - Test with a simple message

## 📋 **Prerequisites**

### **GoTo Connect Setup**

Before installing, you need:

1. **GoTo Connect Account** with SMS capabilities
2. **OAuth2 Application** created in GoTo Connect developer portal
3. **API Credentials** (Client ID and Client Secret)

### **Creating OAuth2 Application**

1. Log into your GoTo Connect developer portal
2. Create a new OAuth2 application
3. Set the redirect URI to: `https://home-assistant.io/auth/callback`
4. Note your Client ID and Client Secret

## 🧪 **Testing the Installation**

### **Test SMS Service**

```yaml
service: notify.goto_sms
data:
  message: "Hello from Home Assistant!"
  target: "+1234567890"
  sender_id: "TestSystem"
```

### **Check Logs**

Enable debug logging in your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.goto_sms: debug
```

## 🔍 **Troubleshooting**

### **Integration Not Found**

- Ensure files are copied to the correct location
- Restart Home Assistant completely
- Check file permissions (755 for directories, 644 for files)

### **OAuth2 Issues**

- Verify your Client ID and Client Secret
- Check that the redirect URI matches exactly
- Ensure your GoTo Connect account has SMS permissions

### **SMS Not Sending**

- Check the target phone number format (include country code)
- Verify your GoTo Connect account has SMS capabilities
- Review the Home Assistant logs for detailed error messages

## 🔄 **Updating the Integration**

### **HACS Users (Automatic Updates)**

If you installed via HACS, updates are handled automatically:

1. **Check for Updates**: HACS will show update notifications
2. **Update**: Go to HACS → Integrations → GoTo SMS → Update
3. **Restart**: Restart Home Assistant after updating

### **Manual Installation Updates**

#### **Option 1: Using the Install Script (Recommended)**

```bash
# Navigate to your installation directory
cd /path/to/ha-goto

# Pull latest changes
git pull origin main

# Run the install script (handles backups automatically)
./install.sh
```

#### **Option 2: Manual Update Process**

1. **Backup Current Installation**:
   ```bash
   cp -r /config/custom_components/goto_sms /config/custom_components/goto_sms.backup.$(date +%Y%m%d)
   ```

2. **Download Latest Version**:
   ```bash
   # Option A: Clone fresh copy
   git clone https://github.com/oneofthegeeks/ha-goto.git ha-goto-new
   
   # Option B: Update existing clone
   cd /path/to/ha-goto
   git pull origin main
   ```

3. **Replace Integration Files**:
   ```bash
   # Remove old version
   rm -rf /config/custom_components/goto_sms
   
   # Copy new version
   cp -r custom_components/goto_sms /config/custom_components/
   
   # Set permissions
   chmod -R 755 /config/custom_components/goto_sms
   ```

4. **Restart Home Assistant**

#### **Option 3: Using the Dedicated Update Script (Recommended)**

The repository includes a dedicated update script:

```bash
# Run the update script
./update.sh
```

The script will:
- Automatically detect your Home Assistant installation
- Create a backup of your current installation
- Pull the latest changes from the repository
- Install the updated integration
- Provide clear next steps

#### **Option 4: Create Your Own Update Script**

Create a reusable update script:

```bash
#!/bin/bash
# update_goto_sms.sh
set -e

echo "🔄 Updating GoTo SMS Integration..."

# Navigate to installation directory
cd /path/to/ha-goto

# Backup current version
echo "📦 Creating backup..."
cp -r /config/custom_components/goto_sms /config/custom_components/goto_sms.backup.$(date +%Y%m%d_%H%M%S)

# Pull latest changes
echo "⬇️  Downloading latest version..."
git pull origin main

# Run install script
echo "🔧 Installing update..."
./install.sh

echo "✅ Update complete! Please restart Home Assistant."
```

Make it executable: `chmod +x update_goto_sms.sh`

### **Post-Update Checklist**

After updating:

1. ✅ **Restart Home Assistant**
2. ✅ **Check the CHANGELOG** for breaking changes
3. ✅ **Test the integration** with a simple SMS
4. ✅ **Review automations** if there were major changes
5. ✅ **Check logs** for any errors

### **Troubleshooting Updates**

#### **Integration Not Working After Update**

1. **Enable Debug Logging**:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.goto_sms: debug
   ```

2. **Check for Errors** in Home Assistant logs

3. **Restore from Backup** if needed:
   ```bash
   rm -rf /config/custom_components/goto_sms
   cp -r /config/custom_components/goto_sms.backup.* /config/custom_components/goto_sms
   ```

4. **Re-authenticate** if OAuth tokens are invalid

#### **Version Compatibility**

- Check `manifest.json` for minimum Home Assistant version
- Review CHANGELOG for breaking changes
- Test thoroughly after major version updates

## 📞 **Support**

If you encounter issues:

1. Check the [GitHub repository](https://github.com/oneofthegeeks/ha-goto) for updates
2. Review the [Home Assistant community forums](https://community.home-assistant.io/)
3. Enable debug logging and check the logs for detailed error information

## 🎉 **Success!**

Once configured, you can use the `notify.goto_sms` service in:
- Automations
- Scripts
- Manual service calls
- Templates

Your GoTo SMS integration is now ready to send SMS messages from Home Assistant! 