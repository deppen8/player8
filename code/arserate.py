import sqlite3
import pandas as pd
import numpy as np
import requests
import seaborn as sns
from bs4 import BeautifulSoup
from datetime import datetime

##############################################################################    
    
def arseblog_scrape(url, db):
    '''Extract information from an Arseblog player ratings webpage and write it to a database.
    
    Parameters
    ----------
    url : str
        Full URL of an Arseblog player ratings webpage
    db : str
        Path to the database file
    
    Notes
    -----
    1. The function prints some information to help the user. First, if the match is already recorded
    in the database, the function prints: "This match already exists in the database. No data entered."
    Otherwise, the following information is presented for inspection:
    - The players it has found
    - Basic match information
    - Whether any Chu-Young Parks have been found (see Note #2)
    - A success message when the function exits
    
    2. The function has what I call a 'Check-Young Park' feature. Arseblog occasionally uses Chu-Young Park as 
    a placeholder for new players that have not yet been entered into the internal Arseblog database. 
    Chu-Young Park did not make any appearances for Arsenal during the period under analysis (matches after 
    1 Jan 2014) and left the club during summer 2014, so any Chu-Young Park entries in the database need to be 
    edited manually. 
    
    (The use of Chu-Young Park is a bit of an inside joke for Arsenal fans. He arrived at the club on a
    frantic transfer deadline day with Arsenal in dire need of a striker. Park had a strong reputation as the 
    captain of the South Korean national team and an up-and-coming talent in the French league. At Arsenal, 
    however, he was barely ever used before being released on a free transfer in 2014.)
    
    Example
    -------
    >>> arseblog_scrape('http://news.arseblog.com/2016/09/nottingham-forest-0-4-arsenal-player-ratings/', 'ratings.db')
    26: Emiliano Martinez
    30: Chu-Young Park
    5: Gabriel .
    16: Rob Holding
    3: Kieran Gibbs
    29: Granit Xhaka
    35: Mohamed Elneny
    54: Jeff Reine-Adelaide
    32: Chuba Akpom
    15: Alex Oxlade-Chamberlain
    9: Lucas Perez
    35: Gedion Zelalem
    30: Chu-Young Park
    37: Krystian Bielik

    URL: http://news.arseblog.com/2016/09/nottingham-forest-0-4-arsenal-player-ratings/
    Date: September 20, 2016

    Season: 2016-17
    Competition: EFL Cup

    Arsenal 4 - 0 Nottingham Forest
    Match ratings successfully entered
    '''
    try:
        # open .db file, create cursor
        conn = sqlite3.connect(db)
        c = conn.cursor()

        # check to see if the match already exists in the db
        c.execute('SELECT * FROM games WHERE url = ?', (url,))
        gamecheck = c.fetchone()
        if gamecheck is None:
            # scrape page
            response = requests.get(url)
            html = response.content
            soup = BeautifulSoup(html, "lxml")

            # find competition
            competition = 'NULL'
            competition_lst = ['Premier League', 'FA Cup', 'Champions League', 
                               'Capital One Cup', 'Community Shield', 'Carabao Cup',
                               'Europa League', 'EFL Cup']
            tags = soup.findAll(attrs={'class':'entry-category'})
            for tag in tags:
                if str(tag.get_text()) in competition_lst:
                    competition = str(tag.get_text())

            # find home/away, goals, and date
            score = soup.find(attrs={'class':'entry-title'}).get_text()
            split_score = score[:-16].split('-')
            home = split_score[0][0:-2].rstrip()
            home_score = split_score[0][-1]
            away = split_score[1][2:].rstrip()
            away_score = split_score[1][0]

            home_away = 'home'
            opponent = away
            arsegoals = home_score
            oppgoals = away_score

            if home not in ['arsenal', 'Arsenal']:
                home_away = 'away'
                opponent = home
                arsegoals = away_score
                oppgoals = home_score
            
            wld = None
            if arsegoals > oppgoals:
                wld = 'win'
            elif arsegoals < oppgoals:
                wld = 'loss'
            else:
                wld='draw'
            
            game_date = soup.find(attrs={'class':'entry-date updated td-module-date'}).get_text()

            season = ''
            start13_14 = datetime(2013, 8, 1)
            end13_14 = datetime(2014, 6, 1)
            start14_15 = datetime(2014, 8, 1)
            end14_15 = datetime(2015, 6, 1)
            start15_16 = datetime(2015, 8, 1)
            end15_16 = datetime(2016, 6, 1)
            start16_17 = datetime(2016, 8, 1)
            end16_17 = datetime(2017, 6, 1)
            start17_18 = datetime(2017, 8, 1)
            end17_18 = datetime(2018, 6, 1)

            date_object = datetime.strptime(game_date, '%B %d, %Y')

            if start13_14 < date_object < end13_14:
                season = '2013-14'
            elif start14_15 < date_object < end14_15:
                season = '2014-15'
            elif start15_16 < date_object < end15_16:
                season = '2015-16'
            elif start16_17 < date_object < end16_17:
                season = '2016-17'
            elif start17_18 < date_object < end17_18:
                season = '2017-18'
            else:
                season = 'NULL'
            
            # insert the match info into the database
            c.execute('INSERT OR IGNORE INTO games (season, competition, home_away, arsegoals, opponent, oppgoals, date, url, wld) VALUES (?,?,?,?,?,?,?,?,?)', (season, competition, home_away, arsegoals, opponent, oppgoals, game_date, url, wld))

            # compile some text about the match for the output
            outputText = ''
            outputText += 'URL: ' + str(url) + '\n'
            outputText += 'Date: ' + str(game_date) + '\n\n'
            outputText += 'Season: ' + str(season) + '\n'
            outputText += 'Competition: ' + str(competition) + '\n\n'
            outputText += 'Arsenal ' + str(arsegoals) + ' - ' + str(oppgoals) + ' ' + str(opponent) + '\n\n'

            # get gameID that was automatically created in the db
            c.execute('SELECT gameID FROM games WHERE date=?', (game_date,))
            game_temp = c.fetchone()
            gameID = int(game_temp[0])

            # loop through each player entry on page
            for entry in soup.find_all(attrs={'class': 'player-list'}):
                # find name
                name_num = entry.find(attrs={'class':'intro'}).get_text()
                print(name_num)
                name = name_num.split(' ', 1)[1]
                if name == 'Chu-Young Park': # Check-Young Park
                    outputText += '\nYOU HAVE AT LEAST ONE CHU-YOUNG PARK IN THE DATASET. MANUAL EDITS NEEDED!!!\n\n\n'
                c.execute('SELECT * FROM players WHERE name = ?', (name,))
                namecheck = c.fetchone()
                if namecheck is None:
                    c.execute('INSERT INTO players (name) VALUES (?)', (name,))
                    conn.commit()
                    outputText += name + ' added to database\n'

                # find playerID automatically created in the db
                c.execute('SELECT playerID FROM players WHERE name=?', (name,))
                player_temp = c.fetchone()
                playerID = int(player_temp[0])

                # find both ratings (returns a list)
                ratings = entry.find_all(attrs={'class':'num'})

                # for numerical ratings, covert to float
                # for non-numerical ratings, use 'NA'
                try:
                    blogsrating = float(ratings[0].get_text())
                except:
                    blogsrating = 'NA'

                try:
                    userrating = float(ratings[1].get_text())
                except:
                    userrating = 'NA'

    #             # insert data into the two ratings tables of the db
    #             c.execute('SELECT * FROM arseblog_ratings WHERE playerID = ? AND gameID = ?', (playerID, gameID))
    #             arsecheck = c.fetchone()
    #             if arsecheck is None:
    #                 c.execute('INSERT INTO arseblog_ratings (playerID, gameID, arseblograting) VALUES (?,?,?)', (playerID, gameID, blogsrating))

    #             c.execute('SELECT userratingID FROM user_ratings WHERE playerID = ? AND gameID = ?', (playerID, gameID))
    #             usercheck = c.fetchone()
    #             if usercheck is None:
    #                 c.execute('INSERT INTO user_ratings (playerID, gameID, userrating) VALUES (?,?,?)', (playerID, gameID, userrating))
                # insert data into the two ratings tables of the db
                c.execute('INSERT INTO arseblog_ratings (playerID, gameID, arseblograting) VALUES (?,?,?)', (playerID, gameID, blogsrating))

                c.execute('INSERT INTO user_ratings (playerID, gameID, userrating) VALUES (?,?,?)', (playerID, gameID, userrating))

            conn.commit()
            conn.close()

            print(outputText)
            print("Match ratings successfully entered")
        else:
            print("This match already exists in the database. No data entered.")
            conn.close()
    except:
        print("something went wrong!")
        conn.close()

##############################################################################

def import_db(db_path):
    """Connect to database and load tables as pandas DataFrames
    
    Parameters
    ----------
    db_path : str
        Filepath to .db file
    
    Returns
    -------
    dict
        Keys are string versions of SQLite table names. Values are pd.DataFrame objects
    """
    # create DB connection
    # '/Users/jacobdeppen/Dropbox/Player_ratings/db_files/ratings.db'
    conn = sqlite3.connect(db_path)

    # query for games table to DF
    games = pd.read_sql_query('select * from games;', conn, parse_dates=['date'])
    games['gameID'] = games['gameID'].astype('category')
        
    # add win/draw/loss column, 'result'
    conditions = [(games['arsegoals']>games['oppgoals']),
                  (games['arsegoals']==games['oppgoals']),
                  (games['arsegoals']<games['oppgoals'])]
    results = ['win', 'draw', 'loss']                                         
    games['result'] = np.select(conditions, results)

    # query for players table to DF
    players = pd.read_sql_query('select * from players;', conn, parse_dates=['birthdate'])
    players['playerID'] = players['playerID'].astype('category')

    # query for ab_ratings table to DF
    ab_rate = pd.read_sql_query('select * from arseblog_ratings;', conn)

    # query for userratings table to DF
    user_rate = pd.read_sql_query('select * from user_ratings;', conn)

    conn.close()
    
    return {'games':games, 'players':players, 'arseblog_ratings':ab_rate, 'user_ratings':user_rate}

##############################################################################

def ready_df(db_path):
    """Prepare tables for analysis by merging them into one big DataFrame
    
    Parameters
    ----------
    db_path : str
        filepath to be fed to the import_db() function
    
    Returns
    -------
    outDF : pandas DataFrame
        a single DataFrame capturing all of the data in a more convenient configuration
    """
    df_dict = import_db(db_path)
    
    # merge the two ratings tables
    ratings_merged = pd.merge(df_dict['arseblog_ratings'], df_dict['user_ratings'], how='outer', on=['gameID', 'playerID']) 
    ratings_merged[['arseblograting', 'userrating']] = ratings_merged[['arseblograting', 'userrating']].apply(pd.to_numeric, errors='coerce')

    # merge ratings to games
    merged = pd.merge(df_dict['games'], ratings_merged, how='outer', on='gameID')
    
    # merge players to games + ratings
    merged = pd.merge(df_dict['players'], merged, how='outer', on='playerID')

    # preferred column order
    col_order = ['playerID', 'gameID', 'date', 'season', 'competition', 'home_away', 'opponent', 'arsegoals','oppgoals', 'wld', 'arseblograting', 'userrating', 'name', 'number', 'positions', 'natl_team', 'birthdate','academy_grad', 'nickname', 'rare_positions', 'url']
    
    outDF = merged[col_order]
    
    return outDF

##############################################################################

def import_table(db_path, table_name='games'):
    """Read in a single table from the database.
    
    Parameters
    ----------
    db_path : str
        Filepath to .db file
    table_name : {'games', 'players', 'arseblog_ratings', 'user_ratings'}
        Name of the table to import
    
    Returns
    -------
    table : pandas DataFrame
        The requested table, converted to a pandas DataFrame
    """
    # create DB connection
    conn = sqlite3.connect(db_path)
    table = None
    if table_name == 'games':
        table = pd.read_sql_query('select * from '+table_name+';', conn, parse_dates=['date'])
        table['gameID'] = table['gameID'].astype('category')
        conditions = [(table['arsegoals']>table['oppgoals']),
                      (table['arsegoals']==table['oppgoals']),
                      (table['arsegoals']<table['oppgoals'])]
        results = ['win', 'draw', 'loss']                                         
        table['result'] = np.select(conditions, results)
    elif table_name == 'players':
        table = pd.read_sql_query('select * from '+table_name+';', conn, parse_dates=['birthdate'])
        table['playerID'] = table['playerID'].astype('category')
    else:
        table = pd.read_sql_query('select * from '+table_name+';', conn)
        
    conn.close()
    return table

##############################################################################

def quick_summary(df, by='player'):
    """Create a simple dataframe with some basic data for a particular set of appearances
    
    Parameters
    ----------
    df : pandas DataFrame
        A dataframe where each row is a player appearance. Must have columns 'name',
        'arseblograting', and 'userrating'
    by : {'player', 'aggregate'}
        Indicate whether you want summary stats player-wise or for the whole group
    
    Returns
    -------
    summary_df : pandas DataFrame
        A dataframe summarizing the ratings for each player in the input dataframe or the whole group
    """
    if by=='player':
        summary_df = df.groupby(['name']).agg({'name': 'size',
                                               'userrating': ['mean','median','min','max'],
                                               'arseblograting': ['mean','median','min','max']}
                                             ).rename(columns={'name':'appearances'}
                                                     )
    elif by=='aggregate':
        summary_df = df[['userrating','arseblograting']].agg({'userrating':['size','mean','median','min','max'], 
                                                              'arseblograting':['size','mean','median','min','max']})
        summary_df = summary_df.unstack().to_frame().T
    return summary_df

##############################################################################

class Player(object):
    """A current or former Arsenal player.
    
    Attributes
    ----------
    name : str
        player name
    first_nm, last_nm : str
    number : str
        player shirt number
    positions: list of str from {'GK','RWB','RB','CB','LB','LWB','DM','CM','RM','LM','CAM','RAM','LAM','ST'}
        primary positions (i.e., where the player plays often)
    nat_team : str
        national team
    df : pandas DataFrame, optional
        pandas DataFrame containing all the data for that player
    birthdate : str, optional
        string of the format YYYY-MM-dd
    academy_grad = bool, optional
        True if the player came from the Arsenal Academy; else False
    nickname : str, optional
        something shorter to call them
    rare_positions : list of str, optional
        positions the player sometimes plays in; use same codes as `positions` list
    """
    
    def __init__(self, name, number, positions, natl_team, df=None, birthdate='', academy_grad = False, nickname=None, rare_positions=[]):
        """Return a new Player object"""
        self.name = name
        self.first_nm, self.last_nm = name.split()[0], name.split()[1]
        self.number = number
        self.positions = positions
        self.natl_team = natl_team
        self.df = df
        self.birthdate = birthdate
        self.academy_grad = academy_grad
        self.nickname = nickname
        if nickname in [None,  '']:
            self.nickname = self.last_nm
        self.rare_positions = rare_positions
    
    def appearances(self):
        """Calculate the number of entries for that player in the DataFrame"""
        self.appearances = len(self.df)
        return self.appearances
    
    def avg_rate(self, cols = ['arseblograting', 'userrating']):
        return {c[:-6]:self.df[c].mean() for c in cols}

    def ab_avg(self):
        return self.df['arseblograting'].mean()
    
    def user_avg(self):
        return self.df['userrating'].mean()

##############################################################################    

def make_Player(db_path, master_df=None):
    """Create a dictionary of objects of Player class
    
    Parameters
    ----------
    path : str
        filepath to be fed to the import_db() function
    
    Returns
    -------
    d : dict
        dictionary where keys are str of players' last names and values are instances of Player class
    """
    
    players_df = import_db(db_path)['players']
    
    players_df['positions'] = players_df['positions'].astype(str).map(lambda x: [x]) 
    players_df['rare_positions'] = players_df['rare_positions'].astype(str).map(lambda x: [x])

    d = {}
        
    for p in players_df.index:
        player = players_df.loc[p]
        lastn = player['name'].split()[1]
        d[lastn] = Player(player['name'], player['number'], player['positions'], player['natl_team'], 
                          birthdate = player['birthdate'], academy_grad=player['academy_grad'], 
                          nickname=player['nickname'], rare_positions=player['rare_positions']
                         )
        if master_df is not None:
            d[lastn].df = master_df[master_df['name']==d[lastn].name]
    return d

##############################################################################

def white2red():
    '''Create a seven-color sequential color scheme from white to red
    
    Returns
    -------
    w2r_palette : seaborn color palette
        A list of seven color definitions
    '''
    w2r_palette = sns.color_palette(['#f8f8f8',
                                '#eeeeee',
                                '#fdc7c7',
                                '#ff8686',
                                '#fb4444',
                                '#ee0000', 
                                '#cc0000'])
    return w2r_palette
