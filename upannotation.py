import urllib
import urllib2
import csv
import sys
import argparse


def get_full_info(query, f, t='ACC', form='txt'):

    url = 'http://www.uniprot.org/mapping/'

    params = {
        'from': f,
        'to': t,
        'format': form,
        'query': query
    }

    data = urllib.urlencode(params)
    request = urllib2.Request(url, data)
    try:
        response = urllib2.urlopen(request)
        page = response.read()
        return page
    # try twice before give up
    except urllib2.HTTPError:
        try:
            response = urllib2.urlopen(request)
            page = response.read()
            return page
        except urllib2.HTTPError as e:
            print e.code
            print e.read
            return None


def get_entry_name(full_info):

    # return entry name of the sequence
    return full_info.splitlines()[0].split()[1]


def get_molecule_length(full_info):

    # return the length of the molecule (AA)
    return full_info.splitlines()[0].split()[3]


def get_accession_number(full_info):

    # return accession number(s) associated with an entry
    ac = ''
    for line in full_info.splitlines():
        if line.split()[0] == 'AC':
            ac += ' '.join(line.replace('AC ', '').split())
    return ac


def get_description(full_info):

    # return the full name recommended by the UniProt consortium
    # and a name used in biotechnological context (if exists)
    de = ''
    for line in full_info.splitlines():
        if line.split()[0] == 'DE':
            if line.split()[1] == 'RecName:':
                if line.split()[2].split('=')[0] == 'Full':
                    de += line.split('=')[1]

            if line.split()[1] == 'AltName:':
                if line.split()[2].split('=')[0] == 'Biotech':
                    de += 'BioTech = ' + line.split('=')[1]
    return de


def get_comments(full_info):

    # return text comments on the entry (function, subunit, induction etc.)
    comment_lines = [line for line in full_info.splitlines() if line.split()[0] == 'CC']
    comments = ''
    for line in comment_lines:
        if '------' in line:
            break

        if line.split()[1] == '-!-':
            comments += line.split('-!-')[1].lstrip() + ' '
        else:
            comments += line.split('CC')[1].lstrip() + ' '
    return comments


def get_link(ac):

    # return UniProt page adress with entry info
    return 'http://www.uniprot.org/uniprot/' + ac.split(';')[0]


def get_gene_ontology(full_info):

    # return GO annotations
    go_lines = [line for line in full_info.splitlines() if line.split()[0] == 'DR' and line.split()[1] == 'GO;']
    go = ''
    for line in go_lines:
        go += line.split('GO; ')[1] + ' '
    return go


def extend_table(**kwargs):

    table_path = kwargs.get("dir")
    table_name = kwargs.get("table_name")
    output_table = kwargs.get("output_name")
    table = open(table_path + table_name, 'r')
    dialect = csv.Sniffer().sniff(table.read(1024))  # copy the input table dialect
    table.seek(0)
    table = csv.reader(table, dialect)
    output_table = csv.writer(open(table_path + output_table, 'w'), dialect,
                              quoting=csv.QUOTE_NONNUMERIC, doublequote=True)

    # obtain the key and alt_key column number
    header = table.next()

    key = kwargs.get("key")
    category = kwargs.get("category")
    try:
        header.index(key)
    except ValueError:
        sys.exit("Can't find column named " + key + " in input table")

    key_index = header.index(key)

    alt_key = kwargs.get("alt_key")
    alt_category = kwargs.get("alt_category")
    if alt_key:
        if not alt_category:
            sys.exit('Please provide alternative category')
        try:
            header.index(alt_key)
            alt_index = header.index(alt_key)
        except ValueError:
            print "Can't find column named " + alt_key + " in input table"

    # write new header
    columns = kwargs.get("columns").split(',')
    col_names = {'ID': 'ID', 'LEN': 'Length (AA)', 'AC': 'Accession number(s)',
                 'DE': 'Description', 'CC': 'Comments', 'GO': 'GO', 'LINK': 'UniProt page'}
    columns = [col for n, col in enumerate(columns) if col not in columns[:n]]  # remove duplicates from columns list
    col_exec = {'ID': 'extension.append(get_entry_name(full_info))',
                'LEN': 'extension.append(get_molecule_length(full_info))',
                'AC': 'extension.append(get_accession_number(full_info))',
                'DE': 'extension.append(get_description(full_info))',
                'CC': 'extension.append(get_comments(full_info))',
                'GO': 'extension.append(get_gene_ontology(full_info))',
                'LINK': 'extension.append(get_link(get_accession_number(full_info)))'}
    order = []

    for col in columns:
        try:
            header.append(col_names[col])
            order.append(col)
        except KeyError:
            sys.exit("Possible column names are ID, LEN, AC, DE, CC, GO, LINK")

    output_table.writerow(header)

    # write the output table
    for row in table:
        mapping_succeed = True
        full_info = get_full_info(row[key_index], f=category)  # mapping function

        if not full_info and alt_key:  # if didn't map, try alternative key and category
            full_info = get_full_info(row[alt_index], f=alt_category)
            if not full_info:  # if it didn't help, go to next row
                mapping_succeed = False
        elif not full_info:
            mapping_succeed = False

        if mapping_succeed:  # if the mapping function found an entry in UniProt DB:
            extension = []
            for col in order:
                exec col_exec[col]
            output_table.writerow(row + extension)

        else:
            if alt_key:
                error_mesage = "ERROR: unable to map " + row[key_index] + " or " \
                               + row[alt_index] + " to any protein in UniProt DB"
            else:
                error_mesage = "ERROR: unable to map " + row[key_index] + " to any protein in UniProt DB"
            output_table.writerow(row + [error_mesage])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Add UniProt annotations to table.',
                                     epilog='Usage example:\npython annotation.py /path/to/directory/ \ \n'
                                            'table.tsv \ \n'
                                            'output.tsv \ \n'
                                            'GENEID GENENAME \ \n'
                                            '--alt_key TXNAME --alt_category ENSEMBLGENOME_TRS_ID \ \n'
                                            '--columns ID,GO,DE,LINK')
    parser.add_argument('dir', help='Path to the directory containing table.\n'
                                    'Output table will be created in this directory as well.')
    parser.add_argument('table_name', help='Original table name')
    parser.add_argument('output_name', help='Output table name')
    parser.add_argument('key', help='Name of the column, which contains name\n'
                                    'to retrieving information (for ex. gene name).')
    parser.add_argument('category', help='Category is abbreviation for the UniProt database name.\n'
                                         'Names: http://www.uniprot.org/help/programmatic_access#id_mapping_examples')
    parser.add_argument('--alt_key', metavar='-ak', default=None,
                        help="Alternative key allow to search in UniProt base by another name\n"
                             "in case the key name doesn't map anything. Need both alternative key\n"
                             "and alternative category to work (default: %(default)s)")
    parser.add_argument('--alt_category', metavar='-ac', default=None,
                        help="Category of alternative key. (default: %(default)s)")
    parser.add_argument('--columns', metavar='-c', default='ID,LEN,AC,DE,CC,GO,LINK',
                        help="String with column names you wish to add to output table\n"
                             "(for ex. ID,CC,LINK) in the order.\n"
                             "\tAvalible options:\n"
                             "\tID:\tentry name of the sequence\n"
                             "\tLEN:\tthe length of the molecule (AA)\n"
                             "\tAC\taccession number(s) associated with an entry\n"
                             "\tDE\tfull name recommended by the UniProt consortium and a name used\n"
                             "\t\tin biotechnological context (if exists)\n"
                             "\tCC\ttext comments on the entry (function, subunit, induction etc.)\n"
                             "\tGO\tGO annotations\n"
                             "\tLINK\tUniProt page adress with entry info\n"
                             "\tdefault: %(default)s")
    args = vars(parser.parse_args())
    extend_table(**args)
