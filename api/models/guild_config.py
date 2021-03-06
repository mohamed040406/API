from postDB import Model, Column, types
from quart import exceptions
from typing import Optional, Union, Literal
from enum import Enum
from http import HTTPStatus


class VerificationTypes(Enum):
    DISCORD_INTEGRATED = "DISCORD_INTEGRATED"
    DISCORD_CODE = "DISCORD_CODE"
    DISCORD_INTEGRATED_CODE = "DISCORD_INTEGRATED_CODE"
    DISCORD_CAPTCHA = "DISCORD_CAPTCHA"
    DISCORD_INTEGRATED_CAPTCHA = "DISCORD_INTEGRATED_CAPTCHA"
    DISCORD_REACTION = "DISCORD_REACTION"
    DISCORD_INTEGRATED_REACTION = "DISCORD_INTEGRATED_REACTION"


class GuildConfig(Model):
    """
    Configuration for a guild, for storing information about what the guild configured.

    :param int guild_id:                The guild's id.
    :param bool xp_enabled:             Wheter XP for every message is enabled.
    :param float xp_multiplier:         XP multiplier for every message.
    :param bool eco_enabled:            Wheter economy commands are enabled.
    :param int muted_role_id:           The muted role's id.
    :param bool do_logging:             Whether to do logging.
    :param int log_channel_id:          The logging channel's id.
    :param bool do_verification:        Wheter to do verification.
    :param str verification_type:       The verification's type.
    :param int verification_channel_id: The verification channel's id.
    """

    guild_id = Column(
        types.ForeignKey("guilds", "id", sql_type=types.Integer(big=True)),
        primary_key=True,
    )
    xp_enabled = Column(types.Boolean)
    xp_multiplier = Column(types.Real)
    eco_enabled = Column(types.Boolean)
    muted_role_id = Column(types.Integer(big=True), nullable=True)
    do_logging = Column(types.Boolean)
    log_channel_id = Column(types.Integer(big=True), nullable=True)
    do_verification = Column(types.Boolean)
    verification_type = Column(types.String)  # enum
    verification_channel_id = Column(types.Integer(big=True), nullable=True)

    @classmethod
    async def fetch(cls, guild_id: Union[str, int]) -> Optional["GuildConfig"]:
        """Fetch a GuildConfig with the given guild ID."""
        query = "SELECT * FROM guildconfigs WHERE guild_id = $1"
        record = await cls.pool.fetchrow(query, int(guild_id))

        if record is None:
            return None

        return cls(**record)

    @classmethod
    async def fetch_or_404(cls, guild_id: Union[str, int]) -> Optional["GuildConfig"]:
        """
        Fetch a guild configuration with the given ID or send a 404 error.

        :param Union[str, int] guild_id: The guild's id.
        """

        if guild_config := await cls.fetch(guild_id):
            return guild_config

        http_status = HTTPStatus.NOT_FOUND
        http_status.description = (
            f"Guild with ID {guild_id} doesn't exist or doesn't have a configuration."
        )
        raise exceptions.NotFound(http_status)

    @classmethod
    async def create(
        cls,
        guild_id: Union[str, int],
        *,
        xp_enabled: Optional[bool] = False,
        xp_multiplier: Optional[float] = 1.0,
        eco_enabled: Optional[bool] = False,
        muted_role_id: Optional[Union[str, int]] = None,
        do_logging: Optional[bool] = False,
        log_channel_id: Optional[Union[str, int]] = None,
        do_verification: Optional[bool] = False,
        verification_type: Optional[
            Literal[
                "DISCORD_INTEGRATED",
                "DISCORD_CODE",
                "DISCORD_INTEGRATED_CODE",
                "DISCORD_CAPTCHA",
                "DISCORD_INTEGRATED_CAPTCHA",
                "DISCORD_REACTION",
                "DISCORD_INTEGRATED_REACTION",
            ]
        ] = "DISCORD_INTEGRATED",
        verification_channel_id: Optional[Union[str, int]] = None,
    ) -> Optional["GuildConfig"]:
        """
        Create a new GuildConfig instance.

        Returns the new instance if created.
        Returns `None` if a Unique Violation occurred.
        """

        if verification_type not in VerificationTypes.__members__:
            raise ValueError(
                f"verification_type must be one of {[m for m in VerificationTypes.__members__]}"
            )

        query = """
        INSERT INTO guildconfigs (guild_id, xp_enabled, xp_multiplier, eco_enabled, muted_role_id,
        do_logging, log_channel_id, do_verification, verification_type, verification_channel_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT DO NOTHING
        RETURNING *;
        """

        record = await cls.pool.fetchrow(
            query,
            int(guild_id),
            xp_enabled,
            xp_multiplier,
            eco_enabled,
            int(muted_role_id) if muted_role_id else None,
            do_logging,
            int(log_channel_id) if log_channel_id else None,
            do_verification,
            verification_type,
            int(verification_channel_id) if verification_channel_id else None,
        )

        if record is None:
            return None

        return cls(**record)

    async def update(self, **fields) -> Optional["GuildConfig"]:
        """Update the GuildConfig with the given arguments."""

        allowed_fields = (
            "xp_enabled",
            "xp_multiplier",
            "eco_enabled",
            "muted_role_id",
            "do_logging",
            "log_channel_id",
            "do_verification",
            "verification_type",
            "verification_channel_id",
        )
        fields = {
            name: fields.get(name, getattr(self, name)) for name in allowed_fields
        }

        for name in (
            "muted_role_id",
            "log_channel_id",
            "verification_channel_id",
        ):
            if fields[name] is not None:
                fields[name] = int(fields[name])

        if (
            "verification_type" in fields
            and fields["verification_type"] not in VerificationTypes.__members__
        ):
            raise ValueError(
                f"verification_type must be one of {[m for m in VerificationTypes.__members__]}"
            )

        query = """
        UPDATE guildconfigs
        SET
            xp_enabled = $2,
            xp_multiplier = $3,
            eco_enabled = $4,
            muted_role_id = $5,
            do_logging = $6,
            log_channel_id = $7,
            do_verification = $8,
            verification_type = $9,
            verification_channel_id = $10
        WHERE guild_id = $1
        RETURNING *;
        """
        record = await self.pool.fetchrow(query, int(self.guild_id), *fields.values())

        if record is None:
            return None

        for field, value in record.items():
            setattr(self, field, value)

        return self

    async def delete(self) -> Optional["GuildConfig"]:
        """Delete the GuildConfig."""

        query = """
        DELETE FROM guildconfigs
        WHERE guild_id = $1
        RETURNING *;
        """
        record = await self.pool.fetchrow(query, self.guild_id)

        if record is None:
            return None

        for field, value in record.items():
            setattr(self, field, value)

        return self
