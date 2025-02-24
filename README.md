# DAVE - Discord Audio Virtual Entertainment

<a href="https://github.com/kmosoti/dave-discord-bot">
  <img src="dave_profile.png" alt="DAVE Profile" width="150px">
</a>

Welcome to **DAVE** – your friendly Discord bot for audio fun and server management. DAVE stands for **Discord Audio Virtual Entertainment**. He’s here to play your favorite tunes, manage your music queue, and occasionally drop a witty comment (or two).

## Features

- **Music Playback:**  
  Play songs by searching or using direct URLs. Whether you want to jam out or set the perfect background vibe, DAVE’s got you covered.

- **Queue Management:**  
  Add tracks to the queue, skip the ones that don’t hit the mark, or view what’s coming up next.

- **Modular Design:**  
  Built with a cog-based architecture, making it easy to extend DAVE’s abilities as new ideas strike.

- **External Audio Processing:**  
  Offloads heavy audio processing to a Lavalink server so that your music plays smooth as butter.

- **Structured Logging:**  
  DAVE logs events in JSON format, so even if something goes wrong, you’ll have all the details at your fingertips.

## Prerequisites

- **Python 3.10+**
- **Ubuntu** (or another compatible Linux distribution)
- **OpenJDK 17** – Required for the Lavalink server.
- **Git** – For fetching the code.

## Installation

1. **Clone the Repository**

   ```bash
   sudo git clone https://github.com/kmosoti/dave-discord-bot.git /opt/discord_bot
   ```

2. **Set Up a Virtual Environment and Install Dependencies**

   ```bash
   cd /opt/discord_bot
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

   *Note:* If conflicts arise from wavelink pulling in discord.py, install wavelink separately using the `--no-deps` flag so that py-cord remains the sole Discord library.

3. **Configure DAVE**

   Create a configuration file at `data/config.json` (or generate it from your Salt Pillar) with your secrets. Example:

   ```json
   {
     "DISCORD": {
       "DISCORD_TOKEN": "YOUR_DISCORD_BOT_TOKEN",
       "GUILD_IDS": [1234567890, 9876543210]
     },
     "LAVALINK": {
       "LAVALINK_HOST": "http://127.0.0.1",
       "LAVALINK_PORT": 2333,
       "LAVALINK_PASSWORD": "youshallnotpass"
     }
   }
   ```

4. **Set Up Systemd Services**

   - **Lavalink Server:**  
     Ensure Java is installed, download the Lavalink JAR (version 4.0.8 is recommended), and set up its service:

     ```bash
     sudo wget -q -O /opt/lavalink/lavalink.jar https://github.com/lavalink-devs/Lavalink/releases/download/4.0.8/Lavalink.jar
     sudo systemctl daemon-reload
     sudo systemctl enable lavalink
     sudo systemctl start lavalink
     ```

   - **DAVE Bot:**  
     Deploy the systemd service file (e.g., from `docs/discord-bot.service.jinja`) to `/etc/systemd/system/discord-bot.service`, then run:

     ```bash
     sudo systemctl daemon-reload
     sudo systemctl enable discord-bot
     sudo systemctl start discord-bot
     ```

## Usage

Once DAVE is up and running, control music playback with slash commands:

- **/play [query]**  
  Request a song by entering a search query or URL. DAVE will play the song immediately or add it to the queue if a track is already playing.

- **/skip**  
  Skip the current track and move on to the next one in the queue.

- **/queue**  
  Display the current queue along with the track that’s currently playing.

## Troubleshooting

- **Command Not Showing Up:**  
  If a command (like `/play`) isn’t available, verify that its cog is loaded correctly and that your slash commands have been synced with Discord.

- **Lavalink Connectivity:**  
  Ensure that your Lavalink server is running and that its configuration (host, port, password) matches what’s in your bot’s configuration.

- **Logging Issues:**  
  Check the log files (or console output) if you encounter errors. DAVE logs events in neat JSON format for easier troubleshooting.

## Contributing

Contributions are welcome! Fork the repository, make your improvements, and open a pull request. (Just be sure not to steal DAVE’s thunder!)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

For more details or to report a jam session mishap, check out the [DAVE Discord Bot GitHub Repository](https://github.com/kmosoti/dave-discord-bot).

Happy listening, and may your Discord server always be in tune!

---

Feel free to tweak further to better match your personality and style.