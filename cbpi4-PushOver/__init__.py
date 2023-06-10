
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
import cbpi
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
import requests
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationType
from cbpi.controller.notification_controller import NotificationController
from cbpi.http_endpoints.http_notification import NotificationHttpEndpoints

logger = logging.getLogger(__name__)

pushover_token = None
pushover_user = None
pushover = None

class PushOver(CBPiExtension):

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self._task = asyncio.create_task(self.run())


    async def run(self):
        plugin = await self.cbpi.plugin.load_plugin_list("cbpi4-PushOver")
        self.version=plugin[0].get("Version","0.0.0")
        self.name=plugin[0].get("Name","cbpi4-PushOver")

        self.pushover_update = self.cbpi.config.get(self.name+"_update", None)

        logger.info('Starting PushOver Notifications background task')
        await self.pushover_settings()

        if pushover_token is None or pushover_token == "" or not pushover_token:
            logger.warning('Check Pushover API Token is set')
        elif pushover_user is None or pushover_user == "" or not pushover_user:
            logger.warning('Check Pushover User Key is set') 
        else:
            self.listener_ID = self.cbpi.notification.add_listener(self.messageEvent)
            logger.info("Pushover Lisetener ID: {}".format(self.listener_ID))
        pass

    async def pushover_settings(self):
        global pushover_token
        global pushover_user
        pushover_user = self.cbpi.config.get("pushover_user", None)
        pushover_token = self.cbpi.config.get("pushover_token", None)

        if pushover_token is None:
            logger.info("INIT Pushover Token")
            try:
                await self.cbpi.config.add("pushover_token", "", type=ConfigType.STRING, description="Pushover API Token",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.pushover_update == None or self.pushover_update != self.version:
                try:                
                    await self.cbpi.config.add("pushover_token", pushover_token, type=ConfigType.STRING, description="Pushover API Token",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if pushover_user is None:
            logger.info("INIT Pushover User Key")
            try:
                await self.cbpi.config.add("pushover_user", "", type=ConfigType.STRING, description="Pushover User Key",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.pushover_update == None or self.pushover_update != self.version:
                try:
                    await self.cbpi.config.add("pushover_user", pushover_user, type=ConfigType.STRING, description="Pushover User Key",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if self.pushover_update == None or self.pushover_update != self.version:
            try:
                await self.cbpi.config.add(self.name+"_update", self.version, type=ConfigType.STRING, description="Pushover Update Version",source="hidden")
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        

    async def messageEvent(self, cbpi, title, message, type, action):
            pushoverData = {}
            pushoverData["token"] = pushover_token
            pushoverData["user"] = pushover_user
            pushoverData["message"] = message 
            pushoverData["title"] = title
            requests.post("https://api.pushover.net/1/messages.json", data=pushoverData)

def setup(cbpi):
    cbpi.plugin.register("PushOver", PushOver)
    pass
