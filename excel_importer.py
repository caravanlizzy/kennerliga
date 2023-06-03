import pandas
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kennerliga.settings")
django.setup()
from user.models import User
from game.models import Game, GameOption, GameOptionChoice
from season.models import Season


class ExcelImporter:
    """ Read and export the kennerliga Excel file to the django database """

    def __init__(self):
        self.df = {}  # store dataframes with year as their key
        self.bga_names = set()
        self.data = {
            'games': {},
            'bga_names': set(),
            'results': [],
        }
        self.years = [2020, 2021, 2022]
        # self.years = [2022]
        self.write_season_to_db = True
        self.temp_league = 0

    def read_file(self, year):
        path = 'data_migration/data/'
        file_end = '.xlsm'
        file_name = str(year) + file_end
        self.df[year] = pandas.read_excel(path + file_name, None)

    def get_file(self, year):
        return self.df[year]

    def get_sheet(self, year, number=1):
        season_key = f'{year}_S{number}'
        return self.get_file(year)[season_key]

    def cell_isna(self, cell):
        return pandas.isna(cell)

    def get_cell(self, sheet, row, col):
        return sheet.iloc[row][col]

    def get_keyword_locations(self, year, month, keywords, exact=False):
        locations = []
        sheet = self.get_sheet(year, month)
        rows, cols = sheet.shape
        for col in range(cols):
            for row in range(rows):
                cell = self.get_cell(sheet, row, col)
                if (isinstance(cell, float)) or isinstance(cell, int):
                    continue
                for keyword in keywords:
                    if exact:
                        condition = keyword == cell
                    else:
                        condition = keyword in cell
                    if condition:
                        locations.append({"keyword": keyword, "row": row, "col": col})
        return locations

    def get_bga_names_from_gesamtwertung(self, year):
        sheet_key = f'{year}_GESAMTWERTUNG'
        sheet = self.get_file(year)[sheet_key]
        start_row = 4
        end_row = sheet.shape[0]
        col = 3
        for row in range(start_row, end_row):
            cell = self.get_cell(sheet, row, col)
            if self.cell_isna(cell):
                return
            else:
                self.data['bga_names'].add(cell)

    def iterate_all_cells(self, year, sheet_number, callback):
        sheet = self.get_sheet(year, sheet_number)
        rows, cols = sheet.shape
        for row in range(rows):
            for col in range(cols):
                cell = self.get_cell(sheet, row, col)
                callback(cell, row, col)

    @staticmethod
    def remove_extra_sheets(year):
        extra = 0
        if year == 2020:
            extra = 1
        elif year == 2022:
            extra = 2
        return extra

    def iterate_all_sheets(self, year, *callbacks):
        file = self.get_file(year)
        start_index = 0 if year == 2020 else 1
        for month in range(start_index, len(file) - self.remove_extra_sheets(
                year)):  # dont consider last 2 sheets, gesamtwertung and definitonen
            print(f'Importing {year}S{month}')
            self.create_season(year, month)
            for callback in callbacks:
                callback(year, month)

    @staticmethod
    def generate_liga_keywords(max_ligen):
        keywords = []
        for liga in range(1, max_ligen + 1):
            keywords.append(f'Liga {liga}')
        return keywords

    def get_games_locations(self, year, month):
        keywords = self.generate_liga_keywords(5)
        locations = self.get_keyword_locations(year, month, keywords)
        return locations

    def store_game(self, game):
        if game not in self.data['games'].keys():
            # create a game entry with empty options
            self.data['games'][game] = []

    def store_game_option(self, game, options):
        if options == '-':
            return
        options = options.split('\n')
        for option in options:
            option = option[2:]
            option, choice = option.split(':')
            option_object = {'option': option, 'choice': choice}
            self.data['games'][game].append(option_object)

    def get_games_from_leagues(self, year, month):
        sheet = self.get_sheet(year, month)
        rows_down_to_value = 4
        cols_right_to_value = 5
        if year == 2020:
            cols_right_to_value -= 1
            rows_down_to_value += 1
            if month > 1:
                cols_right_to_value += 1
        for location in self.get_games_locations(year, month):
            start_row = location['row'] + rows_down_to_value
            game_col = location['col'] + cols_right_to_value
            option_col = game_col + 1
            row = start_row
            try:
                game = self.get_cell(sheet, row, game_col)
                option = self.get_cell(sheet, row, option_col)
            except IndexError:
                print('Index Error - If not 2021S5: check for problems!')
            while not self.cell_isna(game):
                self.store_game(game)
                self.store_game_option(game, option)
                row += 1
                game = self.get_cell(sheet, row, game_col)
                option = self.get_cell(sheet, row, option_col)

    def get_match_results(self, year, month):
        keywords = ['Platzierung']
        locations = self.get_keyword_locations(year, month, keywords, True)
        for location_index, location in enumerate(locations):
            self.store_match_results(location, year, month)

    def get_league_from_location(self, month, year, location, sheet):
        col = 2
        row = location['row'] - 10
        if year == 2020 and month in [0, 1]:
            col = 3
        elif year == 2022:
            if not month == 1:
                row = location['row'] - 30
        league = self.get_cell(sheet, row, col)
        for r in range(1,20):
            if pandas.isna(league):
                row = row + 1
                col = 2
                league = self.get_cell(sheet, row, col)
                if not pandas.isna(league):
                    # print(league)
                    if not league[-1] == ':':
                        league = None
        if pandas.isna(league):
            return False
        elif league[-1] == ':':
            # print(league)
            print(league.split(' ')[1][0])
            return league.split(' ')[1][0]
        else:
            # print('elsing')
            return False

    def store_match_results(self, location, year, month):
        sheet = self.get_sheet(year, month)
        row = location['row']
        game = self.get_cell(sheet, row - 1, 4)
        if year == 2020 and month in [0, 1]:
            game = self.get_cell(sheet, row - 1, 3)
            # league = self.get_cell(sheet, row - 10, 3)
        next_row = row + 1
        league_check = self.get_league_from_location(month, year, location, sheet)
        if league_check:
            self.temp_league = league_check
        while self.store_match_result(next_row, year, month, self.temp_league, game, sheet):
            self.store_match_result(next_row, year, month, game, self.temp_league, sheet)
            next_row += 1

    def store_match_result(self, row, year, month, league, game, sheet):
        player = self.get_cell(sheet, row, 5)
        if self.cell_isna(player):
            return False
        starting_position = self.get_cell(sheet, row, 6)
        character = self.get_cell(sheet, row, 7)
        starting_points = self.get_cell(sheet, row, 8)
        points = self.get_cell(sheet, row, 9)
        tie_breaker = self.get_cell(sheet, row, 10)
        percentage_of_winner = self.get_cell(sheet, row, 11)
        position = self.get_cell(sheet, row, 12)
        league_points = self.get_cell(sheet, row, 13)
        year = year
        season = month
        league = league
        game = game
        result = {
            "player": player,
            "starting_position": starting_position,
            "character": character,
            "starting_points": starting_points,
            "points": points,
            "tie_breaker": tie_breaker,
            "percentage_of_winner": percentage_of_winner,
            "position": position,
            "league_points": league_points,
            "year": year,
            "season": season,
            "league": league,
            "game": game,
        }
        self.data['results'].append(result)

    def create_player(self, name):
        if self.name_unused(name):
            new_player = User.objects.create(username=name, email=f'{name}.{name}@test.de')
            new_player.save()

    @staticmethod
    def name_unused(name):
        return not User.objects.filter(username=name).exists()

    # create actual players
    def write_players_to_db(self):
        for player in self.data['bga_names']:
            self.create_player(player)

    @staticmethod
    def game_exists(game_name):
        return Game.objects.filter(name=game_name).exists()

    @staticmethod
    def game_option_exists(option):
        return GameOption.objects.filter(name=option).exists()

    @staticmethod
    def game_option_choice_exists(choice):
        return GameOptionChoice.objects.filter(name=choice).exists()

    def create_game(self, game_name):
        if not self.game_exists(game_name):
            new_game = Game(name=game_name)
            new_game.save()

    def create_game_option(self, option_name, game_name, bool_value):
        if not self.game_option_exists(option_name):
            game = Game.objects.filter(name=game_name)[0]
            if game:
                new_option = GameOption(name=option_name, game=game)
                if isinstance(bool_value, bool):
                    new_option.value = bool_value
                new_option.save()
                return new_option
            else:
                print(f'No game {game_name} for given option {option_name}')
        else:
            return GameOption.objects.filter(name=option_name)[0]

    def create_option_choice(self, choice_name, option):
        if not self.game_option_choice_exists(choice_name):
            new_choice = GameOptionChoice(name=choice_name, option=option)
            new_choice.save()

    @staticmethod
    def get_boolean_option_value(choice_name):
        option_value = None
        true_option_values = ['ja', 'aktiviert', 'aktiv', 'an']
        false_option_values = ['nein', 'deaktiviert', 'inaktiv', 'aus']
        choice_to_check = choice_name.lower().strip()
        if choice_to_check in true_option_values:
            option_value = True
        elif choice_to_check in false_option_values:
            option_value = False
        return option_value

    def write_games_to_db(self):
        games = self.data['games']
        for game_name in games:
            self.create_game(game_name)
            for settings in games[game_name]:
                option_name = settings['option']
                choice_name = settings['choice']
                boolean_value = self.get_boolean_option_value(choice_name)
                option = self.create_game_option(option_name, game_name, boolean_value)
                if not isinstance(boolean_value, bool):
                    self.create_option_choice(choice_name, option)

    @staticmethod
    def create_season(year, season):
        if not Season.objects.filter(year=year, month=season).exists():
            new_season = Season(year=year, month=season)
            new_season.save()

    @staticmethod
    def add_season_participant(season, participant):
        season.participants.add(participant)
        season.save()

    def import_files(self):
        for year in self.years:
            self.read_file(year)
            self.get_bga_names_from_gesamtwertung(year)
            self.iterate_all_sheets(year, self.get_games_from_leagues, self.get_match_results)


importer = ExcelImporter()
importer.import_files()
importer.write_games_to_db()
importer.write_players_to_db()
# print(importer.data)
