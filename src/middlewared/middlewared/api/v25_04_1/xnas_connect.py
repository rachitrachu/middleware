from pydantic import IPvAnyAddress

from middlewared.api.base import BaseModel, ForUpdateMetaclass, HttpsOnlyURL, NonEmptyString, single_argument_args


__all__ = [
    'XnasConnectEntry', 'XnasConnectGetRegistrationUriArgs', 'XnasConnectGetRegistrationUriResult',
    'XnasConnectUpdateArgs', 'XnasConnectUpdateResult', 'XnasConnectGenerateClaimTokenArgs',
    'XnasConnectGenerateClaimTokenResult', 'XnasConnectIpChoicesArgs', 'XnasConnectIpChoicesResult',
]


class XnasConnectEntry(BaseModel):
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
class XnasConnectUpdateArgs(BaseModel, metaclass=ForUpdateMetaclass):
    enabled: bool
    ips: list[IPvAnyAddress]
    account_service_base_url: HttpsOnlyURL
    leca_service_base_url: HttpsOnlyURL
    tnc_base_url: HttpsOnlyURL
    heartbeat_url: HttpsOnlyURL


class XnasConnectUpdateResult(BaseModel):
    result: XnasConnectEntry


class XnasConnectGetRegistrationUriArgs(BaseModel):
    pass


class XnasConnectGetRegistrationUriResult(BaseModel):
    result: NonEmptyString


class XnasConnectGenerateClaimTokenArgs(BaseModel):
    pass


class XnasConnectGenerateClaimTokenResult(BaseModel):
    result: NonEmptyString


class XnasConnectIpChoicesArgs(BaseModel):
    pass


class XnasConnectIpChoicesResult(BaseModel):
    result: dict[str, str]
