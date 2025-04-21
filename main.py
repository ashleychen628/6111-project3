import sys
import json


def main(filename, min_sup, min_conf):
    dataMining = DataMining(filename, min_sup, min_conf)
    dataMining.start()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 main.py INTEGRATED-DATASET.csv <min_sup> <min_conf>")
        sys.exit(1)

    try:
        filename = sys.argv[1]
        min_sup = sys.argv[2]
        min_conf = sys.argv[3]

    except ValueError:
        print("Error: 'r' and 'k' must be integers.")
        sys.exit(1)

    main(filename, min_sup, min_conf)
