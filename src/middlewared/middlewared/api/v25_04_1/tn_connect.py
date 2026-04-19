from pydantic import IPvAnyAddress

from middlewared.api.base import BaseModel, ForUpdateMetaclass, HttpsOnlyURL, NonEmptyString, single_argument_args


__all__ = [
    'X-NASConnectEntry', 'X-NASConnectGetRegistrationUriArgs', 'X-NASConnectGetRegistrationUriResult',
    'X-NASConnectUpdateArgs', 'X-NASConnectUpdateResult', 'X-NASConnectGenerateClaimTokenArgs',
    'X-NASConnectGenerateClaimTokenResult', 'X-NASConnectIpChoicesArgs', 'X-NASConnectIpChoicesResult',
]


class X-NASConnectEntry(BaseModel):
    id: int
    enabled: bool
    registration_details: dict
    ips: list[NonEmptyString]
    status: NonEmptyString
    status_reason: NonEmptyString
    certificate: int | None
    account_service_base_url: HttpsOnlyURL
    leca_service_base_url: HttpsOnlyURL
    tnc_base_url: HttpsOnlyURL
    heartbeat_url: HttpsOnlyURL


@single_argument_args('tn_connect_update')
class X-NASConnectUpdateArgs(BaseModel, metaclass=ForUpdateMetaclass):
    enabled: bool
    ips: list[IPvAnyAddress]
    account_service_base_url: HttpsOnlyURL
    leca_service_base_url: HttpsOnlyURL
    tnc_base_url: HttpsOnlyURL
    heartbeat_url: HttpsOnlyURL


class X-NASConnectUpdateResult(BaseModel):
    result: X-NASConnectEntry


class X-NASConnectGetRegistrationUriArgs(BaseModel):
    pass


class X-NASConnectGetRegistrationUriResult(BaseModel):
    result: NonEmptyString


class X-NASConnectGenerateClaimTokenArgs(BaseModel):
    pass


class X-NASConnectGenerateClaimTokenResult(BaseModel):
    result: NonEmptyString


class X-NASConnectIpChoicesArgs(BaseModel):
    pass


class X-NASConnectIpChoicesResult(BaseModel):
    result: dict[str, str]
