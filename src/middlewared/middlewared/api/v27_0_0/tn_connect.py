from typing import Literal

from middlewared.api.base import (
    BaseModel, ForUpdateMetaclass, HttpsOnlyURL, NonEmptyString, single_argument_args,
)


__all__ = [
    'X-NASConnectEntry', 'X-NASConnectGetRegistrationUriArgs',
    'X-NASConnectGetRegistrationUriResult',
    'X-NASConnectUpdateArgs', 'X-NASConnectUpdateResult',
    'X-NASConnectGenerateClaimTokenArgs',
    'X-NASConnectGenerateClaimTokenResult',
    'X-NASConnectConfigChangedEvent',
    'X-NASConnectIpsWithHostnamesArgs', 'X-NASConnectIpsWithHostnamesResult',
]


class X-NASConnectEntry(BaseModel):
    id: int
    """Unique identifier for the X-NAS Connect configuration."""
    enabled: bool
    """Whether X-NAS Connect service is enabled."""
    registration_details: dict
    """Object containing registration information and credentials for X-NAS Connect."""
    status: NonEmptyString
    """Current operational status of the X-NAS Connect service."""
    status_reason: NonEmptyString
    """Detailed explanation of the current status, including any error conditions."""
    certificate: int | None
    """ID of the SSL certificate used for X-NAS Connect communications. `null` if using default."""
    account_service_base_url: HttpsOnlyURL
    """Base URL for the X-NAS Connect account service API."""
    leca_service_base_url: HttpsOnlyURL
    """Base URL for the Let's Encrypt Certificate Authority service used by X-NAS Connect."""
    tnc_base_url: HttpsOnlyURL
    """Base URL for the X-NAS Connect service."""
    heartbeat_url: HttpsOnlyURL
    """URL endpoint for sending heartbeat signals to maintain connection status."""
    tier: Literal['FOUNDATION', 'PLUS', 'BUSINESS'] | None
    """X-NAS Connect tier."""
    last_heartbeat_failure_datetime: str | None
    """Datetime of when the current heartbeat failure streak began. Null if heartbeat is not currently failing."""


@single_argument_args('tn_connect_update')
class X-NASConnectUpdateArgs(BaseModel, metaclass=ForUpdateMetaclass):
    enabled: bool
    """Whether to enable the X-NAS Connect service."""


class X-NASConnectUpdateResult(BaseModel):
    result: X-NASConnectEntry
    """The updated X-NAS Connect configuration."""


class X-NASConnectGetRegistrationUriArgs(BaseModel):
    pass


class X-NASConnectGetRegistrationUriResult(BaseModel):
    result: NonEmptyString
    """Registration URI for connecting this X-NAS system to X-NAS Connect."""


class X-NASConnectGenerateClaimTokenArgs(BaseModel):
    pass


class X-NASConnectGenerateClaimTokenResult(BaseModel):
    result: NonEmptyString
    """Generated claim token for authenticating with X-NAS Connect services."""


class X-NASConnectConfigChangedEvent(BaseModel):
    fields: X-NASConnectEntry
    """Event data."""


class X-NASConnectIpsWithHostnamesArgs(BaseModel):
    pass


class X-NASConnectIpsWithHostnamesResult(BaseModel):
    result: dict[str, str]
