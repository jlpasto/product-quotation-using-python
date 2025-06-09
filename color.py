import csv

class Couleur:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.col_color = 'Nom Couleur'
        self.col_price = 'Prix'
    
    def extract_color_prix(self):
        """
        Reads a semicolon-delimited CSV file and returns a dictionary
        with 'Nom Couleur' as keys and 'Prix' as values.

        :param file_path: Path to the CSV file
        :return: Dictionary {col_color: col_price}
        """
        result = {}
        with open(self.file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                nom_color = row.get(self.col_color)
                prix = row.get(self.col_price)
                if nom_color is not None and prix is not None:
                    result[nom_color] = prix
        return result
    
# Extract CSV_Couleur
csv_couleur_filepath = "CSV/CSV_Couleur.csv"
# Create instance of Couleur
csv_couleur = Couleur(csv_couleur_filepath)
# Extract csv file and store in a dict
csv_couleur_dict = csv_couleur.extract_color_prix()
# Get keys and store them in a list
csv_couleur_keys_list = list(csv_couleur_dict.keys())