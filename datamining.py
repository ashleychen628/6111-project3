import csv
from collections import defaultdict
from itertools import combinations

class DataMining:
    def __init__(self, filename, min_sup, min_conf):
        self.filename = filename
        self.min_sup = min_sup
        self.min_conf = min_conf

        # get the transactions in form of list of transactions
        self.transactions = self.read_transactions_from_csv()
        total_transactions = len(self.transactions)
        self.support_threshold = float(self.min_sup * total_transactions)

    
    def start(self):
        """ Start the Data Mining process. """
        # count largest 1-itemsets to get L1
        item_counts = defaultdict(int)
        for transaction in self.transactions:
            for item in transaction:
                item_counts[frozenset([item])] += 1
        
        # Compute L1 by filtering with min_sup threshold
        L1 = []
        for item, count in item_counts.items():
            if count >= self.support_threshold:
                # L1.append((frozenset([item]), count))
                L1.append(item)

        # print(item_counts)
        self.apriori(L1, item_counts)
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
                    # adding to a set
                    basket = {
                        f"Leading_Cause={leading_cause}",
                        f"Sex={sex}",
                        f"Race_Ethnicity={race}"
                    }
                    transactions.append(basket)
        return transactions
    
    def count_support(self, itemsets):
        """ Count support and filter the list using min_sup. """
        candidate_counts = defaultdict(int)
        for trans in self.transactions:
            for item in itemsets:
                if item.issubset(trans):
                    candidate_counts[item] += 1

        return candidate_counts

    def apriori(self, L1, item_counts):
        """ Do the a-priori algorithm. """
        L_k = L1
        k = 2
        all_frequent_itemsets = {i: item_counts[i] for i in L_k}
        # print(all_frequent_itemsets)
        while L_k:
            C_k = []
            L_k_sorted = sorted(L_k)
            for i in range(len(L_k_sorted)):
                for j in range(i + 1, len(L_k_sorted)):
                    l1 = list(L_k_sorted[i])
                    l2 = list(L_k_sorted[j])
                    l1.sort()
                    l2.sort()
                    # match first k-2 items
                    if l1[:k-2] == l2[:k-2]:  
                        # take union of the two sets
                        candidate = frozenset(set(l1) | set(l2))
                        # Prune: check all (k-1)-subsets are frequent
                        subsets = combinations(candidate, k - 1)
                        if all(frozenset(s) in all_frequent_itemsets for s in subsets):
                            C_k.append(candidate)

            candidate_counts = self.count_support(C_k)
            L_k = [c for c in C_k if candidate_counts[c] >= self.support_threshold]
            for c in L_k:
                all_frequent_itemsets[c] = candidate_counts[c]
            
            k += 1

        return all_frequent_itemsets
        # for item, count in all_frequent_itemsets.items():
        #     print(f'{item}: {count}')