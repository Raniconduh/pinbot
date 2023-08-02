import os
import json
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions


import pinbot.config as config


intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)


class ChanDB:
    chans = {}

    def load():
        try:
            with open(config.CHAN_DB_FILE, "r") as f:
                ChanDB.chans = json.load(f)
        except FileNotFoundError:
            pass

    def save():
        with open(config.CHAN_DB_FILE, "w") as f:
            json.dump(ChanDB.chans, f)

    def add(guild: int, channel: int):
        guild = str(guild)
        channel = str(channel)
        ChanDB.chans[guild] = {"channel": channel}

    def get(guild: int):
        guild = str(guild)
        if guild not in ChanDB.chans: return None
        return int(ChanDB.chans[guild]["channel"])


async def get_webhook(channel: nextcord.TextChannel):
    webhooks = await channel.webhooks()
    for w in webhooks:
        if w.user == bot.user:
            return w
    return await channel.create_webhook(name="pinbot", avatar=bot.user.display_avatar)


@bot.slash_command()
@has_permissions(manage_channels=True)
async def setup(interaction: nextcord.Interaction,
                channel: nextcord.TextChannel = nextcord.SlashOption(
                    description="The channel to use for pins")):
    """Set up a channel to use for server pins"""

    try:
        await get_webhook(channel)
    except nextcord.Forbidden:
        await interaction.send("I do not have permission to create a webhook")
        return

    ChanDB.add(interaction.guild_id, channel.id)
    ChanDB.save()

    await interaction.send(f"Using <#{channel.id}> as pins channel")


@bot.message_command()
@has_permissions(manage_messages=True)
async def pin(interaction: nextcord.Interaction,
              message: nextcord.Message):
    """Pin a message to the pins channel"""

    p = interaction.channel.permissions_for(interaction.user)
    if nextcord.Permissions.manage_messages not in p:
        await interaction.send("You do not have permission to pin messages", ephemeral=True)
        return

    channel = ChanDB.get(interaction.guild_id)
    if channel is not None:
        try:
            channel = await bot.fetch_channel(channel)
        except nextcord.NotFound:
            channel = None

    if channel is None:
        await interaction.send("Please run `/setup` to set up a pins channel for this server")
        return

    try:
        wh = await get_webhook(channel)
    except nextcord.Forbidden:
        await interaction.send("I do not have permission to create a webhook")
        return

    a = message.author

    content = {}
    if message.content: content["content"] = message.content

    embeds = message.embeds[:9]
    e = nextcord.Embed(title="Jump to message")
    e.url = message.jump_url
    embeds.append(e)

    await wh.send(**content, username=a.name,
                  avatar_url=a.display_avatar.url, embeds=embeds,
                  allowed_mentions=nextcord.AllowedMentions().none(),
                  files=[await a.to_file() for a in message.attachments])

    await interaction.send(f"Message @ {message.jump_url} pinned")


@bot.event
async def on_ready():
    ChanDB.load()

    print("Ready")


bot.run(os.getenv("DISCORD_TOKEN"))
