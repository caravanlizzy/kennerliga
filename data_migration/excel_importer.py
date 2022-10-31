import pandas


class ExcelImporter:

    def __init__(self, file_name='data.xlsm', year=2022):
        self.file_name = file_name
        self.year = year
        self.df = self.read_file()
        self.keywords = [
            'Angemeldete Spieler',
        ]
        self.keyword_locations = {}
        self.bga_names = set()

    def read_file(self):
        self.df = pandas.read_excel(self.file_name, None)
        return self.df

    def get_sheet(self, number=1):
        season_key = f'{self.year}_S{number}'
        return self.df[season_key]

    def iterate_all_cells(self, sheet_number,  callback):
        sheet = self.get_sheet(sheet_number)
        rows = len(sheet)
        cols = len(sheet.iloc[0])
        for row in range(rows):
            for col in range(cols):
                cell_content = sheet.iloc[row][col]
                callback(cell_content, row, col)

    def set_keyword_locations(self, cell_content, row, col):
        locations = {}
        for keyword in self.keywords:
            if (isinstance(cell_content, float)) or isinstance(cell_content, int): 
                return
            if keyword in cell_content:
                self.keyword_locations[keyword] = {"row": row, "col": col}
    
    def get_bganames_from_anmeldung(self, month):
        # dont need anymore - keep for other monthly auswertungen
        start_row = 4
        col = 4
        sheet = self.get_sheet(month)
        for row in range(start_row, sheet.shape[0] - start_row -1):
            cell_content =  sheet.iloc[row][col]
            if pandas.isna(cell_content):
                return 
            else:
                self.bga_names.add(cell_content)

    def get_bganames_from_gesamtwertung(self):
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
                self.bga_names.add(cell_content)
            

    def iterate_all_sheets(self, *callbacks):
        for month in range(1, len(self.df) -1 ): # dont consider last 2 sheets, gesamtwertung and definitonen
            print(f'season: {month}')
            for callback in callbacks:
                callback(month)

I = ExcelImporter()
I.read_file()
# I.iterate_all_sheets(I.get_bganames_from_anmeldung)
I.get_bganames_from_gesamtwertung()
print(I.bga_names)
print(len(I.bga_names))

