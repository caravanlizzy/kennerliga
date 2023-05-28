import pandas
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kennerliga.settings")
django.setup()
from user.models import User
from game.models import Game, GameOption, GameOptionChoice


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
        for month in range(start_index, len(file) - self.remove_extra_sheets(year)):  # dont consider last 2 sheets, gesamtwertung and definitonen
            print(f'Importing {year}S{month}')
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
        if not game in self.data['games'].keys():
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
        for location in locations:
            self.store_match_results(location, year, month)

    def store_match_results(self, location, year, month):
        sheet = self.get_sheet(year, month)
        row = location['row']
        game = self.get_cell(sheet, row - 1, 4)
        next_row = row + 1
        while self.store_match_result(next_row, year, month, game, sheet):
            self.store_match_result(next_row, month, game, sheet)
            next_row += 1

    def store_match_result(self, row, year, month, game, sheet):
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
            "game": game,
        }
        self.data['results'].append(result)


def create_player(name):
    if name_unused(name):
        new_player = User.objects.create(username=name, email=f'{name}.{name}@test.de')
        new_player.save()


def name_unused(name):
    return not User.objects.filter(username=name).exists()


# create actual players
def store_players():
    for player in players:
        create_player(player)


def game_exists(game_name):
    return Game.objects.filter(name=game_name).exists()


def game_option_exists(option):
    return GameOption.objects.filter(name=option).exists()


def game_option_choice_exists(choice):
    return GameOptionChoice.objects.filter(name=choice).exists()


def create_game(game_name):
    if not game_exists(game_name):
        new_game = Game(name=game_name)
        new_game.save()


def create_game_option(option_name, game_name, bool_value):
    if not game_option_exists(option_name):
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


def create_option_choice(choice_name, option):
    if not game_option_choice_exists(choice_name):
        new_choice = GameOptionChoice(name=choice_name, option=option)
        new_choice.save()


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


def store_games():
    for game_name in games:
        create_game(game_name)
        for settings in games[game_name]:
            option_name = settings['option']
            choice_name = settings['choice']
            boolean_value = get_boolean_option_value(choice_name)
            option = create_game_option(option_name, game_name, boolean_value)
            if not isinstance(boolean_value, bool):
                create_option_choice(choice_name, option)


I = ExcelImporter()
years = [2020, 2021, 2022]

for y in years:
    I.read_file(y)
    I.get_bga_names_from_gesamtwertung(y)
    I.iterate_all_sheets(y, I.get_games_from_leagues, I.get_match_results)

results, players, games = I.data['results'], I.data['bga_names'], I.data['games']
store_games()
