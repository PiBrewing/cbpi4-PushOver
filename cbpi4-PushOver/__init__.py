
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
        logger.info('Starting PushOver Notifications background task')
        await self.pushoverUser()
        await self.pushoverToken()
        if pushover_token is None or pushover_token == "" or not pushover_token:
            logger.warning('Check Pushover API Token is set')
        elif pushover_user is None or pushover_user == "" or not pushover_user:
            logger.warning('Check Pushover User Key is set') 
        else:
            self.listener_ID = self.cbpi.notification.add_listener(self.messageEvent)
            logger.info("Pushover Lisetener ID: {}".format(self.listener_ID))
        pass

    async def pushoverToken(self):
        global pushover_token
        pushover_token = self.cbpi.config.get("pushover_token", None)
        if pushover_token is None:
            logger.info("INIT Pushover Token")
            try:
                await self.cbpi.config.add("pushover_token", "", ConfigType.STRING, "Pushover API Token")
            except:
                logger.warning('Unable to update config')
                
    async def pushoverUser(self):
        global pushover_user
        pushover_user = self.cbpi.config.get("pushover_user", None)
        if pushover_user is None:
            logger.info("INIT Pushover User Key")
            try:
                await self.cbpi.config.add("pushover_user", "", ConfigType.STRING, "Pushover User Key")
            except:
                logger.warning('Unable to update config')

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
