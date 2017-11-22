#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: utils.py
Author: zlamberty
Created: 2017-11-21

Description:
    common utilities

Usage:
    <usage>

"""

import requests

from config import URLS


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def login(username, password, loginurl=URLS['login']):
    session = requests.Session()
    session.headers.update({'User-agent': "rzl"})
    session.post(
        url=loginurl,
        params={'mode': 'login'},
        data={
            'username': username, 'password': password,
            'login': 'Login'
        },
    )
    return session
