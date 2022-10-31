import pandas


class ExcelImporter:

    def __init__(self, file_name='data.xlsm', year=2022):
        self.file_name = file_name
        self.year = year
        self.df = pandas.DataFrame() # empty dataframe, to be filled by read_file

    def read_file(self):
        self.df = pandas.read_excel(self.file_name, None)
        return self.df

    def iterate_cells(self, callback):
        rows = len(df)
        cols = len(df.ilos[0])
        for row in range(rows):
            for col in range(cols):
                cell = df.iloc[row][col]
                callback()

    def get_keyword_locations(cell, row, col):
        locations = {}
        keywords = [
            'Angemeldete Spieler für',
        ]
        for keyword in keywords:
            if keyword in cell:
                locations[keyword] = {"row": row, "col": col}
        return locations


    def import_players(self):
        trigger_word = 'Angemeldete Spieler für'

