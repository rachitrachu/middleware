# Copyright (c) - iXsystems Inc. dba TrueNAS
#
# Licensed under the terms of the TrueNAS Enterprise License Agreement
# See the file LICENSE.IX for complete terms and conditions

from collections import defaultdict
from datetime import date, timedelta
import textwrap
from typing import Any

from middlewared.alert.base import (
    AlertClass, AlertClassConfig, AlertCategory, AlertLevel, Alert, NonDataclassAlertClass, ThreadedAlertSource,
)
from middlewared.alert.schedule import IntervalSchedule
from middlewared.utils import ProductType
from middlewared.utils.license import LICENSE_ADDHW_MAPPING


class LicenseAlert(NonDataclassAlertClass[str], AlertClass):
    config = AlertClassConfig(
        category=AlertCategory.SYSTEM,
        level=AlertLevel.CRITICAL,
        title="X-NAS License Issue",
        text="%s",
        products=(ProductType.ENTERPRISE,),
    )


class LicenseIsExpiringAlert(NonDataclassAlertClass[str], AlertClass):
    config = AlertClassConfig(
        category=AlertCategory.SYSTEM,
        level=AlertLevel.WARNING,
        title="X-NAS License Is Expiring",
        text="%s",
        products=(ProductType.ENTERPRISE,),
    )


class LicenseHasExpiredAlert(NonDataclassAlertClass[str], AlertClass):
    config = AlertClassConfig(
        category=AlertCategory.SYSTEM,
        level=AlertLevel.CRITICAL,
        title="X-NAS License Has Expired",
        text="%s",
        products=(ProductType.ENTERPRISE,),
    )


class LicenseStatusAlertSource(ThreadedAlertSource):
    products = (ProductType.ENTERPRISE,)
    run_on_backup_node = False
    schedule = IntervalSchedule(timedelta(hours=24))

    def check_sync(self) -> list[Alert[Any]] | Alert[Any]:
        alerts: list[Alert[Any]] = []

        local_license = self.middleware.call_sync('system.license')
        if local_license is None:
            return Alert(LicenseAlert("Your X-NAS has no license, contact support."))

        # Community X-NAS builds ship a self-issued "XNAS" license. Their
        # purpose is to enable the enterprise-gated code paths, not to
        # enforce hardware binding or vendor-support contracts, so skip the
        # hardware-match / support-status checks below in that case.
        xnas_community = local_license['model'] == 'XNAS'

        # check if this node's system serial matches the serial in the license
        # (licenselib stores a 16-char serial; DMI reports up to 36 chars, so
        # allow either side to be a prefix of the other for the match)
        local_serial = self.middleware.call_sync('system.dmidecode_info')['system-serial-number']
        license_serials = [s for s in (local_license['system_serial'], local_license['system_serial_ha']) if s]
        serial_match = any(
            local_serial == s or local_serial.startswith(s) or s.startswith(local_serial)
            for s in license_serials
        )
        if not xnas_community and not serial_match:
            alerts.append(Alert(LicenseAlert('System serial does not match license.')))

        standby_license = standby_serial = None
        try:
            if local_license['system_serial_ha']:
                standby_license = self.middleware.call_sync('failover.call_remote', 'system.license')
                standby_serial = self.middleware.call_sync(
                    'failover.call_remote', 'system.dmidecode_info')['system-serial-number']
        except Exception:
            pass

        if standby_license and standby_serial is not None:
            # check if the remote node's system serial matches the serial in the license
            if standby_serial not in (standby_license['system_serial'], standby_license['system_serial_ha']):
                alerts.append(Alert(LicenseAlert('System serial of standby node does not match license.')))

        model = self.middleware.call_sync('truenas.get_chassis_hardware').removeprefix('TRUENAS-').split('-')[0]
        if xnas_community:
            # Community build -- no vendor hardware enforcement.
            pass
        elif model == 'UNKNOWN':
            alerts.append(Alert(LicenseAlert('X-NAS is running on unsupported hardware.')))
        elif model != local_license['model']:
            alerts.append(Alert(
                LicenseAlert(
                    f'Your license was issued for model {local_license["model"]!r} '
                    f'but the system was detected as model {model!r}'
                )
            ))

        enc_nums: defaultdict[str, int] = defaultdict(lambda: 0)
        for enc in filter(lambda x: not x['controller'], self.middleware.call_sync('enclosure2.query')):
            enc_nums[enc['model']] += 1

        if local_license['addhw']:
            for quantity, code in local_license['addhw']:
                if code not in LICENSE_ADDHW_MAPPING:
                    self.middleware.logger.warning('Unknown additional hardware code %d', code)
                    continue

                name = LICENSE_ADDHW_MAPPING[code]
                if name == 'ES60':
                    continue

                if enc_nums[name] != quantity:
                    alerts.append(Alert(
                        LicenseAlert(
                            'License expects %(license)s units of %(name)s Expansion shelf but found %(found)s.' % {
                                'license': quantity,
                                'name': name,
                                'found': enc_nums[name]
                            }
                        )
                    ))
        elif enc_nums:
            alerts.append(Alert(
                LicenseAlert(
                    'Unlicensed Expansion shelf detected. This system is not licensed for additional expansion shelves.'
                )
            ))

        for days in [0, 14, 30, 90, 180]:
            if local_license['contract_end'] <= date.today() + timedelta(days=days):
                serial_numbers = ", ".join(list(filter(None, [local_license['system_serial'],
                                                              local_license['system_serial_ha']])))
                contract_start = local_license['contract_start'].strftime("%B %-d, %Y")
                contract_expiration = local_license['contract_end'].strftime("%B %-d, %Y")
                contract_type = local_license['contract_type']  # Display as stored, usually upper case.
                customer_name = local_license['customer_name']

                alert_klass: type[LicenseHasExpiredAlert] | type[LicenseIsExpiringAlert]
                if days == 0:
                    alert_klass = LicenseHasExpiredAlert
                    alert_text = textwrap.dedent("""\
                        SUPPORT CONTRACT EXPIRATION: Please reactivate to continue receiving technical
                        support. Contact Xloud at info@xloud.tech.
                    """)
                    subject = "Your X-NAS support contract has expired"
                    opening = textwrap.dedent("""\
                        Your support contract has ended. A support contract may be renewed after contract
                        expiration. Please contact Xloud at info@xloud.tech.
                    """)
                    encouraging = textwrap.dedent("""\
                        Please renew the support contract for your X-NAS product as soon as possible to
                        maintain support services. Contact Xloud at info@xloud.tech.
                    """)
                else:
                    alert_klass = LicenseIsExpiringAlert
                    alert_text = textwrap.dedent(f"""\
                        RENEW YOUR SUPPORT CONTRACT: The support contract for this product will expire
                        on {contract_expiration}. To avoid service interruptions, contact Xloud at
                        info@xloud.tech.
                    """)
                    days_left = (local_license['contract_end'] - date.today()).days
                    subject = f"Your X-NAS support contract will expire in {days_left} days"
                    if days == 14:
                        opening = textwrap.dedent(f"""\
                            The support contracts for the following X-NAS products are expiring in 14 days:
                            {serial_numbers}
                            This is a reminder regarding the impending expiration of your X-NAS
                            {contract_type} support contract.
                        """)
                        encouraging = textwrap.dedent("""\
                            We encourage you to urgently contact Xloud at info@xloud.tech to renew your
                            support contracts.
                        """)
                    else:
                        opening = textwrap.dedent(f"""\
                            Your X-NAS {contract_type} support contract will expire in {days_left} days.
                            Please consider renewing your support contract now. Contact Xloud at
                            info@xloud.tech.
                        """)
                        encouraging = textwrap.dedent("""\
                            Please contact Xloud at info@xloud.tech to renew your contract before expiration.
                        """)

                alerts.append(Alert(
                    alert_klass(alert_text),
                    mail={
                        "cc": ["info@xloud.tech"],
                        "subject": subject,
                        "text": textwrap.dedent("""\
                            Hello, {customer_name}

                            {opening}

                            Support Level: {contract_type}
                            Product: {chassis_hardware}
                            Serial Numbers: {serial_numbers}
                            Support Contract Start Date: {contract_start}
                            Support Contract Expiration Date: {contract_expiration}

                            {encouraging}

                            Your X-NAS system will remain accessible after the support contract expires.
                            However, after expiration it will no longer be eligible for support from Xloud.
                            A support contract may be renewed after it has expired and there may be additional
                            costs associated with contract reactivation and lapsed-contract fees.

                            Sincerely,

                            Xloud
                            Web: https://xloud.tech/
                            Email: info@xloud.tech
                        """).format(**{
                            "customer_name": customer_name,
                            "opening": opening,
                            "contract_type": contract_type,
                            "chassis_hardware": model,
                            "serial_numbers": serial_numbers,
                            "contract_start": contract_start,
                            "contract_expiration": contract_expiration,
                            "encouraging": encouraging,
                        })
                    },
                ))
                break

        return alerts
