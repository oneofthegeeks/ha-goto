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