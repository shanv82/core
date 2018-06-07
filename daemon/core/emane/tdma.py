"""
tdma.py: EMANE TDMA model bindings for CORE
"""

import os

from core import constants
from core import logger
from core.conf import Configuration
from core.emane import emanemanifest
from core.emane import emanemodel
from core.enumerations import ConfigDataTypes
from core.misc import utils


class EmaneTdmaModel(emanemodel.EmaneModel):
    # model name
    name = "emane_tdma"

    # mac configuration
    mac_library = "tdmaeventschedulerradiomodel"
    mac_xml = "/usr/share/emane/manifest/tdmaeventschedulerradiomodel.xml"
    mac_defaults = {
        "pcrcurveuri": "/usr/share/emane/xml/models/mac/tdmaeventscheduler/tdmabasemodelpcr.xml",
    }
    mac_config = emanemanifest.parse(mac_xml, mac_defaults)

    # add custom schedule options and ignore it when writing emane xml
    schedule_name = "schedule"
    default_schedule = os.path.join(constants.CORE_DATA_DIR, "examples", "tdma", "schedule.xml")
    mac_config.insert(
        0,
        Configuration(
            _id=schedule_name,
            _type=ConfigDataTypes.STRING,
            default=default_schedule,
            label="TDMA schedule file (core)"
        )
    )
    config_ignore = {schedule_name}

    def post_startup(self, emane_manager):
        """
        Logic to execute after the emane manager is finished with startup.

        :param core.emane.emanemanager.EmaneManager emane_manager: emane manager for the session
        :return: nothing
        """
        # get configured schedule
        config = emane_manager.get_configs(self.object_id, self.name)
        if not config:
            return
        schedule = config[self.schedule_name]

        event_device = emane_manager.event_device

        # initiate tdma schedule
        logger.info("setting up tdma schedule: schedule(%s) device(%s)", schedule, event_device)
        utils.check_cmd(["emaneevent-tdmaschedule", "-i", event_device, schedule])
