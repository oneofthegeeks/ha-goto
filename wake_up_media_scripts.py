#!/usr/bin/env python3
"""
Wake-Up Media Scripts for Home Assistant
This script provides helper functions for managing wake-up media content
"""

import json
import os
import requests
from typing import Dict, List, Optional
import yaml

class WakeUpMediaManager:
    """Manages wake-up media content and playlists"""
    
    def __init__(self, config_file: str = "wake_up_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.get_default_config()
    
    def save_config(self):
        """Save configuration to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "media_sources": {
                "nature_sounds": [
                    "https://www.soundjay.com/misc/sounds/bird-chirping-01.wav",
                    "https://www.soundjay.com/misc/sounds/rain-01.wav",
                    "https://www.soundjay.com/misc/sounds/ocean-waves-01.wav"
                ],
                "gentle_music": [
                    "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",  # Morning Coffee
                    "spotify:playlist:37i9dQZF1DX0XUsuxWHRQd",  # Relaxing Morning
                    "spotify:playlist:37i9dQZF1DX4WYpdgoIcn6"   # Chill Hits
                ],
                "alarm_sounds": [
                    "https://www.soundjay.com/misc/sounds/alarm-clock-01.wav",
                    "https://www.soundjay.com/misc/sounds/bell-ringing-01.wav"
                ],
                "custom_playlists": [
                    "spotify:playlist:YOUR_CUSTOM_PLAYLIST_ID"
                ]
            },
            "tv_content": {
                "morning_videos": [
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Replace with gentle morning content
                    "https://www.youtube.com/watch?v=YOUR_MORNING_VIDEO_ID"
                ],
                "nature_channels": [
                    "YouTube: Nature Sounds",
                    "YouTube: Relaxing Morning"
                ]
            },
            "tts_messages": [
                "Good morning! Time to wake up!",
                "Rise and shine! A new day awaits!",
                "Good morning! Let's start the day with energy!",
                "Wake up, sleepyhead! Time to conquer the day!"
            ]
        }
    
    def add_media_source(self, category: str, source: str):
        """Add a new media source to a category"""
        if category not in self.config["media_sources"]:
            self.config["media_sources"][category] = []
        
        if source not in self.config["media_sources"][category]:
            self.config["media_sources"][category].append(source)
            self.save_config()
            print(f"Added {source} to {category}")
        else:
            print(f"{source} already exists in {category}")
    
    def remove_media_source(self, category: str, source: str):
        """Remove a media source from a category"""
        if category in self.config["media_sources"]:
            if source in self.config["media_sources"][category]:
                self.config["media_sources"][category].remove(source)
                self.save_config()
                print(f"Removed {source} from {category}")
            else:
                print(f"{source} not found in {category}")
        else:
            print(f"Category {category} not found")
    
    def get_random_media(self, category: str) -> Optional[str]:
        """Get a random media source from a category"""
        import random
        
        if category in self.config["media_sources"]:
            sources = self.config["media_sources"][category]
            if sources:
                return random.choice(sources)
        return None
    
    def get_random_tts_message(self) -> str:
        """Get a random TTS message"""
        import random
        return random.choice(self.config["tts_messages"])
    
    def generate_home_assistant_script(self) -> str:
        """Generate Home Assistant script configuration for media management"""
        script_content = """
# Generated Media Management Script
script:
  play_random_wake_up_media:
    alias: "Play Random Wake Up Media"
    description: "Plays random media based on selected category"
    sequence:
      - choose:
          - conditions:
              - condition: state
                entity_id: input_select.wake_up_sound
                state: "Nature Sounds"
            sequence:
              - service: media_player.play_media
                target:
                  entity_id: media_player.sons_google_speaker
                data:
                  media_content_id: "{{ states('sensor.random_nature_sound') }}"
                  media_content_type: "music"
          
          - conditions:
              - condition: state
                entity_id: input_select.wake_up_sound
                state: "Gentle Music"
            sequence:
              - service: media_player.play_media
                target:
                  entity_id: media_player.sons_google_speaker
                data:
                  media_content_id: "{{ states('sensor.random_gentle_music') }}"
                  media_content_type: "music"
          
          - conditions:
              - condition: state
                entity_id: input_select.wake_up_sound
                state: "Alarm Clock"
            sequence:
              - service: tts.google_translate_say
                target:
                  entity_id: media_player.sons_google_speaker
                data:
                  message: "{{ states('sensor.random_tts_message') }}"
                  language: "en"
"""
        return script_content
    
    def create_media_sensors(self) -> str:
        """Create Home Assistant sensors for random media selection"""
        sensor_content = """
# Random Media Selection Sensors
template:
  - sensor:
      - name: "Random Nature Sound"
        state: >
          {% set sounds = [
            "https://www.soundjay.com/misc/sounds/bird-chirping-01.wav",
            "https://www.soundjay.com/misc/sounds/rain-01.wav",
            "https://www.soundjay.com/misc/sounds/ocean-waves-01.wav"
          ] %}
          {{ sounds | random }}
        icon: mdi:bird
        
      - name: "Random Gentle Music"
        state: >
          {% set playlists = [
            "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
            "spotify:playlist:37i9dQZF1DX0XUsuxWHRQd",
            "spotify:playlist:37i9dQZF1DX4WYpdgoIcn6"
          ] %}
          {{ playlists | random }}
        icon: mdi:music
        
      - name: "Random TTS Message"
        state: >
          {% set messages = [
            "Good morning! Time to wake up!",
            "Rise and shine! A new day awaits!",
            "Good morning! Let's start the day with energy!",
            "Wake up, sleepyhead! Time to conquer the day!"
          ] %}
          {{ messages | random }}
        icon: mdi:message-text
"""
        return sensor_content

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Wake-Up Media Manager")
    parser.add_argument("--add", nargs=2, metavar=("CATEGORY", "SOURCE"),
                       help="Add a media source to a category")
    parser.add_argument("--remove", nargs=2, metavar=("CATEGORY", "SOURCE"),
                       help="Remove a media source from a category")
    parser.add_argument("--list", action="store_true",
                       help="List all media sources")
    parser.add_argument("--generate-script", action="store_true",
                       help="Generate Home Assistant script")
    parser.add_argument("--generate-sensors", action="store_true",
                       help="Generate Home Assistant sensors")
    
    args = parser.parse_args()
    
    manager = WakeUpMediaManager()
    
    if args.add:
        category, source = args.add
        manager.add_media_source(category, source)
    elif args.remove:
        category, source = args.remove
        manager.remove_media_source(category, source)
    elif args.list:
        print(json.dumps(manager.config, indent=2))
    elif args.generate_script:
        print(manager.generate_home_assistant_script())
    elif args.generate_sensors:
        print(manager.create_media_sensors())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()