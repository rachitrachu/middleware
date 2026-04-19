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


class X-NASGetChassisHardwareArgs(BaseModel):
    pass


class X-NASGetChassisHardwareResult(BaseModel):
    result: str


class X-NASIsIxHardwareArgs(BaseModel):
    pass


class X-NASIsIxHardwareResult(BaseModel):
    result: bool


class X-NASGetEulaArgs(BaseModel):
    pass


class X-NASGetEulaResult(BaseModel):
    result: LongString | None


class X-NASIsEulaAcceptedArgs(BaseModel):
    pass


class X-NASIsEulaAcceptedResult(BaseModel):
    result: bool


class X-NASAcceptEulaArgs(BaseModel):
    pass


class X-NASAcceptEulaResult(BaseModel):
    result: None


class X-NASIsProductionArgs(BaseModel):
    pass


class X-NASIsProductionResult(BaseModel):
    result: bool


class X-NASSetProductionArgs(BaseModel):
    production: bool
    attach_debug: bool = False


class X-NASSetProductionResult(BaseModel):
    result: dict | None
