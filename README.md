# Pinbot

While Discord only allows 50 pinned message per channel, Pinbot allows unlimited pinned messages, aggregated across the entire server.

## Server Setup & Usage

To set up the bot, a user with the manage channels permission must run `/setup` and pass in the channel to be used for pins. This should be a channel made solely for the purpose of pinning messages.

When properly set up, any user with the manage messages permission can run the pin command (found in the "apps" menu when right-clicking a message) to pin a given message to the pins channel.

## Hosting

The file `.env` should be filled in with the below information and sourced before the bot is run:

* `DISCORD_TOKEN`: A string representing the Discord bot token
* `CHAN_DB_FILE`: The path/name of the JSON file to be used as a channel database
