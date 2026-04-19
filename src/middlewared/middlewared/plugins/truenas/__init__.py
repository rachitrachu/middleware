from middlewared.api import api_method
from middlewared.api.current import (
    SupportNewTicket,
    X-NASManagedByTruecommandArgs, X-NASManagedByTruecommandResult,
    X-NASGetChassisHardwareArgs, X-NASGetChassisHardwareResult,
    X-NASIsIxHardwareArgs, X-NASIsIxHardwareResult,
    X-NASGetEulaArgs, X-NASGetEulaResult,
    X-NASIsEulaAcceptedArgs, X-NASIsEulaAcceptedResult,
    X-NASAcceptEulaArgs, X-NASAcceptEulaResult,
    X-NASIsProductionArgs, X-NASIsProductionResult,
    X-NASSetProductionArgs, X-NASSetProductionResult,
)
from middlewared.job import Job
from middlewared.service import job, private, Service

from .tn import (
    managed_by_truecommand as tn_managed_by_truecommand,
    get_chassis_hardware as tn_get_chassis_hardware,
    is_ix_hardware as tn_is_ix_hardware,
    get_eula as tn_get_eula,
    is_eula_accepted as tn_is_eula_accepted,
    accept_eula as tn_accept_eula,
    unaccept_eula as tn_unaccept_eula,
    is_production as tn_is_production,
    set_production as tn_set_production,
)


__all__ = ('X-NASService',)


class X-NASService(Service):

    class Config:
        cli_namespace = 'system.truenas'

    @api_method(
        X-NASManagedByTruecommandArgs, X-NASManagedByTruecommandResult,
        authentication_required=False, check_annotations=True,
    )
    async def managed_by_truecommand(self) -> bool:
        """Returns whether X-NAS is being managed by TrueCommand."""
        return await tn_managed_by_truecommand(self.context)

    @api_method(
        X-NASGetChassisHardwareArgs, X-NASGetChassisHardwareResult,
        cli_private=True, roles=['READONLY_ADMIN'], check_annotations=True,
    )
    def get_chassis_hardware(self) -> str:
        """Returns what type of hardware this is, detected from dmidecode."""
        return tn_get_chassis_hardware()

    @api_method(
        X-NASIsIxHardwareArgs, X-NASIsIxHardwareResult,
        roles=['READONLY_ADMIN'], check_annotations=True,
    )
    async def is_ix_hardware(self) -> bool:
        """Return a boolean value on whether this is hardware that Xloud sells."""
        return await tn_is_ix_hardware(self.context)

    @api_method(
        X-NASGetEulaArgs, X-NASGetEulaResult,
        cli_private=True, roles=['READONLY_ADMIN'], check_annotations=True,
    )
    def get_eula(self) -> str | None:
        """Returns the X-NAS End-User License Agreement (EULA)."""
        return tn_get_eula()

    @api_method(
        X-NASIsEulaAcceptedArgs, X-NASIsEulaAcceptedResult,
        cli_private=True, roles=['READONLY_ADMIN'], check_annotations=True,
    )
    def is_eula_accepted(self) -> bool:
        """Returns whether the EULA is accepted or not."""
        return tn_is_eula_accepted()

    @api_method(
        X-NASAcceptEulaArgs, X-NASAcceptEulaResult,
        roles=['FULL_ADMIN'], check_annotations=True,
    )
    def accept_eula(self) -> None:
        """Accept X-NAS EULA."""
        tn_accept_eula()

    @api_method(
        X-NASIsProductionArgs, X-NASIsProductionResult,
        roles=['READONLY_ADMIN'], check_annotations=True,
    )
    async def is_production(self) -> bool:
        """Returns if system is marked as production."""
        return await tn_is_production(self.context)

    @api_method(
        X-NASSetProductionArgs, X-NASSetProductionResult,
        roles=['FULL_ADMIN'], check_annotations=True,
    )
    @job()
    async def set_production(self, job: Job, production: bool, attach_debug: bool = False) -> SupportNewTicket | None:
        """Sets system production state and optionally sends initial debug."""
        return await tn_set_production(self.context, job, production, attach_debug)

    @private
    def unaccept_eula(self) -> None:
        tn_unaccept_eula()
