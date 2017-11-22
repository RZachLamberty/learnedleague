#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: learnedleague.py
Author: zlamberty
Created: 2017-11-20

Description:


Usage:
    <usage>

"""

import re

import lxml.html
import numpy as np
import pandas as pd

from config import URLS


import sys
sys.path.insert(0, '/home/zlamberty/code/elo')
import elo

# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

class LLError(Exception):
    pass


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def get_teams(session, season, rundle, teamurl=URLS['standings']):
    """return all the team names in a given rundle in a given season"""
    resp = session.get(teamurl.format(season=season, rundle=rundle))
    root = lxml.html.fromstring(resp.text)
    return [_.attrib['title'] for _ in root.xpath('.//table//td/a/img')]


def elo_init(teams, season, rundle):
    """initialize a dataframe with elo scores"""
    dfelo = pd.DataFrame({'team': teams})
    dfelo.loc[:, 'season'] = season
    dfelo.loc[:, 'day'] = 1
    dfelo.loc[:, 'rundle'] = rundle
    dfelo.loc[:, 'elo'] = 1500
    return dfelo


def ll_elo(session, season, rundle, matchupurl=URLS['matchups'],
           teamurl=URLS['standings']):
    """calculate the learned league team elo rankings"""
    # build an elo ranking
    dfelo = elo_init(
        teams=get_teams(session, season, rundle, teamurl),
        season=season,
        rundle=rundle
    )

    def update_elo(record):
        mov = elo.margin_of_victory_multiplier(
            deltaPts=record.score_delta,
            rW=record.elo,
            rL=record.elo_opp
        )
        escore = elo.expected_score(
            r0=record.elo,
            r1=record.elo_opp,
        )
        return elo.update_score(
            r0=record.elo,
            rScore=record.wlt,
            eScore=escore,
            movFactor=mov
        )

    daynum = 1
    while True:
        try:
            print(daynum)
            df = pd.DataFrame(
                matchday_results(session, season, daynum, rundle, matchupurl)
            )
            df.loc[:, 'score_delta'] = df.score - df.opp_score
            df.loc[:, 'wlt'] = np.where(
                df.score > df.opp_score,
                1,
                np.where(df.score < df.opp_score, 0, 0.5)
            )

            # join in elo scores and opponent's elo scores
            thiselo = dfelo[dfelo.day == daynum]
            dfwelo = df.merge(thiselo, on=['team', 'season', 'day', 'rundle'])
            dfwelo = dfwelo.merge(
                thiselo,
                left_on=['opp', 'season', 'day', 'rundle'],
                right_on=['team', 'season', 'day', 'rundle'],
                suffixes=('', '_opp')
            )

            # override the meaningful columns so we can append
            dfwelo.loc[:, 'day'] = daynum + 1
            dfwelo.loc[:, 'elo'] = dfwelo.apply(func=update_elo, axis=1)

            # append the new elo rankings to the bottom of dfelo
            dfelo = dfelo.append(dfwelo[['team', 'season', 'day', 'rundle', 'elo']])

            daynum += 1
        except LLError:
            break

    return dfelo.sort_values(by=['team', 'day'])


def matchday_results(session, season, day, rundle, matchupurl=URLS['matchups']):
    """pull the results of a single day of competition"""
    url = matchupurl.format(season=season, day=day, rundle=rundle)
    resp = session.get(url)
    root = lxml.html.fromstring(resp.text)

    resulttable = root.find('.//table[@class="tblResults"]')

    try:
        matches = resulttable.xpath('.//tr')
    except AttributeError:
        raise LLError("no matches yet for day {}".format(day))

    params = {'season': season, 'day': day, 'rundle': rundle}

    for match in matches:
        score = match.xpath('td/nobr/a/text()')[0].encode('ascii', 'ignore')
        m = re.match(
            b'(?P<ptsa>\d)\((?P<qsa>[\dF])\)(?P<ptsb>\d)\((?P<qsb>[\dF])\)',
            score
        ).groupdict()

        m = {k: (-1 if v == b'F' else int(v)) for (k, v) in m.items()}

        teama, teamb = match.xpath('td/nobr/text()')

        ma = {}
        ma.update(params)
        ma.update({
            'team': teama,
            'score': m['ptsa'],
            'qs_answered': m['qsa'],
            'opp': teamb,
            'opp_score': m['ptsb'],
            'opp_qs_answered': m['qsb'],
        })
        yield ma

        ma = {}
        ma.update(params)
        ma.update({
            'team': teamb,
            'score': m['ptsb'],
            'qs_answered': m['qsb'],
            'opp': teama,
            'opp_score': m['ptsa'],
            'opp_qs_answered': m['qsa'],
        })
        yield ma


# ----------------------------- #
#   Command line                #
# ----------------------------- #

def parse_args():
    """ Take a log file from the commmand line """
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", "--xample", help="An Example", action='store_true')

    args = parser.parse_args()

    logger.debug("arguments set to {}".format(vars(args)))

    return args


if __name__ == '__main__':

    args = parse_args()

    main()
