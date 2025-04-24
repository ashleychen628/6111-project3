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
        self.total_transactions = len(self.transactions)
        self.support_threshold = float(self.min_sup * self.total_transactions)

    
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
                L1.append(item)

        # Apriori algorithm by min_sup
        all_frequent_itemsets = self.apriori(L1, item_counts)
        # select the rules by min_conf
        rules_selected = self.generate_rules(all_frequent_itemsets)

        self.print_output(all_frequent_itemsets, rules_selected)

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
            L_k_sorted = sorted([sorted(list(itemset)) for itemset in L_k])
            for i in range(len(L_k_sorted)):
                for j in range(i + 1, len(L_k_sorted)):
                    l1 = list(L_k_sorted[i])
                    l2 = list(L_k_sorted[j])
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
    
    def generate_rules(self, frequent_itemsets):
        """ Generate the rules using the filtered itemsets. """
        rules = []
        for itemset in frequent_itemsets:
            if len(itemset) < 2:
                continue  

            # Generate all non-empty proper subsets of the itemset
            for i in range(1, len(itemset)):
                for LHS in combinations(itemset, i):
                    LHS = frozenset(LHS)
                    RHS = itemset - LHS
                    if len(RHS) == 1: # exactly one item on the right side
                        support_LHS_RHS_count = frequent_itemsets[itemset]  # already normalized
                        support_LHS_count = frequent_itemsets.get(LHS)

                        if support_LHS_count: # at least one item on the left side
                            confidence = support_LHS_RHS_count / support_LHS_count
                            support_LHS_RHS = support_LHS_RHS_count / self.total_transactions
                            if confidence >= self.min_conf:
                                rules.append((LHS, RHS, support_LHS_RHS, confidence))
                                # print(f'for A:{LHS}, and B:{RHS}, support_count={support_LHS_RHS_count}, support_AB={support_LHS_RHS}, support_A_count={support_LHS_count}, confidence={confidence}')

        return rules

    def print_output(self, frequent_itemsets, rules):
        """ Print the output to txt file. """
        # Sort rules by confidence (descending)
        sorted_rules = sorted(rules, key=lambda x: x[3], reverse=True)

        # Sort frequent list by support (descending)
        sorted_frequent = sorted(
            [(itemset, count) for itemset, count in frequent_itemsets.items()],
            key=lambda x: x[1], reverse=True
        )

        # Write to output.txt
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(f"==Frequent itemsets (min_sup={int(self.min_sup * 100)}%)\n")
            for itemset, count in sorted_frequent:
                support_percent = 100 * count / self.total_transactions
                items = ",".join(sorted(itemset))
                f.write(f"[{items}], {support_percent:.4f}%\n")

            f.write(f"==High-confidence association rules (min_conf={int(self.min_conf * 100)}%)\n")
            for A, B, support, confidence in sorted_rules:
                left = ",".join(sorted(A))
                right = ",".join(sorted(B))
                f.write(f"[{left}] => [{right}] (Conf: {confidence*100:.1f}%, Supp: {support*100:.4f}%)\n")
