from typing import cast

from quant import (
    SlashCommand,
    InteractionContext,
    SlashOption,
    SlashOptionType,
    MessageFlags,
    Embed,
    EmbedAuthor
)
from quant.data.guild.messages.embeds import EmbedImage

from netnet.structure.common import Bot


async def hug_callback(context: InteractionContext) -> None:
    bot: Bot = cast(Bot, context.client)
    target_id = context.interaction.interaction_data.options[0].value
    guild = bot.cache.get_guild(context.interaction.guild_id)
    target = guild.get_member(int(target_id))

    if target.user.user_id == context.interaction.member.user.user_id:
        return await context.interaction.respond(
            'Вы не можете обнять себя',
            flags=MessageFlags.EPHEMERAL
        )
    if target.user.is_bot:
        return await context.interaction.respond(
            'Вы не можете обнять бота',
            flags=MessageFlags.EPHEMERAL
        )

    return await context.interaction.respond(
        embed=Embed(
            author=EmbedAuthor(
                name=f"{context.interaction.member.user.username} обнял {target.user.username}",
                icon_url=context.interaction.member.avatar
            ),
            image=EmbedImage(await bot.kawaii_api.get('hug'))
        ),
        flags=MessageFlags.NONE
    )


async def kiss_callback(context: InteractionContext) -> None:
    bot: Bot = cast(Bot, context.client)
    target_id = context.interaction.interaction_data.options[0].value
    guild = bot.cache.get_guild(context.interaction.guild_id)
    target = guild.get_member(int(target_id))

    if target.user.user_id == context.interaction.member.user.user_id:
        return await context.interaction.respond(
            'Вы не можете поцеловать себя',
            flags=MessageFlags.EPHEMERAL
        )
    if target.user.is_bot:
        return await context.interaction.respond(
            'Вы не можете поцеловал бота',
            flags=MessageFlags.EPHEMERAL
        )

    return await context.interaction.respond(
        embed=Embed(
            author=EmbedAuthor(
                name=f"{context.interaction.member.user.username} поцеловал {target.user.username}",
                icon_url=context.interaction.member.avatar
            ),
            image=EmbedImage(await bot.kawaii_api.get('kiss'))
        ),
        flags=MessageFlags.NONE
    )


async def setup(client: Bot):
    options = [
        SlashOption(
            name="target",
            description="Укажите пользователя или ID",
            option_type=SlashOptionType.USER,
            required=True
        )
    ]

    commands = {
        SlashCommand(
            name="hug",
            description="Обнять",
            options=options
        ): hug_callback,
        SlashCommand(
            name="kiss",
            description="Поцеловать",
            options=options
        ): kiss_callback
    }

    for command, callback in commands.items():
        command.set_callback(callback)
        await client.add_slash_command(command)
