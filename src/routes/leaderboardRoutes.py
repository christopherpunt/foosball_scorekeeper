from flask import render_template, Blueprint
from leaderboardStats import LeaderboardStats
from helpers import *

leaderboard_blueprint = Blueprint('leaderboard', __name__)

leaderboardStats = LeaderboardStats()

@leaderboard_blueprint.route('/')
def getLeaderboardStats():
    stats = leaderboardStats.getAllStats()
    return render_template('leaderboard.html', all_stats=stats)

@leaderboard_blueprint.route('/player_stats')
def playerStats():
    stats = leaderboardStats.getPlayerStats()
    return render_template('leaderboard/player_stats.html', stats=stats)

@leaderboard_blueprint.route('/team_stats')
def teamStats():
    stats = leaderboardStats.getTeamStats()
    return render_template('leaderboard/team_stats.html', stats=stats)

@leaderboard_blueprint.route('/shortestGame_stats')
def shortestGame():
    stats = leaderboardStats.getShortestGames()
    return render_template('leaderboard/shortestGame_stats.html', stats=stats)

@leaderboard_blueprint.route('/gameHistory_stats')
def gameHistory():
    stats = leaderboardStats.getRecentGameHistory()
    return render_template('leaderboard/gameHistory_stats.html', stats=stats)

@leaderboard_blueprint.route('/bean_stats')
def teamBeans():
    stats = leaderboardStats.getTeamBeans()
    return render_template('leaderboard/bean_stats.html', stats=stats)

@leaderboard_blueprint.route('/hiddenStats')
def hiddenStats():
    stats = leaderboardStats.getHiddenStats()
    return render_template('leaderboard/hiddenStats.html', hiddenStats=stats)