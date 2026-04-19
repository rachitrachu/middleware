from middlewared.api.base import BaseModel, LongString


__all__ = [
    'X-NASSetProductionArgs', 'X-NASSetProductionResult',
    'X-NASIsProductionArgs', 'X-NASIsProductionResult',
    'X-NASAcceptEulaArgs', 'X-NASAcceptEulaResult',
    'X-NASIsEulaAcceptedArgs', 'X-NASIsEulaAcceptedResult',
    'X-NASGetEulaArgs', 'X-NASGetEulaResult',
    'X-NASIsIxHardwareArgs', 'X-NASIsIxHardwareResult',
    'X-NASGetChassisHardwareArgs', 'X-NASGetChassisHardwareResult',
    'X-NASManagedByTruecommandArgs', 'X-NASManagedByTruecommandResult'
]


class X-NASManagedByTruecommandArgs(BaseModel):
    pass


class X-NASManagedByTruecommandResult(BaseModel):
    result: bool
    """Whether this X-NAS system is currently managed by TrueCommand."""


class X-NASGetChassisHardwareArgs(BaseModel):
    pass


class X-NASGetChassisHardwareResult(BaseModel):
    result: str
    """Hardware chassis model identifier for this X-NAS system."""


class X-NASIsIxHardwareArgs(BaseModel):
    pass


class X-NASIsIxHardwareResult(BaseModel):
    result: bool
    """Whether this system is running on Xloud hardware."""


class X-NASGetEulaArgs(BaseModel):
    pass


class X-NASGetEulaResult(BaseModel):
    result: LongString | None
    """Full text of the End User License Agreement. `null` if no EULA is required."""


class X-NASIsEulaAcceptedArgs(BaseModel):
    pass


class X-NASIsEulaAcceptedResult(BaseModel):
    result: bool
    """Whether the End User License Agreement has been formally accepted."""


class X-NASAcceptEulaArgs(BaseModel):
    pass


class X-NASAcceptEulaResult(BaseModel):
    result: None
    """Returns `null` on successful EULA acceptance."""


class X-NASIsProductionArgs(BaseModel):
    pass


class X-NASIsProductionResult(BaseModel):
    result: bool
    """Whether this X-NAS system is configured for production use."""


class X-NASSetProductionArgs(BaseModel):
    production: bool
    """Whether to configure the system for production use."""
    attach_debug: bool = False
    """Whether to attach debug information when transitioning to production mode."""


class X-NASSetProductionResult(BaseModel):
    result: dict | None
    """Result object containing production configuration details. `null` if transition failed."""
