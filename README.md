# UPAnnotation.py

Add columns with some useful UniProt information to a genes / transcripts table. 

## Arguments:

- positional arguments:
  - *dir* : path to the directory containing table (tsv or csv). Output table will be created in this directory as well;
  - *table_name* : input table name;
  - *output_name* : output table name;
  - *key* : name of the column, which contains name to retrieving information (for ex. gene name);
  - *category* : category is abbreviation for the UniProt database name. You can find the names list here: http://www.uniprot.org/help/programmatic_access#id_mapping_examples.

- optional arguments:
  - *-h, --help* : show help information and exit;
  - *--alt_key -ak* : alternative key allow to search in UniProt base by another name if the key name doesn't map anything. If you give the alternative key, you should give the alternative category as well (default: None);
  - *--alt_category -ac* : category of alternative key. Can be same as main category (default: None);
  - *--columns -c* : string with column names you wish to add to output table (for ex. ID,CC,LINK) in the order you want. (default: ID,LEN,AC,DE,CC,GO,LINK).
    - Avalible options:
    - **ID** : entry name of the sequence;
    - **LEN** : the length of the molecule (AA);
    - **AC** : accession number(s) associated with an entry;
    - **DE** : full name recommended by the UniProt consortium and a name used in biotechnological context (if exists);
    - **CC** : text comments on the entry (function, subunit, induction etc.);
    - **GO** : GO terms and annotations;
    - **LINK** : UniProt page adress with entry info.

## Usage example:
### Simple
`python upannotation.py /path/to/directory/ table.tsv output.tsv GENEID GENENAME`
### Specify alternative key, alternative category and columns
`python upannotation.py /path/to/directory/ table.tsv output.tsv GENEID GENENAME --alt_key TXNAME --alt_category ENSEMBLGENOME_TRS_ID --columns ID,GO,DE,LINK`

## To implement:
- [ ] brute-force category checker (if you don't know the category for sure)
- [ ] handle multiple mapping (let's say some gene name is mapped to several UniProt accessions, then you'll be able to specify some extra information (for example organism name) to map this gene name to only one accession)
