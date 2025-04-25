# 6111-project3

# Data Mining

#### Names: Danyao Chen
#### UNI: dc3861

## **Code Structure**
```
|-- INTEGRATED-DATASET.csv
|-- main.py
|-- datamining.py
|-- output.txt
```

## **Run the Project**
```sh
git clone https://github.com/your-username/your-repo.git
cd your-repo

// after creating your virtual environment
python3 -m venv env
source env/bin/activate
(env) pip install -r requirements.txt

// after activate your env
(env) python3 main.py INTEGRATED-DATASET.csv <min_sup> <min_conf>
// example
(env) python3 main.py INTEGRATED-DATASET.csv 0.01 0.5
```

## **Project Setup**
#### 1. NYC Open Data sets I used to generate the INTEGRATED-DATASET.csv:
New York City Leading Causes of Death

https://data.cityofnewyork.us/Health/New-York-City-Leading-Causes-of-Death/jb7j-dtam/about_data

#### 2. Dataset Preprocessing Steps:
* Column Selection
  * The columns "Leading Cause", "Sex", "Race Ethnicity", and "Deaths" were extracted from the original dataset. (I also deleted the first row of column names and the title for convenience)
  * Other fields (Year, Age Adjusted Death Rate) were ignored.
  * Column "Year" is ignored because including "Year" would have fragmented the dataset, turning otherwise frequent patterns into smaller, year-specific subsets.
    For example, the pattern [Sex=F, Cause=Diabetes] might occur consistently across years, but including the year would spread this across multiple itemsets like:
   ```
      [Sex=F, Cause=Diabetes, Year=2017]
      [Sex=F, Cause=Diabetes, Year=2018]
   ```
     This would reduce support for each pattern and obscure meaningful trends. Apriori works best when items co-occur across many transactions, however, I think year-based splitting weakens that signal.
   I experimented with including the "Year" column in the dataset but found that it led to a larger number of interfering or uninformative rules. For example, in the year 2009, the combination [Race_Ethnicity=White Non-Hispanic, Year=2009] produced two rules:
   ```
   [Race_Ethnicity=White Non-Hispanic, Year=2009] => [Sex=F] (Conf: 50.0%)
   [Race_Ethnicity=White Non-Hispanic, Year=2009] => [Sex=M] (Conf: 50.0%)
   ```
   Since the dataset only includes binary gender values (F and M and Unknown), this 50/50 split is deterministic and trivial for that combination — it doesn’t provide any new insight. Including "Year" simply causes these repetitive rules to be generated for every year, cluttering the output without revealing meaningful patterns. As a result, I chose to remove the "Year" column to focus the algorithm on more generalizable and interesting associations.
  <img width="674" alt="Screen Shot 2025-04-24 at 19 39 43" src="https://github.com/user-attachments/assets/e2176ed7-69e4-4044-a88e-74d81daf3243" />

  * Column "Age Adjusted Death Rate" is ignored, since it's a continuous variable, not a categorical item — and Apriori is fundamentally designed for discrete, categorical data. Including it would require discretization (e.g., low/medium/high), which introduces subjective bins and complexity, because these data are too scattered and are not within some specific range (I found it hard to do a reasonable discretization). As an alternative, the Deaths column already provides a reliable, interpretable weight to express frequency — and was used to weight the support counts. In addition, adding death rate would be redundant and noisy, and it could distort the support-based confidence calculation.

* Row Filtering
  * Only rows with non-empty values for all three categorical columns were retained.
  * In the original data sets, the codes inside the parentheses behind each leading cause (e.g. V01-X39, X43, X45-X59, Y85-Y86 refer to ICD-10 codes) are International Classification of Diseases, used globally to categorize causes of death. I deleted contents inside this parentheses to reduce complexity. Otherwise, they're making the item inside transactions too long and hard to read. I believe this deletion won't influence the apriori calculation result because they're unique to each leading cause, the remaining leading causes keep the same.
* Transformation into Transactions
  * Each row was transformed into a set of key=value items:
  * Example:
    Row: "Diabetes Mellitus", "F", "Hispanic"
    → Basket: { "Leading_Cause=Diabetes Mellitus", "Sex=F", "Race_Ethnicity=Hispanic" }
  * Why key=value?
    * To ensure that each item is unambiguous and uniquely identifies both the attribute and its value.
    * This won't hurt the calculation of support or confidence.
* Adding Death Weights
  * The Deaths value from each row was retained as a numeric weight and stored alongside the transaction for support weighting during the Apriori computation.
* Final Output Format
  * The resulting INTEGRATED-DATASET.csv is a four-column file:
  ``` Leading Cause, Sex, Race Ethnicity, Deaths ```

#### What makes my choice of INTEGRATED-DATASET file compelling
1. Rich and High-Quality Categorical Information
   
   This dataset offers clean, well-structured categorical variables that are highly suitable for market-basket style mining:
     * Leading Cause – the type of disease or condition that caused death.
     * Sex – male or female.
     * Race Ethnicity – multiple clearly defined demographic groups.
     * Deaths – a numeric value that provides real-world frequency for weighting.
       
   These variables translate naturally into discrete items, enabling meaningful itemsets and interpretable association rules.
   
2. Meaningful Real-World Patterns

   The dataset captures public health outcomes across demographic lines. This makes the frequent itemsets and association rules directly relevant to real-world concerns like:
   * Which diseases disproportionately affect certain gender or racial groups.
   * Which demographics are more frequently associated with specific causes of death.
     
   This goes beyond artificial data and enables data-driven reasoning about equity, disparities, and public health trends in NYC.

3. Support for Weighted Frequency (Deaths)

   Unlike typical categorical datasets, this one includes a Deaths column which allows: 1) Death-weighted support calculations, improving accuracy and relevance. 2) Avoiding artificial row duplication — each transaction can be weighted by its real-world impact. This made it possible to calculate support and confidence values that reflect actual human loss, not just row counts.

## **Internal Design of the Project**
This project implements the classic Apriori algorithm to discover frequent itemsets and generate high-confidence association rules from a preprocessed NYC Open Data dataset (INTEGRATED-DATASET.csv). The implementation includes custom adaptations for categorical encoding and optional support weighting.

Key Components:
1. Preprocessing: read_transactions_from_csv()
* Each row in the dataset is converted into a set of key=value strings, e.g.: {"Leading_Cause=Diabetes Mellitus", "Sex=F", "Race_Ethnicity=Hispanic"}
* This avoids ambiguity between values (e.g., "F" for sex vs. something else), and makes the generated rules interpretable and distinct.
* The result is a list of transaction sets stored in self.transactions.

2. Frequent Itemset Mining: apriori() (a-priori algorithm described in Section 2.1 of the Agrawal and Srikant paper in VLDB 1994)
* The algorithm starts by counting support for all 1-itemsets (L1).
* It iteratively generates candidate k-itemsets (Ck) by self-joining frequent (k-1)-itemsets and pruning those whose (k−1)-subsets are not all frequent.
* Support counting is handled using count_support(), which checks for subset inclusion using set operations.
* Itemsets are only retained if they meet the global support threshold (derived from min_sup).

3. Association Rule Generation: generate_rules()
* For every frequent itemset of size ≥ 2, the code generates all possible rules of the form A => B, where:
  * LHS is a non-empty subset of the itemset.
  * RHS is exactly one item (as required by spec).
  * A and B are disjoint: RHS = itemset - LHS.
* confidence is calculated using confidence = support_LHS_RHS_count / support_LHS_count (number of LHS U RHS / number of LHS) 
* A rule is included if it meets the min_conf threshold.

4. Output Formatting: print_output()
* Results are written to output.txt in two parts:
  * A list of frequent itemsets with their support percentages.
  * A list of rules sorted by descending confidence, formatted with both support and confidence values.

5. Weighting:
* Instead of treating each row in the dataset as a single, equally weighted transaction, I used the "Deaths" column to weight each transaction by the number of deaths it represents.
* Each row in the dataset (i.e., one combination of Leading Cause, Sex, and Race Ethnicity) is not just a category — it reflects a real-world frequency: how many people actually died under that condition.
* I did not duplicate rows. Instead, I implemented a parallel list of transaction weights (self.transaction_weights), where each weight corresponds to the Deaths value of a row.
* When counting itemset support (in both 1-itemset and k-itemset passes), I used:
  ```
  support[itemset] += weight
  ```
  rather than incrementing by 1.
* Why?
  * Reflect Real-World Impact:
    The dataset includes actual mortality counts. A row with 300 deaths is far more significant than one with 3 deaths. Weighting the support ensures that more deadly patterns carry more influence in the results.
  * Avoid Distorting Results:
    Treating each row equally would give equal support to a rare but heavily deadly combination (e.g., a specific disease that only occurs once but causes many deaths) and a common but low-mortality one. This would underrepresent critical health risks.

## **The command line specification of a compelling sample run**
```
python3 main.py INTEGRATED-DATASET.csv 0.01 0.5
```
where minimum support = 0.01
confidence = 0.5
* When min_sup = 0.01, total number of transactions is 1094, 1094*0.01 = 10.94. To be considered frequent, each itemset must appear at least 11 times. Given that the dataset includes only a few values for Sex and Race Ethnicity, but over 25 distinct leading causes of death, the data is naturally spread out. So reaching a support count of 11 already indicates a pattern that is noticeable and meaningful in the context of this dataset.
* When min_conf = 0.5, it produces string, interpretable rules with fewer borderline/noisy cases. However, when I test out with min_conf = 0.4, it revealed several weaker but consistent trends (e.g., symmetrical demographic splits and low-support disease-demographic associations), which could be of interest in exploratory analyses or follow-up studies but not super compelling for our project.
* These rules reflect real-world public health disparities and are backed by sufficient data volume, making them both statistically significant and socially relevant. This makes the chosen thresholds (support = 0.01, confidence = 0.5) a compelling setting for discovering high-impact and explainable patterns.
