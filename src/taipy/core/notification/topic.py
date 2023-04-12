# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import Optional, Tuple

from ..exceptions.exceptions import InvalidEntityId, InvalidEntityType, InvalidEventAttributeName, InvalidEventOperation
from .event import (
    _ENTITY_TYPE_PREFIXES,
    _NO_ATTRIBUTE_NAME_OPERATIONS,
    _UNSUBMITTABLE_ENTITY_TYPES,
    EventEntityType,
    EventOperation,
)


class Topic:
    def __init__(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        operation: Optional[str] = None,
        attribute_name: Optional[str] = None,
    ):

        self.entity_type, self.entity_id = self.__preprocess_entity_type_and_entity_id(entity_type, entity_id)
        self.operation = self.__preprocess_operation(operation, self.entity_type)
        self.attribute_name = self.__preprocess_attribute_name(attribute_name, self.operation)

    @classmethod
    def __preprocess_entity_type_and_entity_id(
        cls, entity_type: Optional[str], entity_id: Optional[str]
    ) -> Tuple[EventEntityType, Optional[str]]:
        try:
            # TODO: add test for this
            converted_entity_type = entity_type if not entity_type else EventEntityType.__members__[entity_type.upper()]
        except KeyError:
            raise InvalidEntityType

        if converted_entity_type and entity_id:
            tmp_entity_type = cls.__get_entity_type_from_id(entity_id)
            if tmp_entity_type != converted_entity_type:
                raise InvalidEntityType
            converted_entity_type = tmp_entity_type
        else:
            if entity_id:
                converted_entity_type = cls.__get_entity_type_from_id(entity_id)
        return converted_entity_type, entity_id  # type: ignore

    @classmethod
    def __get_entity_type_from_id(cls, entity_id: str):
        for entity_prefix, event_entity_type in _ENTITY_TYPE_PREFIXES.items():
            if entity_id.startswith(entity_prefix):
                return event_entity_type
        raise InvalidEntityId

    @classmethod
    def __preprocess_attribute_name(
        cls, attribute_name: Optional[str] = None, operation: Optional[EventOperation] = None
    ) -> Optional[str]:
        # TODO: check if attribute_name exists in entity?
        if (not operation or operation in _NO_ATTRIBUTE_NAME_OPERATIONS) and attribute_name is not None:
            raise InvalidEventAttributeName
        return attribute_name

    @classmethod
    def __preprocess_operation(
        cls, operation: Optional[str] = None, entity_type: Optional[EventEntityType] = None
    ) -> Optional[EventOperation]:
        # TODO: what if operation or entity_type or both is None?
        try:
            converted_operation = operation if not operation else EventOperation.__members__[operation.upper()]
        except KeyError:
            raise InvalidEventOperation
        if (
            entity_type
            and entity_type in _UNSUBMITTABLE_ENTITY_TYPES
            and converted_operation == EventOperation.SUBMISSION
        ):
            raise InvalidEventOperation
        return converted_operation  # type: ignore

    def __hash__(self):
        return hash((self.entity_type, self.entity_id, self.operation, self.attribute_name))

    def __eq__(self, __value) -> bool:
        if (
            self.entity_type == __value.entity_type
            and self.entity_id == __value.entity_id
            and self.operation == __value.operation
            and self.attribute_name == __value.attribute_name
        ):
            return True
        return False
