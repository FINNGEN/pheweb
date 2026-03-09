# -*- coding: utf-8 -*-
"""
HLA Summary data model classes.

DAO, DTO classes and interfaces.
"""
import typing
from dataclasses import dataclass


class HLADAO:
    """
    HLA DAO.

    Abstract class for HLA dao.
    """

@dataclass
class JeevesContext:
    """
    Jeeves context.

    Type interface for the jeeves context.
    """

    hla_dao: typing.Optional[HLADAO]
