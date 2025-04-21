import csv
from collections import defaultdict

class DataMining:
    def __init__(self, filename, min_sup, min_conf):
        self.filename = filename
        self.min_sup = min_sup
        self.min_conf = min_conf
    
    def start(self):
        """ Start the Data Mining process. """
        # get the transactions in form of list of transactions
        transactions = self.read_transactions_from_csv()
        total_transactions = len(transactions)
        
        # count largest 1-itemsets to get L1
        item_counts = defaultdict(int)
        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1
        
        # Compute L1 by filtering with min_sup threshold
        support_threshold = float(self.min_sup * total_transactions)
        L1 = []
        for item, count in item_counts.items():
            if count >= support_threshold:
                L1.append((frozenset([item]), count))

        # DEBUG PRINTS
        # print("L1 frequent 1-itemsets:")
        # for itemset, count in L1:
        #     support_percent = 100 * count / total_transactions
        #     print(f"{list(itemset)}: {support_percent:.2f}%")

        # 


    def read_transactions_from_csv(self):
        """ Read dataset in filename into a list of sets. """
        transactions = []
        with open(self.filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 3:
                    continue  # skip invalid rows
                leading_cause = row[0].strip()
                sex = row[1].strip()
                race = row[2].strip()
                if leading_cause and sex and race:
                    basket = {
                        f"Leading_Cause={leading_cause}",
                        f"Sex={sex}",
                        f"Race_Ethnicity={race}"
                    }
                    transactions.append(basket)
        return transactions