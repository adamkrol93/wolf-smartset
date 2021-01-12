from abc import ABC, abstractmethod


class Device:

    def __init__(self, device_id: int, gateway: int, name: str):
        self.id = device_id
        self.gateway = gateway
        self.name = name

    def __str__(self) -> str:
        return 'Name: {}, Id: {}, Gateway {}'.format(self.name, self.id, self.gateway)


class Parameter(ABC):

    @property
    @abstractmethod
    def value_id(self):
        ...

    @value_id.setter
    @abstractmethod
    def value_id(self, value_id: int):
        ...

    @property
    @abstractmethod
    def name(self):
        ...

    @property
    @abstractmethod
    def parameter_id(self):
        ...

    @property
    @abstractmethod
    def parent(self):
        ...

    def __str__(self) -> str:
        return "%s -> %s[%d][%d] of %s" % (self.__class__.__name__, self.name, self.parameter_id, self.value_id, self.parent)


class SimpleParameter(Parameter):
    @property
    def name(self):
        return self._name

    @property
    def value_id(self):
        return self._value_id

    @value_id.setter
    def value_id(self, value_id: int):
        self._value_id = value_id

    @property
    def parent(self):
        return self._parent

    @property
    def parameter_id(self):
        return self._parameter_id

    def __init__(self, value_id: int, name: str, parent: str, parameter_id: int):
        self._value_id = value_id
        self._name = name
        self._parent = parent
        self._parameter_id = parameter_id


class UnitParameter(Parameter, ABC):
    @property
    @abstractmethod
    def unit(self):
        ...

    def __str__(self) -> str:
        return super().__str__() + " unit: [%s]" % self.unit


class Temperature(UnitParameter):
    @property
    def parameter_id(self):
        return self._parameter_id

    @property
    def unit(self):
        return "°C"

    @property
    def name(self):
        return self._name

    @property
    def value_id(self):
        return self._value_id

    @value_id.setter
    def value_id(self, value_id: int):
        self._value_id = value_id

    @property
    def parent(self):
        return self._parent

    def __init__(self, value_id: int, name: str, parent: str, parameter_id: int):
        self._value_id = value_id
        self._name = name
        self._parent = parent
        self._parameter_id = parameter_id


class Pressure(UnitParameter):
    @property
    def unit(self):
        return 'bar'

    @property
    def parameter_id(self):
        return self._parameter_id

    @property
    def name(self):
        return self._name

    @property
    def value_id(self):
        return self._value_id

    @value_id.setter
    def value_id(self, value_id: int):
        self._value_id = value_id

    @property
    def parent(self):
        return self._parent

    def __init__(self, value_id: int, name: str, parent: str, parameter_id: int):
        self._value_id = value_id
        self._name = name
        self._parent = parent
        self._parameter_id = parameter_id


class HoursParameter(UnitParameter):
    @property
    def unit(self):
        return 'H'

    @property
    def parameter_id(self):
        return self._parameter_id

    @property
    def name(self):
        return self._name

    @property
    def value_id(self):
        return self._value_id

    @value_id.setter
    def value_id(self, value_id: int):
        self._value_id = value_id

    @property
    def parent(self):
        return self._parent

    def __init__(self, value_id: int, name: str, parent: str, parameter_id: int):
        self._value_id = value_id
        self._name = name
        self._parent = parent
        self._parameter_id = parameter_id


class PercentageParameter(UnitParameter):

    @property
    def parameter_id(self):
        return self._parameter_id

    @property
    def unit(self):
        return "%"

    @property
    def name(self):
        return self._name

    @property
    def value_id(self):
        return self._value_id

    @value_id.setter
    def value_id(self, value_id: int):
        self._value_id = value_id

    @property
    def parent(self):
        return self._parent

    def __init__(self, value_id: int, name: str, parent: str, parameter_id: int):
        self._value_id = value_id
        self._name = name
        self._parent = parent
        self._parameter_id = parameter_id


class ListItem:
    name: str
    value: int

    def __init__(self, value: int, name: str):
        self.value = int(value)
        self.name = name

    def __str__(self) -> str:
        return '%d -> %s' % (self.value, self.name)


class ListItemParameter(Parameter):

    @property
    def parameter_id(self):
        return self._parameter_id

    @property
    def value_id(self):
        return self._value_id

    @value_id.setter
    def value_id(self, value_id: int):
        self._value_id = value_id

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    def __init__(self, value_id: int, name: str, parent: str, items: [ListItem], parameter_id: int):
        self._value_id = value_id
        self._name = name
        self._parent = parent
        self.items = items
        self._parameter_id = parameter_id

    def __str__(self) -> str:
        return super().__str__() + " items: " + ", ".join([item.__str__() for item in self.items])


class Value:

    def __init__(self, value_id: int, value: str, state: str):
        self.value_id = value_id
        self.value = value
        self.state = state

    def __str__(self) -> str:
        return 'Value id: {}, value: {}, state {}'.format(self.value_id, self.value, self.state)

