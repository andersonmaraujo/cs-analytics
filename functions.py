import pandas as pd
import numpy as np
import json
import os

def prepare_dataframe(refactored_match_data):
  df_rounds = pd.DataFrame()
  df_match = []
  for round in refactored_match_data['gameRounds']:
    for player in round['players']:
      df_match.append([
          refactored_match_data['matchID'],
          refactored_match_data['mapName'],
          player['playerName'],
          round['roundNum'],
          player['teamName'],
          player['steamID'],
          player['side'],
          player['kills'],
          player['wasKilled'],
          player['ace'],
          player['ninja'],
          player['headshots'],
          player['onetaps'],
          player['clutch'],
          player['noscopes'],
          player['lookingaway'],
          player['trade_kills'],
          player['activity']
      ])
      df_rounds = pd.concat([pd.DataFrame(df_match, columns=['matchID', 'mapName', 'playerName', 'roundNum', 'teamName', 'playerSteamID', 'side', 'kills', 'wasKilled', 'wasAce', 'wasNinja', 'headshots', 'onetaps','clutch','lookingaway','trade_kills', 'noscopes','activity'])], ignore_index=True)

  return df_rounds

def refactor_match_data(match_data):
  match_data_refactored = {}
  match_data_refactored = {
        'matchID': match_data['matchID'],
        'mapName': match_data['mapName'], 
        'winnerTeam': match_data['gameRounds'][-1]['winningTeam'],
        'winnerScore': match_data['gameRounds'][-1]['endTScore'] if match_data['gameRounds'][-1]['winningTeam'] == match_data['gameRounds'][-1]['tTeam'] else match_data['gameRounds'][-1]['endCTScore'],
        'loserScore': match_data['gameRounds'][-1]['endCTScore'] if match_data['gameRounds'][-1]['winningTeam'] == match_data['gameRounds'][-1]['tTeam'] else match_data['gameRounds'][-1]['endTScore'],
        'gameRounds': get_rounds_info(match_data)['gameRounds']
        }

  return match_data_refactored

def get_rounds_info(match_data):
  rounds_data = { 'gameRounds':[] }

  for round in match_data["gameRounds"]:
    if round['isWarmup']:
      continue
    new_round = {
        'winningTeam': round['winningTeam'],
        'winningSide': round['winningSide'],
        'roundNum': round['roundNum'],
        'roundEndReason': round['roundEndReason'],
        'endTScore': round['endTScore'],
        'endCTScore': round['endCTScore'],
        'teams': get_teams_info(round)['teams'],
        'players': get_players_info(round)['players']
    }
    rounds_data['gameRounds'].append(new_round)
  return rounds_data

def get_teams_info(round_data):
  teams_data = { 'teams': [] }
  
  

  return teams_data

def get_players_info(round_data):
  players_data = { 'players': [] }

  for side in ['ctSide', 'tSide']:
    new_player = {}
    for player in round_data[side]['players']:
      #TO-DO
      # was looking away
      new_player = {
          'teamName': round_data[side]['teamName'],
          'side': 'CT' if side == 'ctSide' else 'T',
          'playerName': player['playerName'],
          'steamID': player['steamID'],
          'kills': get_kills_count_byplayer('CT' if side == 'ctSide' else 'T', player['steamID'], round_data),
          'wasKilled': get_killed_info_byplayer('CT' if side == 'ctSide' else 'T', player['steamID'], round_data),
          'ace': get_aces_count('CT' if side == 'ctSide' else 'T', player['steamID'], round_data),
          'ninja': get_ninja_defuse_byplayer('CT' if side == 'ctSide' else 'T', player['steamID'], round_data),
          'cashSpent': get_cash_spent_by_player(player['steamID'], round_data),
          'headshots': get_kills_byheadshot_count_byplayer('CT' if side == 'ctSide' else 'T', player['steamID'], round_data),
          'onetaps': get_one_tap_count_by_player(player['steamID'], round_data),
          'clutch': get_clutch_by_player('CT' if side == 'ctSide' else 'T', player['steamID'], round_data),
          'noscopes': get_noscope_kills_by_player('CT' if side == 'ctSide' else 'T', player['steamID'], round_data),
          'lookingaway': get_kills_looking_away_by_player('CT' if side == 'ctSide' else 'T', player['steamID'], round_data),
          'trade_kills': get_traded_kills_by_player('CT' if side == 'ctSide' else 'T', player['steamID'], round_data),
          'activity': get_player_round_activity('CT' if side == 'ctSide' else 'T', player['steamID'], round_data)
      }
      players_data['players'].append(new_player)
  return players_data

def get_player_round_activity(side, player_steam_id, round):
  player_activity = 0
  for kill in round['kills']:
    if (kill['playerTradedSteamID'] == player_steam_id or
        (kill['attackerSteamID'] == player_steam_id and kill['victimSide'] != side) or
        (kill['assisterSteamID'] == player_steam_id and kill['victimSide'] != side)):
      player_activity = 1

  for player in round['frames'][-1]['ct' if side == 'CT' else 't']['players']:
    if(player['steamID'] == player_steam_id and player['isAlive'] == True):
      player_activity = 1
  return player_activity

def get_traded_kills_by_player(side, player_steam_id, round):
  traded_kills = 0
  for kill in round['kills']:
      if kill['attackerSteamID'] == player_steam_id and kill['victimSide'] != side:
        if kill['isTrade']:
          traded_kills = traded_kills+1
  return traded_kills

def get_kills_looking_away_by_player(side, player_steam_id, round):
  looking_away = 0
  for kill in round['kills']:
    if kill['attackerSteamID'] == player_steam_id and kill['victimSide'] != side:
      if was_victim_looking_away(kill):
        looking_away = looking_away + 1
  return looking_away


def calculate_unit_vector(point1, point2):
    """Calculate unit vector from point1 to point2."""
    vector = np.array(point2) - np.array(point1)
    return vector / np.linalg.norm(vector)

def spherical_to_cartesian(theta, phi):
    """
    Convert spherical coordinates to cartesian.
    Theta and Phi should be in degrees.
    """
    theta = np.radians(theta)
    phi = np.radians(phi)
    x = np.sin(phi) * np.cos(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(phi)
    return [x, y, z]

def angle_between_vectors(v1, v2):
    """Calculate the angle in degrees between vectors 'v1' and 'v2'."""
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    return np.degrees(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))

def was_victim_looking_away(data):
    """Determine if the victim was looking away from the attacker."""
    # Extract attacker and victim positions
    attacker_position = [data['attackerX'], data['attackerY'], data['attackerZ']]
    victim_position = [data['victimX'], data['victimY'], data['victimZ']]

    # Calculate unit vector from attacker to victim
    attacker_to_victim_vector = calculate_unit_vector(attacker_position, victim_position)

    # Convert victim's viewing angles to a direction vector
    victim_view_vector = spherical_to_cartesian(data['victimViewX'], data['victimViewY'])

    # Calculate the angle between the two vectors
    angle = angle_between_vectors(attacker_to_victim_vector, victim_view_vector)

    # If the angle is greater than 90 degrees, the victim was looking away
    return angle > 90

def get_noscope_kills_by_player(side, player_steam_id, round):
  noscope_kills = 0
  for kill in round['kills']:
    if kill['attackerSteamID'] == player_steam_id and kill['victimSide'] != side:
      if kill['noScope']:
        noscope_kills = noscope_kills +1
  return noscope_kills

def get_clutch_by_player(side, player_steam_id, round):
  isClutch = 0
  enemies_alive = 5
  friends_alive = 5
  if round['winningSide'] == side:
    if (side == 'CT' and not round['roundEndReason'] in ['TargetBombed', 'TerroristsWins']) or side == 'T':
      if (side == 'T' and not round['roundEndReason'] in ['BombDefused', 'CTWins']) or side == 'CT':
        last_kill = round['kills'][-1]

        for frame in round['frames']:
          if frame['tick'] == last_kill['tick']:
            enemies_alive = frame['t' if side == 'CT' else 'ct']['alivePlayers']
            friends_alive = 0 if frame['ct' if side == 'CT' else 't']['alivePlayers'] > 1 else 1
  
  if enemies_alive > friends_alive and friends_alive > 0:
    isClutch = 1
  return isClutch

def get_one_tap_count_by_player(player_steam_id, round):
  onetap = 0
  for frame in round['damages']:
      if frame['attackerSteamID'] == player_steam_id:
        if frame['hpDamage'] > 99 and frame['hitGroup'] == 'Head':
          for kills in round['kills']:
            if kills['attackerSteamID'] == player_steam_id:
              if kills['tick'] == frame['tick'] and kills['victimSteamID'] == frame['victimSteamID']:
                    onetap = onetap+1
          
  return onetap


def get_cash_spent_by_player(player_steam_id, round):
  for side in ['t','ct']:
    for player in round['frames'][-1][side]['players']:
      if player['steamID'] == player_steam_id:
        return player['cashSpendThisRound']
  return 0

def get_aces_count(side, player_steam_id, round):
  kills = 0
  for kill in round['kills']:
    if player_steam_id == kill['attackerSteamID']:
      if side != kill['attackerSide']:
        kills = kills+1
  if kills > 4:
    return 1
  else:
    return 0

def get_kills_byheadshot_count_byplayer(side, player_steam_id, round):
  kills = 0
  for kill in round['kills']:
    if player_steam_id == kill['attackerSteamID']:
      if side == kill['attackerSide']:
        if kill['isHeadshot']:
            kills = kills+1
  return kills

def get_kills_count_byplayer(side, player_steam_id, round):
  kills = 0
  for kill in round['kills']:
    if player_steam_id == kill['attackerSteamID']:
      if side == kill['attackerSide']:
        kills = kills+1
  return kills

def get_killed_info_byplayer(side, player_steam_id, round):
  wasKilled = 0
  for kill in round['kills']:
    if player_steam_id == kill['victimSteamID']:
        wasKilled = 1
  return wasKilled

def get_ninja_defuse_byplayer(side, player_steam_id, round):
  ninja = 0
  for bombEvent in round['bombEvents']:
    if bombEvent['bombAction'] == 'defuse':
      if bombEvent['playerSteamID'] == player_steam_id:
        #find if exists enemies alive
        enemy_alive_players = 0
        team_alive_players = 0
        for frame in round['frames']:
          if frame['tick'] > bombEvent['tick']:
            for player in frame['ct' if side == 'CT' else 't']['players']:
              if player['isAlive']:
                team_alive_players = +1
            for player in frame['ct' if side == 'T' else 't']['players']:
              if player['isAlive']:
                enemy_alive_players = +1
        ninja = 1 if team_alive_players < enemy_alive_players else 0

  return ninja