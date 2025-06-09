import csv

class Model:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.col_model = 'Nom_Model'
        self.col_price = 'Prix'
    
    def extract_model_prix(self):
        """
        Reads a semicolon-delimited CSV file and returns a dictionary
        with 'Nom_Model' as keys and 'Prix' as values.

        :param file_path: Path to the CSV file
        :return: Dictionary {col_model: col_price}
        """
        result = {}
        with open(self.file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                nom_model = row.get(self.col_model)
                prix = row.get(self.col_price)
                if nom_model is not None and prix is not None:
                    result[nom_model] = prix
        return result
    
    
# Extract CSV_Modeles_Baguettes
csv_baguettes_filepath = "CSV/CSV_Modeles_Baguettes.csv"
# Create instance of model
csv_baguettes_model = Model(csv_baguettes_filepath)
# Extract csv file and store in a dict
csv_baguettes_dict = csv_baguettes_model.extract_model_prix()
# Get keys and store them in a list
csv_baguettes_keys_list = list(csv_baguettes_dict.keys())

# Extract CSV_Modeles_Carre / Square
csv_carre_filepath = "CSV/CSV_Modeles_Carre.csv"
# Create instance of model
csv_carre_model = Model(csv_carre_filepath)
# Extract csv file and store in a dict
csv_carre_dict = csv_carre_model.extract_model_prix()
# Get keys and store them in a list
csv_carre_keys_list = list(csv_carre_dict.keys())

# Extract CSV_Modeles_Frise
csv_frise_filepath = "CSV/CSV_Modeles_Frise.csv"
# Create instance of model
csv_frise_model = Model(csv_frise_filepath)
# Extract csv file and store in a dict
csv_frise_dict = csv_frise_model.extract_model_prix()
# Get keys and store them in a list
csv_frise_keys_list = list(csv_frise_dict.keys())

# Extract CSV_Modeles_Hexa
csv_hexa_filepath = "CSV/CSV_Modeles_Hexa.csv"
# Create instance of model
csv_hexa_model = Model(csv_hexa_filepath)
# Extract csv file and store in a dict
csv_hexa_dict = csv_hexa_model.extract_model_prix()
# Get keys and store them in a list
csv_hexa_keys_list = list(csv_hexa_dict.keys())

# Extract CSV_Modeles_Tapis / Berber Carpet
csv_tapis_filepath = "CSV/CSV_Modeles_Tapis.csv"
# Create instance of model
csv_tapis_model = Model(csv_tapis_filepath)
# Extract csv file and store in a dict
csv_tapis_dict = csv_tapis_model.extract_model_prix()
# Get keys and store them in a list
csv_tapis_keys_list = list(csv_tapis_dict.keys())