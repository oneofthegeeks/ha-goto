# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install the Integration

**Option A: HACS (Easiest)**
1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Add this repository as a custom repository in HACS
3. Search for "GoTo SMS" and install it
4. Restart Home Assistant

**Option B: Manual Installation**
```bash
# Download and run the installer
git clone https://github.com/oneofthegeeks/ha-goto.git
cd ha-goto
./install.sh
```

### 2. Get GoTo Connect Credentials

1. Go to [GoTo Connect Developer Portal](https://developer.goto.com/)
2. Create a new OAuth2 application
3. Set redirect URI to: `https://home-assistant.io/auth/callback`
4. Copy your Client ID and Client Secret

### 3. Configure in Home Assistant

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "GoTo SMS"
4. Enter your Client ID and Client Secret
5. Follow the OAuth2 authorization flow

### 4. Test It

Go to **Developer Tools** → **Services** and call:

```yaml
service: notify.goto_sms
data:
  message: "Hello from Home Assistant!"
  target: "+1234567890"
  sender_id: "+1234567890"  # Your GoTo phone number in E.164 format
```

## 🎉 You're Done!

Your GoTo SMS integration is now ready to use in automations, scripts, and manual service calls.

## 📚 Need More Help?

- Check the [full README](README.md) for detailed instructions
- Review the [troubleshooting section](README.md#troubleshooting)
- [Create an issue](https://github.com/oneofthegeeks/ha-goto/issues) if you need help 