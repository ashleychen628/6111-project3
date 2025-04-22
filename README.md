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
  * The columns "Leading Cause", "Sex", "Race Ethnicity", and "Deaths" were extracted from the original dataset.
  * Other fields (Year, Age Adjusted Death Rate) were ignored.
  * Column "Year" is ignored because including "Year" would have fragmented the dataset, turning otherwise frequent patterns into smaller, year-specific subsets.
    For example, the pattern [Sex=F, Cause=Diabetes] might occur consistently across years, but including the year would spread this across multiple itemsets like:
   ```
      [Sex=F, Cause=Diabetes, Year=2017]
      [Sex=F, Cause=Diabetes, Year=2018]
   ```
     This would reduce support for each pattern and obscure meaningful trends. Apriori works best when items co-occur across many transactions, however, I think year-based splitting weakens that signal.
  * Column "Age Adjusted Death Rate" is ignored, since it's a continuous variable, not a categorical item — and Apriori is fundamentally designed for discrete, categorical data. Including it would require discretization (e.g., low/medium/high), which introduces subjective bins and complexity. As an alternative, the Deaths column already provides a reliable, interpretable weight to express frequency — and was used to weight the support counts. In addition, adding death rate would be redundant and noisy, and it could distort the support-based confidence calculation.

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
