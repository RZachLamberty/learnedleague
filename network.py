#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: network.py
Author: zlamberty
Created: 2017-11-14

Description:


Usage:
    <usage>

"""

import re

import lxml.html
import networkx as nx

from config import URLS


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #


LL_GRAPH = nx.DiGraph()


# ----------------------------- #
#   custom errors               #
# ----------------------------- #

class NoParentError(Exception):
    pass


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def build_ll_graph(username, password, loginurl=URLS['login']):
    """create a networkx graph of learned league ancestry"""
    session = login(username, password, loginurl)



def ancestors(leafname, username, password, profileurl=URLS['profile'],
              loginurl=URLS['login']):
    """parse ll for a user's list of ancestors

    args:
        leafname (str): a valid ll username used for the first leaf of the
            family tree
        username (str): a valid ll username used to log in to the ll service
        password (str): a valid ll password associated with `username`, used to
            log in
        profileurl (str): the url of learned league profile pages
        loginurl (str): the (post) endpoint of the learned league signin

    returns:
        tree (dict): edgelist where key: value represents child: parent

    raises:
        none

    """
    tree = {}
    childname = leafname
    session = login(username, password, loginurl=loginurl)
    while True:
        try:
            parent = get_parent(
                childname=childname,
                session=session,
                profileurl=profileurl
            )
            tree[childname] = parent
            childname = parent
        except NoParentError:
            break

    return tree


def get_parent(childname, session, profileurl=URLS['profile']):
    global LL_GRAPH
    try:
        parent = list(LL_GRAPH[childname].keys())[0]
    except (KeyError, IndexError):
        resp = session.get(profileurl, params=childname)
        root = lxml.html.fromstring(resp.text)
        try:
            aelem = root.find('.//a[@class="flag"]/img[@class="flag"]/..')
            parent = re.match(
                r'/profiles.php\?(\w+)', aelem.attrib['href']
            ).groups()[0]
            LL_GRAPH.add_edge(childname, parent)
        except AttributeError:
            raise NoParentError()

    return parent
