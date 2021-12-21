# Dataset Anonymization
Light set of tools for consistent dataset anonymization.

## What is Data Anonymization?
Data anonymization is a type of information sanitation whose intent is privacy protection. It is the process of 
removing and/or altering identifiable information in such a way that entities described in the data can no longer be 
identified, and in turn remain anonymous.[[1]](https://en.wikipedia.org/wiki/Data_anonymization)

## Basic Design
This packages targets the following behavior for anonymization.

1. __Unrelated to Original Property Values__: Unless otherwise defined by user, The anonymized values should *not* be a 
function of the original property values (as would be the case with hashing or encryption). Instead, the anonymized 
value should be randomly generated independent of the original property value. This makes the anonymization 
__irreversible__ and makes it much harder, if not virtually impossible, to back out original property values, even for
data types with very short predictable patterns, like tax ids, phone numbers, and ip addresses. 
2. __Maintain Exact Duplicates__: For any two property values `i` and `j`, if `i==j`, then `a_i==a_j`  where `a_i` and 
`a_j`  are the anonymizations of `i` and `j` respectively.  This is necessary for maintaining connectivity across information.  
4. __Not Replicable__:  This anonymization is designed to run over all the data at once in a batch like process
producing values in a stochastic and unseeded matter unless otherwise defined by the user.  As such, it will produce 
different anonymized values on each run in a random way. This is by design, as it makes it as difficult as possible to 
back-out or brute-force the original values, even if the users' anonymization source code is made publicly available.

## Usage
To use, simply do
```
import uuid
from dataset_anonymization import anonymize
print(anonymize(['hello','hello','world','world'], uuid.uuid4))
```
Output: (Exact uuid values will vary, but duplicates should be maintained) 
```
[UUID('0b687aec-fc70-43dc-b05b-55d6e42be4e7'), UUID('0b687aec-fc70-43dc-b05b-55d6e42be4e7'), UUID('105cf183-0a72-4848-b890-d4f0c7f940b9'), UUID('105cf183-0a72-4848-b890-d4f0c7f940b9')]
```

You can also mutate dataframes by column.  For example:

```
import pandas as pd
import uuid
from dataset_anonymization import anonymize_dataframe
import random
import string 

def random_string():
    return ''.join(random.choice(string.ascii_letters) for i in range(8))

ints = [i for i in range(10)] * 2
ints.sort()

strings = [random_string() for i in range(10)] * 2
strings.sort()

df = pd.DataFrame({'ints': ints, 'string': strings})

anonymize_dataframe(df, {'ints': uuid.uuid4, 'string': uuid.uuid4})

print(df)

```

Output:
```
    ints    string                       ints_anonymized                     string_anonymized
0      0  DUvhmXhn  24c1e11d-c6f2-4211-8eff-dee831094754  247bace5-9ebd-44a3-830a-88309d8b875c
1      0  DUvhmXhn  24c1e11d-c6f2-4211-8eff-dee831094754  247bace5-9ebd-44a3-830a-88309d8b875c
2      1  DnLFfHky  c78dfb18-ce9e-4e20-bf2b-c47ac30b3985  8dd57b0a-04a8-452b-91e8-757fc4dd13ee
3      1  DnLFfHky  c78dfb18-ce9e-4e20-bf2b-c47ac30b3985  8dd57b0a-04a8-452b-91e8-757fc4dd13ee
4      2  HLPMJTFy  feee02e9-5174-443d-99fc-a03ba5ed88bc  c3da24aa-eba4-431f-b5bb-8c09023231e4
5      2  HLPMJTFy  feee02e9-5174-443d-99fc-a03ba5ed88bc  c3da24aa-eba4-431f-b5bb-8c09023231e4
...         ...         ...         ...         ...             ...         ...         ...
14     7  sxABGRLJ  3efd572f-37ad-41f2-86ff-d5341e03e691  3cee402a-7ccf-4b7f-9385-fa5b5aac44a4
15     7  sxABGRLJ  3efd572f-37ad-41f2-86ff-d5341e03e691  3cee402a-7ccf-4b7f-9385-fa5b5aac44a4
16     8  wGXJHAFV  4e53b095-cd3e-462f-afe5-b27c68861bba  2845295b-8362-4f8c-880a-4c3a7114c269
17     8  wGXJHAFV  4e53b095-cd3e-462f-afe5-b27c68861bba  2845295b-8362-4f8c-880a-4c3a7114c269
18     9  wPhvPgTb  b567260c-57d9-4ad9-9d80-b73b3a1b6ff2  cad2019a-e6ea-40ac-bc68-279151224834
19     9  wPhvPgTb  b567260c-57d9-4ad9-9d80-b73b3a1b6ff2  cad2019a-e6ea-40ac-bc68-279151224834

```

The above use uuid.uuid4() as the `generate` argument, but you can really use any function you want, 
including other random generators or `Faker` type methods.  Just be careful with the choice.  Beware of generator
properties like sufficient randomness to avoid collisions, and/or, if you are tracking state with another class, that you 
aren't unintentionally using a pattern that exposes the original property values. 

Unless you seek human-readable anonymization values or something else specific, I recommend using `uuid4`. There exist 
`anonymize_uuid` and `anonymize_dataframe_uuid` that just use `uuid.uuid4()` so you do not have to pass a `generate`
callable argument. i.e.
```
from dataset_anonymization import anonymize_uuid
print(anonymize_uuid(['hello','hello','world','world']))
```
Output:
```\
[UUID('ea008361-bdaf-4b50-8877-10c8b6045d06'), UUID('ea008361-bdaf-4b50-8877-10c8b6045d06'), UUID('8dcc1f94-d42c-46b1-bec3-23a867566ddb'), UUID('8dcc1f94-d42c-46b1-bec3-23a867566ddb')]

```
and

```
import pandas as pd
import uuid
from dataset_anonymization import anonymize_dataframe_uuid
import random
import string 

def random_string():
    return ''.join(random.choice(string.ascii_letters) for i in range(8))

ints = [i for i in range(10)] * 2
ints.sort()

strings = [random_string() for i in range(10)] * 2
strings.sort()

df = pd.DataFrame({'ints': ints, 'string': strings})

anonymize_dataframe_uuid(df, ['ints', 'string'])

print(df)

```

Output:
```
    ints    string                       ints_anonymized                     string_anonymized
0      0  LBqYZful  c7cccc17-f6e6-4ce8-aa3b-23f49edc5e32  f8437f5a-3ece-4c26-8900-4ced1e80c5a8
1      0  LBqYZful  c7cccc17-f6e6-4ce8-aa3b-23f49edc5e32  f8437f5a-3ece-4c26-8900-4ced1e80c5a8
2      1  LhBSMPvX  2eb7682d-c302-481b-aada-ad4edfb19f95  dcbb9274-3463-4bf6-ad74-c604a12614f6
3      1  LhBSMPvX  2eb7682d-c302-481b-aada-ad4edfb19f95  dcbb9274-3463-4bf6-ad74-c604a12614f6
4      2  LxmmfQlf  7c56c661-035b-4540-a94e-22b83e5f4f76  b44eb000-68d1-44df-9190-252bada177e0
5      2  LxmmfQlf  7c56c661-035b-4540-a94e-22b83e5f4f76  b44eb000-68d1-44df-9190-252bada177e0
...         ...         ...         ...         ...             ...         ...         ...
14     7  rDzrXIrk  2278139d-acdf-421a-9135-0ad47cf026c8  25a87660-9e87-48fd-a1a4-e5be6ccd74a9
15     7  rDzrXIrk  2278139d-acdf-421a-9135-0ad47cf026c8  25a87660-9e87-48fd-a1a4-e5be6ccd74a9
16     8  syItQmoP  3b2d822d-9674-42cb-9bed-7f8a6d35e2dc  9942d2db-0e30-46a7-a053-7ae59b5f9cb3
17     8  syItQmoP  3b2d822d-9674-42cb-9bed-7f8a6d35e2dc  9942d2db-0e30-46a7-a053-7ae59b5f9cb3
18     9  wXBxwLiy  8fa26883-808c-418e-9cc9-8605c511228c  58c080db-ba2d-46f3-bfa8-59e9ccc57538
19     9  wXBxwLiy  8fa26883-808c-418e-9cc9-8605c511228c  58c080db-ba2d-46f3-bfa8-59e9ccc57538

```