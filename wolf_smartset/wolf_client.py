import datetime
from typing import Union

import httpx
import logging
from httpx import Headers

from wolf_smartset.constants import BASE_URL, ID, GATEWAY_ID, NAME, SYSTEM_ID, MENU_ITEMS, TAB_VIEWS, BUNDLE_ID, \
    BUNDLE, VALUE_ID_LIST, GUI_ID_CHANGED, SESSION_ID, VALUE_ID, VALUE, STATE, VALUES, PARAMETER_ID, UNIT, \
    CELSIUS_TEMPERATURE, BAR, PERCENTAGE, LIST_ITEMS, DISPLAY_TEXT, PARAMETER_DESCRIPTORS, TAB_NAME, HOUR, \
    LAST_ACCESS, ERROR_CODE, ERROR_TYPE
from wolf_smartset.create_session import create_session
from wolf_smartset.helpers import bearer_header
from wolf_smartset.models import Temperature, Parameter, SimpleParameter, Device, Pressure, ListItemParameter, \
    PercentageParameter, Value, ListItem, HoursParameter
from wolf_smartset.token_auth import Tokens, TokenAuth

_LOGGER = logging.getLogger(__name__)


class WolfClient:
    session_id: int or None
    tokens: Tokens or None
    last_access: datetime or None
    last_failed: bool

    def __init__(self, username: str, password: str):
        self.tokens = None
        self.token_auth = TokenAuth(username, password)
        self.session_id = None
        self.last_access = None
        self.last_failed = False

    async def __request(self, method: str, path: str, **kwargs) -> Union[dict, list]:
        await self.__authorize()

        headers = kwargs.get('headers')

        if headers is None:
            headers = bearer_header(self.tokens.access_token)
        else:
            headers = {**bearer_header(self.tokens.access_token), **dict(headers)}

        resp = await self.__execute(headers, kwargs, method, path)
        if resp.status_code == 401 or resp.status_code == 500:
            _LOGGER.debug('Retrying')
            await self.__authorize()
            headers = {**bearer_header(self.tokens.access_token), **dict(headers)}
            try:
                execution = await self.__execute(headers, kwargs, method, path)
                return execution.json()
            except FetchFailed as e:
                self.last_failed = True
                raise e
        else:
            self.last_failed = False
            return resp.json()

    @staticmethod
    async def __execute(headers, kwargs, method, path):
        async with httpx.AsyncClient() as client:
            return await client.request(method, f"{BASE_URL}/{path}", **dict(kwargs, headers=Headers(headers)))

    async def __authorize(self):
        if self.last_failed is True or self.tokens is None or datetime.datetime.now() > self.tokens.expire_date:
            await self.__authorize_and_session()

    async def __authorize_and_session(self):
        async with httpx.AsyncClient() as session:
            self.tokens = await self.token_auth.token(session)
            self.session_id = await create_session(session, self.tokens.access_token)

    # api/portal/GetSystemList
    async def fetch_system_list(self) -> [Device]:
        system_list = await self.__request('get', 'api/portal/GetSystemList')
        _LOGGER.debug('Fetched systems: %s', system_list)
        return [Device(system[ID], system[GATEWAY_ID], system[NAME]) for system in system_list]

    # api/portal/GetGuiDescriptionForGateway?GatewayId={gateway_id}&SystemId={system_id}
    async def fetch_parameters(self, gateway_id, system_id) -> [Parameter]:
        payload = {GATEWAY_ID: gateway_id, SYSTEM_ID: system_id}
        desc = await self.__request('get', 'api/portal/GetGuiDescriptionForGateway', params=payload)
        _LOGGER.debug('Fetched parameters: %s', desc)
        tab_views = desc[MENU_ITEMS][0][TAB_VIEWS]
        result = [WolfClient._map_view(view) for view in tab_views]

        result.reverse()
        distinct_ids = []
        flattened = []
        for sublist in result:
            distinct_names = []
            for val in sublist:
                if val.value_id not in distinct_ids and val.name not in distinct_names:
                    distinct_ids.append(val.value_id)
                    distinct_names.append(val.name)
                    flattened.append(val)
        return flattened

    # api/portal/GetParameterValues
    async def fetch_value(self, gateway_id, system_id, parameters: [Parameter]):
        data = {
            BUNDLE_ID: 1000,
            BUNDLE: False,
            VALUE_ID_LIST: [param.value_id for param in parameters],
            GATEWAY_ID: gateway_id,
            SYSTEM_ID: system_id,
            GUI_ID_CHANGED: True,
            SESSION_ID: self.session_id,
            LAST_ACCESS: self.last_access
        }
        res = await self.__request('post', 'api/portal/GetParameterValues', json=data,
                                   headers={"Content-Type": "application/json"})

        _LOGGER.debug('Fetched values: %s', res)

        if ERROR_CODE in res or ERROR_TYPE in res:
            raise FetchFailed(res)

        self.last_access = res[LAST_ACCESS]
        return [Value(v[VALUE_ID], v[VALUE], v[STATE]) for v in res[VALUES] if VALUE in v]

    @staticmethod
    def _map_parameter(parameter: dict, parent: str) -> Parameter:
        value_id = parameter[VALUE_ID]
        name = parameter[NAME]
        parameter_id = parameter[PARAMETER_ID]
        if UNIT in parameter:
            unit = parameter[UNIT]
            if unit == CELSIUS_TEMPERATURE:
                return Temperature(value_id, name, parent, parameter_id)
            elif unit == BAR:
                return Pressure(value_id, name, parent, parameter_id)
            elif unit == PERCENTAGE:
                return PercentageParameter(value_id, name, parent, parameter_id)
            elif unit == HOUR:
                return HoursParameter(value_id, name, parent, parameter_id)
        elif LIST_ITEMS in parameter:
            items = [ListItem(list_item[VALUE], list_item[DISPLAY_TEXT]) for list_item in parameter[LIST_ITEMS]]
            return ListItemParameter(value_id, name, parent, items, parameter_id)
        return SimpleParameter(value_id, name, parent, parameter_id)

    @staticmethod
    def _map_view(view: dict):
        if 'SVGHeatingSchemaConfigDevices' in view:
            units = dict([(unit['valueId'], unit['unit']) for unit
                          in view['SVGHeatingSchemaConfigDevices'][0]['parameters'] if 'unit' in unit])

            new_params = []
            for param in view[PARAMETER_DESCRIPTORS]:
                if param[VALUE_ID] in units:
                    param[UNIT] = units[param[VALUE_ID]]
                new_params.append(WolfClient._map_parameter(param, view[TAB_NAME]))
            return new_params
        else:
            return [WolfClient._map_parameter(p, view[TAB_NAME]) for p in view[PARAMETER_DESCRIPTORS]]


class FetchFailed(Exception):
    """Server returned 500 code with message while executing query"""
    pass
