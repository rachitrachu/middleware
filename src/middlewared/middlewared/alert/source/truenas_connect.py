from middlewared.alert.base import AlertClassConfig, AlertCategory, AlertLevel, OneShotAlertClass


class TNCHeartbeatConnectionFailureAlert(OneShotAlertClass):
    config = AlertClassConfig(
        category=AlertCategory.TRUENAS_CONNECT,
        level=AlertLevel.ERROR,
        title='Unable to connect to X-NAS Connect Heartbeat Service',
        text='Failed to connect to X-NAS Connect Heartbeat Service in the last 48 hours',
        deleted_automatically=False,
        keys=[],
    )


class TNCDisabledAutoUnconfiguredAlert(OneShotAlertClass):
    config = AlertClassConfig(
        category=AlertCategory.TRUENAS_CONNECT,
        level=AlertLevel.ERROR,
        title='X-NAS Connect Disabled - Service Unconfigured',
        text=(
            'X-NAS Connect has been disabled from X-NAS Connect.'
            ' The system has automatically unconfigured itself.'
        ),
        deleted_automatically=False,
        keys=[],
    )
