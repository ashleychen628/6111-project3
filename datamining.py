class DataMining:
    def __init__(self, filename, min_sup, min_conf):
        self.filename = filename
        self.min_sup = min_sup
        self.min_conf = min_conf
    
    def start(self):
        """ Start the Data Mining process. """
        transactions = self.read_transactions_from_csv
        print(transactions)

    def read_transactions_from_csv(self):
        """ Read dataset in filename into a list of sets. """
        transactions = []
            with open(self.filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            basket = set()
            for column, value in row.items():
                if value.strip():  # skip blanks
                    basket.add(f"{column.strip()}={value.strip()}")
            transactions.append(basket)
        return transactions