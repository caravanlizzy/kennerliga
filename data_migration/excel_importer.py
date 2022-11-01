import pandas

class ExcelImporter:
    """ Read and export the kennerliga excel file to the django database """

    def __init__(self, file_name='data.xlsm', year=2022):
        self.file_name = file_name
        self.year = year
        self.df = self.read_file()
        self.bga_names = set()
        self.data = {
            'games':{},
            'bga_names':set(),
        }

    def read_file(self):
        self.df = pandas.read_excel(self.file_name, None)
        return self.df

    def get_sheet(self, number=1):
        season_key = f'{self.year}_S{number}'
        return self.df[season_key]

    def get_keyword_locations(self, month,  keywords):
        locations = []
        sheet = self.get_sheet(month)
        rows, cols = sheet.shape
        for col in range(cols):
            for row in range(rows):
                for keyword in keywords:
                    cell_content = sheet.iloc[row][col]
                    if (isinstance(cell_content, float)) or isinstance(cell_content, int):
                        continue
                    else:
                        if keyword in cell_content:
                            locations.append({"keyword":keyword, "row": row, "col": col})
        return locations

    def get_bga_names_from_gesamtwertung(self):
        sheet_key = f'{self.year}_GESAMTWERTUNG'
        sheet = self.df[sheet_key]
        start_row = 4
        end_row = sheet.shape[0];
        col =  3
        for row in range(start_row, end_row):
            cell_content =  sheet.iloc[row][col]
            if pandas.isna(cell_content):
                return
            else:
                self.data['bga_names'].add(cell_content)

    def iterate_all_cells(self, sheet_number,  callback):
        sheet = self.get_sheet(sheet_number)
        rows, cols = sheet.shape
        for row in range(rows):
            for col in range(cols):
                cell_content = sheet.iloc[row][col]
                callback(cell_content, row, col)

    def iterate_all_sheets(self, *callbacks):
        for month in range(1, len(self.df) -1 ): # dont consider last 2 sheets, gesamtwertung and definitonen
            print(f'season: {month}')
            for callback in callbacks:
                callback(month)

    def generate_liga_keywords(self, max_ligen):
        keywords = []
        for liga in range(1, max_ligen + 1):
            keywords.append(f'Liga {liga}')
        return keywords

    def get_games_from_leagues(self, month):
        games = []
        sheet = self.get_sheet(month)
        keywords = self.generate_liga_keywords(5)
        locations = self.get_keyword_locations(month, keywords)
        for location in locations:
            start_row = location['row'] + 4
            game_col = location['col'] + 5
            option_col = game_col + 1
            row = start_row
            game = sheet.iloc[row][game_col]
            self.add_game(game)
            while not pandas.isna(sheet.iloc[row][option_col]):
                if not self.game_exists(game):
                    self.add_game(game)
                option = sheet.iloc[row][option_col]
                self.add_game_option(game, option)
                print(self.data['games'])
                row += 1

    def game_exists(self, game):
        return game in self.data['games'][game]

    def add_game(self, game):
        self.data['games'][game] = []

    def add_game_option(self, game, option):
        self.data['games'][game].append(option)


I = ExcelImporter()
I.read_file()
# I.iterate_all_sheets(I.get_bga_names_from_anmeldung)
I.get_bga_names_from_gesamtwertung()
# print(I.bga_names)
# print(len(I.bga_names))
I.iterate_all_sheets(I.get_games_from_leagues)
print(I.data)

# def get_bga_names_from_anmeldung(self, month):
#     # dont need anymore - keep for other monthly auswertungen
#     start_row = 4
#     col = 4
#     sheet = self.get_sheet(month)
#     for row in range(start_row, sheet.shape[0] - start_row -1):
#         cell_content =  sheet.iloc[row][col]
#         if pandas.isna(cell_content):
#             return
#         else:

#             self.bga_names.add(cell_content)
