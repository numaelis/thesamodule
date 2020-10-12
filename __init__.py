#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: numaelis
"""

from trytond.pool import Pool

from .thesamodule import *


def register():
    Pool.register(
        ThesaModules,
        ThesaModulesView,
        ThesaUsersFolder,
        ThesaGroupUsers,
        ViewResultThesaStart,
        module="thesamodule", type_="model")
    Pool.register(
        ViewResultThesa,
        module='thesamodule', type_='wizard')
