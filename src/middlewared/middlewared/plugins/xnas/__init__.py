from middlewared.api import api_method
from middlewared.api.current import (
    SupportNewTicket,
    XnasManagedByTruecommandArgs, XnasManagedByTruecommandResult,
    XnasGetChassisHardwareArgs, XnasGetChassisHardwareResult,
    XnasIsIxHardwareArgs, XnasIsIxHardwareResult,
    XnasGetEulaArgs, XnasGetEulaResult,
    XnasIsEulaAcceptedArgs, XnasIsEulaAcceptedResult,
    XnasAcceptEulaArgs, XnasAcceptEulaResult,
    XnasIsProductionArgs, XnasIsProductionResult,
    XnasSetProductionArgs, XnasSetProductionResult,
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


__all__ = ('XnasService',)


class XnasService(Service):

    class Config:
        cli_namespace = 'system.truenas'

    @api_method(
        XnasManagedByTruecommandArgs, XnasManagedByTruecommandResult,
        authentication_required=False, check_annotations=True,
    )
    async def managed_by_truecommand(self) -> bool:
        """Returns whether X-NAS is being managed by TrueCommand."""
        return await tn_managed_by_truecommand(self.context)

    @api_method(
        XnasGetChassisHardwareArgs, XnasGetChassisHardwareResult,
        cli_private=True, roles=['READONLY_ADMIN'], check_annotations=True,
    )
    def get_chassis_hardware(self) -> str:
        """Returns what type of hardware this is, detected from dmidecode."""
        return tn_get_chassis_hardware()

    @api_method(
        XnasIsIxHardwareArgs, XnasIsIxHardwareResult,
        roles=['READONLY_ADMIN'], check_annotations=True,
    )
    async def is_ix_hardware(self) -> bool:
        """Return a boolean value on whether this is hardware that Xloud sells."""
        return await tn_is_ix_hardware(self.context)

    @api_method(
        XnasGetEulaArgs, XnasGetEulaResult,
        cli_private=True, roles=['READONLY_ADMIN'], check_annotations=True,
    )
    def get_eula(self) -> str | None:
        """Returns the X-NAS End-User License Agreement (EULA)."""
        return tn_get_eula()

    @api_method(
        XnasIsEulaAcceptedArgs, XnasIsEulaAcceptedResult,
        cli_private=True, roles=['READONLY_ADMIN'], check_annotations=True,
    )
    def is_eula_accepted(self) -> bool:
        """Returns whether the EULA is accepted or not."""
        return tn_is_eula_accepted()

    @api_method(
        XnasAcceptEulaArgs, XnasAcceptEulaResult,
        roles=['FULL_ADMIN'], check_annotations=True,
    )
    def accept_eula(self) -> None:
        """Accept X-NAS EULA."""
        tn_accept_eula()

    @api_method(
        XnasIsProductionArgs, XnasIsProductionResult,
        roles=['READONLY_ADMIN'], check_annotations=True,
    )
    async def is_production(self) -> bool:
        """Returns if system is marked as production."""
        return await tn_is_production(self.context)

    @api_method(
        XnasSetProductionArgs, XnasSetProductionResult,
        roles=['FULL_ADMIN'], check_annotations=True,
    )
    @job()
    async def set_production(self, job: Job, production: bool, attach_debug: bool = False) -> SupportNewTicket | None:
        """Sets system production state and optionally sends initial debug."""
        return await tn_set_production(self.context, job, production, attach_debug)

    @private
    def unaccept_eula(self) -> None:
        tn_unaccept_eula()
