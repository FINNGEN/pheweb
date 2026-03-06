# -*- coding: utf-8 -*-
"""
HLA Summary data model classes.

DAO, DTO classes and interfaces.
"""
import abc
import typing
from dataclasses import dataclass
from typing import NamedTuple, List, Any


class HLASummaryDAO:
    """
    HLA Summary DAO.

    Abstract class for HLA summary dao.
    """

@dataclass
class JeevesContext:
    """
    Jeeves context.

    Type interface for the jeeves context.
    """

    hla_dao: typing.Optional[HLASummaryDAO]
