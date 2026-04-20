from middlewared.api.base import BaseModel, LongString


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


class XnasGetChassisHardwareArgs(BaseModel):
    pass


class XnasGetChassisHardwareResult(BaseModel):
    result: str


class XnasIsIxHardwareArgs(BaseModel):
    pass


class XnasIsIxHardwareResult(BaseModel):
    result: bool


class XnasGetEulaArgs(BaseModel):
    pass


class XnasGetEulaResult(BaseModel):
    result: LongString | None


class XnasIsEulaAcceptedArgs(BaseModel):
    pass


class XnasIsEulaAcceptedResult(BaseModel):
    result: bool


class XnasAcceptEulaArgs(BaseModel):
    pass


class XnasAcceptEulaResult(BaseModel):
    result: None


class XnasIsProductionArgs(BaseModel):
    pass


class XnasIsProductionResult(BaseModel):
    result: bool


class XnasSetProductionArgs(BaseModel):
    production: bool
    attach_debug: bool = False


class XnasSetProductionResult(BaseModel):
    result: dict | None
