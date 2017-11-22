#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: config.py
Author: zlamberty
Created: 2017-11-21

Description:
    simple configuration details

Usage:
    <usage>

"""

URLS = {'base': 'https://www.learnedleague.com'}
URLS['profile'] = '{}/profiles.php'.format(URLS['base'])
URLS['login'] = '{}/ucp.php'.format(URLS['base'])
URLS['matchups'] = '{}/match.php?{{season:}}&{{day:}}&{{rundle:}}'.format(URLS['base'])
URLS['standings'] = '{}/standings.php?{{season:}}&{{rundle:}}'.format(URLS['base'])
