from middlewared.api.base import BaseModel, LongString

from .support import SupportNewTicket


__all__ = [
    'XnasSetProductionArgs', 'XnasSetProductionResult',
    'XnasIsProductionArgs', 'XnasIsProductionResult',
    'XnasAcceptEulaArgs', 'XnasAcceptEulaResult',
    'XnasIsEulaAcceptedArgs', 'XnasIsEulaAcceptedResult',
    'XnasGetEulaArgs', 'XnasGetEulaResult',
    'XnasIsIxHardwareArgs', 'XnasIsIxHardwareResult',
    'XnasGetChassisHardwareArgs', 'XnasGetChassisHardwareResult',
    'XnasManagedByTruecommandArgs', 'XnasManagedByTruecommandResult'
]


class XnasManagedByTruecommandArgs(BaseModel):
    pass


class XnasManagedByTruecommandResult(BaseModel):
    result: bool
    """Whether this X-NAS system is currently managed by TrueCommand."""


class XnasGetChassisHardwareArgs(BaseModel):
    pass


class XnasGetChassisHardwareResult(BaseModel):
    result: str
    """Hardware chassis model identifier for this X-NAS system."""


class XnasIsIxHardwareArgs(BaseModel):
    pass


class XnasIsIxHardwareResult(BaseModel):
    result: bool
    """Whether this system is running on Xloud hardware."""


class XnasGetEulaArgs(BaseModel):
    pass


class XnasGetEulaResult(BaseModel):
    result: LongString | None
    """Full text of the End User License Agreement. `null` if no EULA is required."""


class XnasIsEulaAcceptedArgs(BaseModel):
    pass


class XnasIsEulaAcceptedResult(BaseModel):
    result: bool
    """Whether the End User License Agreement has been formally accepted."""


class XnasAcceptEulaArgs(BaseModel):
    pass


class XnasAcceptEulaResult(BaseModel):
    result: None
    """Returns `null` on successful EULA acceptance."""


class XnasIsProductionArgs(BaseModel):
    pass


class XnasIsProductionResult(BaseModel):
    result: bool
    """Whether this X-NAS system is configured for production use."""


class XnasSetProductionArgs(BaseModel):
    production: bool
    """Whether to configure the system for production use."""
    attach_debug: bool = False
    """Whether to attach debug information when transitioning to production mode."""


class XnasSetProductionResult(BaseModel):
    result: SupportNewTicket | None
    """Support ticket details if system was newly marked as production. `null` otherwise."""
