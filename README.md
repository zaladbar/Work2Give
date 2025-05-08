# Donate When Idle

**Donate When Idle** is an open-source, privacy-first desktop app that automatically donates money when you're idle or slacking off on your computer. It integrates with ActivityWatch to detect idleness and Beeminder to record donations, effectively turning your procrastination time into charity donations.

## How it Works

- **Idle Detection:** The app uses ActivityWatch to monitor your keyboard and mouse activity. If you're inactive for a specified number of minutes (`idleMinutes`), it considers you "idle".
- **"Slack" Detection:** Optionally, if you enable *cloudMode* and provide an `OPENAI_KEY`, the app will use an AI classifier (via OpenAI) to judge if your current activity is "slacking off" (e.g., browsing social media or streaming videos). A built-in list of distracting domains (social, streaming, shopping, etc.) provides a local heuristic if you don’t use the cloud classifier.
- **Beeminder Integration:** When you go idle for too long *or* the app judges that you're slacking, it sends a datapoint of value **1** to your Beeminder goal (specified by `BEEMINDER_GOAL`). This is effectively a $1 donation trigger (since derailing that goal will charge you money).
- **Donation Split:** By default, 90% of each $1 goes to your chosen charity and 10% goes to the app's developer (as a tip for maintenance and development). You can adjust this `devShare` percentage in the app settings (set `devShare` to 0 to give 100% to charity).

## Installation and Setup

1. **Install ActivityWatch:** If you haven't already, download and run [ActivityWatch](https://activitywatch.net). The app relies on ActivityWatch’s AFK (away-from-keyboard) detection. No additional configuration in ActivityWatch is needed (just make sure it's running in the background).
2. **Create a Beeminder Goal:** Log in to [Beeminder](https://beeminder.com) and create a new "Do More" goal (for example, called "donations"). This goal will track the number of $1 donations. Set your pledge and charity information as desired on Beeminder.
3. **Get Your Beeminder Auth Token:** On Beeminder, go to Account > Settings > API Authentication Token. Copy this token.
4. **Configure Environment Variables:** The app uses environment variables to know which goal to update:
   - `BEEMINDER_GOAL` – the slug of your Beeminder goal (e.g., `"donations"`).
   - `BEEMINDER_TOKEN` – your Beeminder API token (the long string from the previous step).
   - `OPENAI_KEY` – *optional*, only if using the cloud AI classifier; set this to your OpenAI API key.
   - `IDLE_MINUTES` – *optional*, the idle timeout in minutes (defaults to 5).
   - `CLOUD_MODE` – *optional*, set to `"1"` or `"true"` to enable cloud AI mode (defaults to false/off).
   - `DEV_SHARE` – *optional*, a decimal between 0 and 1 for the developer's share of each donation (defaults to 0.10 for 10%).
5. **Download the App:** You can download the latest release from the [GitHub Releases](https://github.com/yourusername/donate-when-idle/releases) page. Download the installer for your OS (Windows, macOS, or Linux).
6. **Run the App:** Launch the **Donate When Idle** application. On first run, it will open a settings window where you can adjust:
   - **Idle Minutes** – how many minutes of inactivity trigger a donation (e.g., 5 minutes).
   - **Cloud Mode** – toggle on/off the OpenAI-powered slack detector.
   - **Dev Share** – adjust what percentage of the donation goes to the developer (vs. charity).
   These settings are saved to disk (in your app data folder) and will persist across restarts.
7. **Keep it Running:** For the app to do its job, it needs to run in the background. You can minimize it; it will continue to monitor your idle time. If you quit the app, no donations will be triggered until you run it again.

## Usage

- Go about your work normally. If you step away from your computer for longer than the `idleMinutes` threshold, the **donate_when_idle.py** script (packaged with the app) will notice via ActivityWatch and send a `{ "value": 1 }` to your Beeminder goal.
- Likewise, if *cloudMode* is enabled and you've provided an OpenAI API key, the app will periodically check your current active window. If it detects a "slack" activity (for example, YouTube or Twitter), it will also send a donation datapoint. (If no OpenAI key is set, it uses a local list of domains to decide what counts as slack.)
- You will see the updates on your Beeminder goal page. Each datapoint represents $1 that you'll donate. If you derail (exceed your goal's limit), Beeminder will charge your payment method. You can then donate that amount to a charity of your choice. (Tip: You might set your Beeminder goal with a $0 pledge initially to test, then increase once you’re confident everything works.)

## Ledger Server (Optional)

Included in the `ledger_server/` directory is a simple FastAPI server that keeps a JSON log of all donation events, including how the donation is split. This is not required for the app to function, but it can be useful for transparency or personal records. To use it:
- Install Docker and Docker Compose.
- Run `docker-compose up -d` inside the `ledger_server` folder. This will build and start the server on port 8000, saving data to `ledger.json`.
- Every time a donation is triggered, the app will try to POST an entry to this server (localhost:8000/ledger). The entry contains `charity_share` and `dev_share` amounts (e.g., 0.9 and 0.1 for a $1 donation with 90/10 split) and a timestamp.
- You can GET the latest entry at `http://localhost:8000/ledger/latest` to see the most recent donation record.

This is optional – if the ledger server isn't running, the app will simply skip logging (and you might see a connection error in the console, which you can ignore).

## Building from Source

This project is built with [Tauri](https://tauri.app/) (Rust + WebView) and React. If you want to build it yourself:
- Install [Rust](https://www.rust-lang.org/tools/install) and [Node.js](https://nodejs.org/).
- Clone the repo and run `npm install` to install dependencies.
- Run `npm run tauri build`. This will compile the Rust backend and bundle the React frontend into a binary for your OS.
- The resulting installer or binary will be in `src-tauri/target/release/` (or the `src-tauri/target/release/bundle` directory for installers).

## Gumroad Starter Kit (Binaries)

For convenience, pre-compiled binaries are also available via Gumroad. You can find the **Donate When Idle Starter Kit** on Gumroad (see `marketing/gumroad_product.json` for details). Purchasing the starter kit will give you a zip file containing the installers for Windows (.exe), macOS (.dmg), and Linux (.AppImage), so you can get up and running quickly without building from source. *(Note: The code remains open source under MPL-2.0/MIT, and purchasing is optional – it just supports the developer and saves you the build process.)*

## Contributing and Feedback

Contributions are very welcome! If you have an idea for improvement or find a bug, please open an issue or pull request on GitHub. Some areas of interest:
- Tuning the "slack" domain list or improving the AI prompt for classification.
- Integrations with other services (perhaps sending data to other habit trackers or donation platforms).
- UI/UX enhancements for the settings window.

If you use **Donate When Idle** and it helps you (or you ended up donating a bit because of it!), I'd love to hear about it. Feel free to reach out or share your story.

Happy productive work, and happy donating! 🎉
