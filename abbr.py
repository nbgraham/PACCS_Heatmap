import csv


def remove_duplicates(infilename, outfilename):
    rows = []

    with open(infilename, 'rt', encoding='utf8') as csvinfile:
        reader = csv.reader(csvinfile)
        prev_row = None
        for row in reader:
            if row != prev_row:
                rows.append(row)
            prev_row = row

    with open(outfilename, 'wt', encoding='utf8') as csvoutfile:
        writer = csv.writer(csvoutfile)

        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    remove_duplicates(r'C:\Users\nickb\Google Drive\Career\PACCS\BuildingAbbreviations.csv',
                      r'C:\Users\nickb\Google Drive\Career\PACCS\building_abbreviations.csv')