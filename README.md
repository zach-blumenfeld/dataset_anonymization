# Dataset Anonymization
Light set of tools for consistent dataset anonymization.

## What is Data Anonymization?
Data anonymization is a type of information sanitation whose intent is privacy protection. It is the process of removing and/or altering identifiable information in such a way that entities described in the data can no longer be identified, and in turn remain anonymous.[[1]](https://en.wikipedia.org/wiki/Data_anonymization)

__Disclaimer__: This package was created by a data scientist who does not specialize in data privacy or security.  This library is still in development phase. While unit tests have been validated and this library has been used in experimental capacity with success, it has not been robustly tested or rigorously analyzed against industry standards for privacy protection or security, nor has it been reviewed by such experts. Please be mindful and use intelligently. 

## Basic Design

There are two anonymization approaches and one hashing approach supported by this library. The anonymization approaches are designed with sole intent of protecting sensitive data while maintaining correlations for analytical purposes.  Anonymization is intended to make it as hard as possible to crack original source values or check for identifier existence in the data even in the even that the source anonymization code is spilled. Anonymization follows the following 5 rules:

1. __Duplicate Preserving__: For any two property values `i` and `j`, if `i==j`, then `a_i==a_j`  where `a_i` and 
`a_j`  are the anonymizations of `i` and `j` respectively.  This is necessary for maintaining connectivity across information for downstream analytics.
2. __Irreversible__: The anonymization is a one-way function. i.e. Given a property values `i` and anonymization `a_i`, there is no deterministic function `f` s.t. `f(a_i) = i` for all `i` in the source dataset. This rules out encryption algorithms.  
3. __Data Order Independent__: The anonymized values are not dependent on the physical ordering stored or loaded from the source dataset nor any natural ordering of the data, such as numeric, alphabetical, or via frequency counts of any columns in the datatable. 

4. __Data Value Independent__: Outside matching exact duplicates, the anonymized values are not a function the source values. As a result we can say that given a property values `i` and anonymization `a_i`, there is no deterministic function `f` s.t. `f(i) = a_i` for all `i` in the source dataset.
5. __Unreproducible__: Re-running the anonymization on the same dataset will produce different anonymized values each time. 

The hashing approaching (described more below) follows 1-3 above but NOT 4-5 and is designed for masking less sensitive join/relationship keys.


## Caveats
1. __Inferring Source Values Via Probability Mass__: Because of the need to preserve duplicates, users of the anonymized data can observe the relative frequency of different discrete values and how they correlate to other variables in the dataset.  In certain instances, this could give away details about the source data, particularly when combined with subject matter expertise.  For example, suppose this library is used to anonymize the names of retail businesses selling electronics in a specific geographical region. If a user has knowledge of market share distribution in that region, they may be able to guess the identity of the retails with high accuracy based off the frequency counts of the labels alone. It is the responsibility of the user to identify these risks and handle responsibly.
## Installation
`python -m pip install git+https://github.com/zach-blumenfeld/dataset_anonymization.git`

## Usage
### Anonymization
There are two anonymization approaches supported in this library. Each have two methods, one for application to lists, and another to pandas dataframe columns.

#### 1. `anonymize/anonymize_df_col` - "Identifier Anonymization"
This replaces source values with uuid4 values. Ideal for lists/dataframe columns with a high frequency of unique values, i.e. 'high cardinality', but still containing some duplicates. The uuids are randomly generated to the uuid4 spec for each unique value in the list/dataframe column. Duplicates are preserved. uuids are not great for human readability (128-bit values, often represented in hexidecimal format like so: `324f2e8d-01d5-47b7-b9a6-7f53c4a934bd` ), but they are cheap to generate and take up little space if kept in uuid or byte format. The process is random and unseeded so the anonymized values will be different on each run and therefore unreproducible. 

```
from dataset_anonymization import anonymize
print(anonymize(['hello','hello','world','world']))
```

output:
```
[UUID('0b687aec-fc70-43dc-b05b-55d6e42be4e7'), UUID('0b687aec-fc70-43dc-b05b-55d6e42be4e7'), UUID('105cf183-0a72-4848-b890-d4f0c7f940b9'), UUID('105cf183-0a72-4848-b890-d4f0c7f940b9')]
```

and for dataframes:
```
import pandas as pd
from dataset_anonymization import anonymize_df_col
import random
import string 

def random_string():
    return ''.join(random.choice(string.ascii_letters) for i in range(8))

strings = [random_string() for i in range(10)] * 2
strings.sort()

df = pd.DataFrame({'string': strings})

anonymize_df_col(df, 'string', replace=False, suffix = "_anonymized")

print(df)

```

output:
```
      string                     string_anonymized
0   AthGRzyG  80dd3746-9a49-40f8-b85f-d4eb7dbdb72f
1   AthGRzyG  80dd3746-9a49-40f8-b85f-d4eb7dbdb72f
2   NhMpMbAY  e2c24e57-94a2-485b-afde-f3fda9743946
3   NhMpMbAY  e2c24e57-94a2-485b-afde-f3fda9743946
4   SOTJqubp  9e646a37-e7fb-4a73-9764-deb814c2d800
5   SOTJqubp  9e646a37-e7fb-4a73-9764-deb814c2d800
...         ...         ...         ...         ...
14  hHtRgaDq  f3c1e826-1a1d-4f0e-8e3d-df09180d3b9a
15  hHtRgaDq  f3c1e826-1a1d-4f0e-8e3d-df09180d3b9a
16  vSZEvPaS  1b678bfd-bf57-40b5-bf02-4254c3509e87
17  vSZEvPaS  1b678bfd-bf57-40b5-bf02-4254c3509e87
18  xLFvxzUE  bbb2abba-4de2-4bdd-86e1-849c11e8a947
19  xLFvxzUE  bbb2abba-4de2-4bdd-86e1-849c11e8a947
```

#### 2. `anonymize_label/anonymize_df_label` - "Label Anonymization"
This replaces source values with enumerated, human-readable, labels. Intended for lists/dataframe columns with a relatively low frequency of unique values, i.e. 'low cardinality', such as sensitive type or category labels or where human readability post-anonymization is otherwise important such as with names or locations.  In theory there is no limit (beyond python internal hashtable implementation) on the number of unique values, however performance at higher cardinalities is not tested and may vary. The user can specify a prefix and postfix to alter the anonymized label which is formatted as `<prefix><enumeration number><postfix>`. The default is `prefix='TYPE_'` and `postfix=''`. The enumeration numbers start at 1 and go up to the number of unique source values. The mapping of the unique source values to enumeration numbers is random and unseeded.  As a result, just like `anonymize/anonymize_df_col` the anonymized values will be different on each run and therefore unreproducible while duplication between source values will always be preserved. 

```
from dataset_anonymization import anonymize_label
print(anonymize_label(['hello','hello','world','world'], prefix = 'TYPE_', postfix = ''))
```

output:
```
['TYPE_2', 'TYPE_2', 'TYPE_1', 'TYPE_1']
```

and for dataframes:
```
import pandas as pd
from dataset_anonymization import anonymize_df_label

names = ['Liam', 'Olivia', 'Noah', 'Emma','Oliver', 'Ava'] * 2
names.sort()

df = pd.DataFrame({'person_name': names})

anonymize_df_label(df, 'person_name', prefix = 'NAME_', postfix = '', replace=False, suffix = "_anonymized")

print(df)

```

output:
```
   person_name person_name_anonymized
0          Ava                 NAME_3
1          Ava                 NAME_3
2         Emma                 NAME_5
3         Emma                 NAME_5
4         Liam                 NAME_4
5         Liam                 NAME_4
6         Noah                 NAME_2
7         Noah                 NAME_2
8       Oliver                 NAME_1
9       Oliver                 NAME_1
10      Olivia                 NAME_6
11      Olivia                 NAME_6
```

### Hashing
There is currently one approach for hashing values implemented by `hash_key` for lists and `hash_df_key`: for dataframe columns. This replaces each source value with a hexidecimal string representation of a SHA-512 hash truncated to the first 128 bits.  The SHA-512 is calculated on string input obtained by converting the source value to a string and concatenated with a user supplied passphrase. This is ideal for dataframe columns that represent join/relationship keys across multiple different data tables where it is important that the anonymization is reproducible (i.e. each unique source value maps to the same hash every time it is run with the same passphrase) so that data tables can be anonymized in separate processes more efficiently.  This method is intended for use on less sensitive identifiers such as internal system-generated ids, that, with an abundance of caution, the user still wants to mask.  The passphrase argument is included in case the user wishes to hinder brute-force or precomputed table approaches to crack the source values.  In such cases the passphrase should not be shared.  **It should be re-iterated that this is NOT a suitable method for protecting PII or otherwise highly sensitive data, particularly those data with predictable formats such as (but not exclusive to) SSNs/tax Ids, geo-locations, and phone numbers**. 

```
from dataset_anonymization import hash_key
print(hash_key(['hello','hello','world','world'], passphrase='passphrase'))
```

output:
```
['b43b658cf6fbaefb0ac26d6ad9df4aaa', 'b43b658cf6fbaefb0ac26d6ad9df4aaa', '423c6bd491b6c467a6de8c1a69e262ae', '423c6bd491b6c467a6de8c1a69e262ae']
```

and for dataframes:
```
import pandas as pd
from dataset_anonymization import hash_df_key

ints= [random.choice(range(0,int(1e6))) for i in range(10)] * 2
ints.sort()

df = pd.DataFrame({'seq_id': ints})

hash_df_key(df, 'seq_id', 'passphrase', replace=False, suffix = "_anonymized")

print(df)

```

output:
```
    seq_id                 seq_id_anonymized
0    37890  257577b6db9a29515cceb2caec998a36
1    37890  257577b6db9a29515cceb2caec998a36
2    81345  65cc83f6e995d3b6b041d9717946b6be
3    81345  65cc83f6e995d3b6b041d9717946b6be
4   190412  f6299d117f6314973896bd05ecbf497f
5   190412  f6299d117f6314973896bd05ecbf497f
...         ...         ...         ...     
14  593134  0bcaa51b6c2563b4a3c034377bbabea4
15  593134  0bcaa51b6c2563b4a3c034377bbabea4
16  758211  d7cb2297c5a16232c1a60ae1d28cacaf
17  758211  d7cb2297c5a16232c1a60ae1d28cacaf
18  947806  5826080c6fae2c01098ef5836bd68f6f
19  947806  5826080c6fae2c01098ef5836bd68f6f
```