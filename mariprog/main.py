"""
Parse the site dump spreadsheet from Mallard and get nice stuff from it.
"""
import csv
import re
from datetime import date

inspections_in_programme = []
LIST_OF_PORTS = []
INITIALS = ["KS", "PN", "SP", "ML", "SC", "DS", "WW", "GE", "TL", "PD", "AO"]
WEEKS = []
DATE_PATTERN = re.compile("^\d{1,2}\/\d{1,2}\/\d{2,4}$")


def parse_programme_date(date_string):
    dstring = date_string.split("/")
    return date.fromisoformat("-".join([_convert_year_str(dstring[2]), dstring[1], dstring[0]]))


def _convert_year_str(year_str):
    if len(year_str) == 2:
        return f"20{year_str}"
    elif len(year_str) == 4:
        return year_str
    else:
        return year_str


class Inspection:

    def __init__(self, week_begining, inspection_data):
        self._inspection_data = inspection_data
        self.week_begining = parse_programme_date(week_begining)

    def __repr__(self):
        return [item[1] for item in self._inspection_data if item[0] == "Facility"][0]

    @property
    def facility(self):
        return [item[1] for item in self._inspection_data if item[0] == "Facility"][0]

    @property
    def location(self):
        return [item[1] for item in self._inspection_data if item[0] == "Location"][0]

    @property
    def inspectors(self):
        return [item[0] for item in self._inspection_data if item[1] == "X" and item[0] in INITIALS]

    @property
    def comments(self):
        return [item[1] for item in self._inspection_data if item[0] == "Comments/Date"][0]


class PortFromCSVRow:
    def __init__(self, row):
        self.site_name = row['SiteName'].strip()
        self.county = row['County'].strip()
        self.last_inspection_date = self.parse_date_string(row['DateOfLastInspection'])
        self.frequency_target = row['FrequencyTarget'].strip() if row['FrequencyTarget'] else "XXXXX"
        self.pfsi_category = row['SubCategoryDesc'].strip()
        self.site_category = row['SiteCategoryDesc'].strip()

    def parse_date_string(self, date_string):
        try:
            dstring = date_string.split()[0]
        except IndexError:
            return date(1900, 1, 1)
        year = dstring.split("-")[2]
        month = dstring.split("-")[1]
        day = dstring.split("-")[0]
        return date.fromisoformat("-".join([year, month, day]))

    def __repr__(self):
        return f"{self.site_name}: {self.pfsi_category}"


def _get_header_key_from_csv(opened_csv):
    reader = csv.reader(opened_csv)
    for row in reader:
        if row[0] == "Week Comm":
            return row
    opened_csv.close()


def parse_programme(csv_file):
    """
    Parses the current programme spreadsheet.
    """
    current_week = ""

    with open(csv_file, "r", encoding="ISO-8859-1") as csvfile:
        csv_reader = csv.reader(csvfile)
        key = _get_header_key_from_csv(csvfile)
        for row in csv_reader:
            if re.match(DATE_PATTERN, row[0]):
                WEEKS.append(parse_programme_date(row[0]))
                inspection = Inspection(row[0], list(zip(key, row)))
                current_week = row[0]
                inspections_in_programme.append(inspection)
            elif row[0] == "":
                inspection = Inspection(current_week, list(zip(key, row)))
                inspections_in_programme.append(inspection)

        for inspection in inspections_in_programme:
            print(inspection.week_begining, inspection.location, inspection.facility, inspection.inspectors, inspection.comments)


def parse_csv(csv_file):
    """
    Parses the csv file.
    """
    try:
        with open(csv_file, "r", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                port = PortFromCSVRow(row)
                if row['SiteTypeDesc'] == "Port":
                    LIST_OF_PORTS.append(port)
    except UnicodeDecodeError:
        # the file was made on Windoze
        with open(csv_file, "r", encoding="ISO-8859-1") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                port = PortFromCSVRow(row)
                if row['SiteTypeDesc'] == "Port":
                    LIST_OF_PORTS.append(port)



def print_site_data_to_terminal(filename):
    parse_csv(filename)
    sorted_list = sorted(LIST_OF_PORTS, key=lambda port: port.last_inspection_date)
    for port in sorted_list:
        print(f"{port.site_name:<60} --- {port.county:<20} {port.pfsi_category:<10} {port.site_category:<10} {port.frequency_target:<5} {port.last_inspection_date}")


# TODO check this
def week_port_is_in_programme(port):
    for p in LIST_OF_PORTS:
        if p.site_name == port:
            for inspection in inspections_in_programme:
                if port == inspection.facility:
                    print(port, inspection.week_begining)


def count_inspections_for_inspector(initials):
    count = 0
    for inspection in inspections_in_programme:
        if initials in inspection.inspectors:
            count += 1
    return count


def main():
    """
    Main function.
    """
    print_site_data_to_terminal("dump.csv")
    parse_programme("programme.csv")
    print("ML: ", count_inspections_for_inspector("ML"))
    print("WW: ", count_inspections_for_inspector("WW"))
    print("TL: ", count_inspections_for_inspector("TL"))
    print("GE: ", count_inspections_for_inspector("GE"))
    print("KS: ", count_inspections_for_inspector("KS"))
    print("PN: ", count_inspections_for_inspector("PN"))
    print("SC: ", count_inspections_for_inspector("SC"))
    print("SP: ", count_inspections_for_inspector("SP"))


if __name__ == '__main__':
    main()
