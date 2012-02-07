import csv
import ast

def read_table_raw(filename, delimiter='\t'):
    table = []
    with open(filename) as f:
        reader = csv.reader(f, delimiter=delimiter, quoting=csv.QUOTE_NONE)
        for row in reader:
            table.append(row)
    return table


def convert_cell(cell):
    # see http://www.python.org/dev/peps/pep-0754/
    nan = float('nan')
    if cell == '':
        return None
    elif cell == 'nan':
        return nan
    else:
        return ast.literal_eval(cell)
		
def read_table(filename, delimiter='\t'):
    table = read_table_raw(filename, delimiter)
    table = list(zip(*table))
    dict = {}
    for col in table:
        dict[col[0]] = [convert_cell(cell) for cell in col[1:]]
    return dict


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:	   
        filename = sys.argv[1]
    else:
        filename = 'read_table_testdata.csv'
    m = read_table(filename)
    print(m)
    print("Entry D:", m['D'])




