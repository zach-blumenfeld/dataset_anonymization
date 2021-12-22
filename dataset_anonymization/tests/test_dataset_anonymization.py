import unittest
import pandas as pd
import dataset_anonymization
import uuid
import string
import random

VEC_LENGTH = 100
LETTERS = string.ascii_letters
STRING_LENGTH = 8
COL_SUFFIX = '_anonymized'
INT_COL = 'ints'
STR_COL = 'strings'
SALT = 's0'
SALT_DICT = {INT_COL: 's1', STR_COL: 's2'}


def random_string():
    return ''.join(random.choice(LETTERS) for i in range(STRING_LENGTH))


def return_0():
    return 0


class TestBase(unittest.TestCase):
    def _test_uniqueness(self, pv):
        self.assertEqual(len(set(pv)), VEC_LENGTH)

    def _test_duplicate_preservation_in_doubled_vec(self, pv):
        self.assertEqual(len(set(pv)), VEC_LENGTH)
        for i in range(VEC_LENGTH):
            self.assertEqual(pv[i], pv[i + VEC_LENGTH])


class TestTruncHash(TestBase):

    def __test_uniqueness_and_duplicate_preservation(self, v):
        h1 = dataset_anonymization.trunc_hash(v, SALT)
        h2 = dataset_anonymization.trunc_hash(v, SALT)

        self._test_uniqueness(h1)
        self._test_duplicate_preservation_in_doubled_vec(h1 + h2)

    def test_uniqueness_and_duplicate_preservation_int(self):
        self.__test_uniqueness_and_duplicate_preservation([i for i in range(VEC_LENGTH)])

    def test_uniqueness_and_duplicate_preservation_str(self):
        self.__test_uniqueness_and_duplicate_preservation([random_string() for i in range(VEC_LENGTH)])

    def test_df_uniqueness_and_duplicate_preservation_int(self):
        df = pd.DataFrame({INT_COL: [i for i in range(VEC_LENGTH)],
                           STR_COL: [random_string() for i in range(VEC_LENGTH)]})

        df1 = df.copy()
        dataset_anonymization.trunc_hash_dataframe(df1, SALT_DICT)
        self._test_uniqueness(df1[INT_COL + COL_SUFFIX].tolist())
        self._test_uniqueness(df1[STR_COL + COL_SUFFIX].tolist())

        df2 = df.copy()
        dataset_anonymization.trunc_hash_dataframe(df2, SALT_DICT)
        df3 = pd.concat([df1, df2])
        self._test_duplicate_preservation_in_doubled_vec(df3[INT_COL + COL_SUFFIX].tolist())
        self._test_duplicate_preservation_in_doubled_vec(df3[STR_COL + COL_SUFFIX].tolist())

    def test_df_replace(self):
        df = pd.DataFrame({INT_COL: [i for i in range(VEC_LENGTH)],
                           STR_COL: [random_string() for i in range(VEC_LENGTH)]})

        dataset_anonymization.trunc_hash_dataframe(df, SALT_DICT, replace=True)
        self.assertEqual(sum(df[INT_COL].apply(len) == 32), VEC_LENGTH)
        self.assertEqual(sum(df[STR_COL].apply(len) == 32), VEC_LENGTH)


class TestAnonymization(TestBase):

    def __test_uniqueness_and_duplicate_preservation(self, v):
        self._test_uniqueness(dataset_anonymization.anonymize(v, uuid.uuid4))
        self._test_duplicate_preservation_in_doubled_vec(dataset_anonymization.anonymize_uuid(v + v))

    def test_uniqueness_and_duplicate_preservation_int(self):
        self.__test_uniqueness_and_duplicate_preservation([i for i in range(VEC_LENGTH)])

    def test_uniqueness_and_duplicate_preservation_str(self):
        self.__test_uniqueness_and_duplicate_preservation([random_string() for i in range(VEC_LENGTH)])

    def test_uuid_uniqueness_and_duplicate_preservation_int(self):
        v = [i for i in range(VEC_LENGTH)]
        self._test_uniqueness(dataset_anonymization.anonymize_uuid(v))
        self._test_duplicate_preservation_in_doubled_vec(dataset_anonymization.anonymize_uuid(v + v))

    def test_df_uniqueness_and_duplicate_preservation_int(self):
        df = pd.DataFrame({INT_COL: [i for i in range(VEC_LENGTH)],
                           STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        df1 = df.copy()
        dataset_anonymization.anonymize_dataframe(df1, {INT_COL: uuid.uuid4})
        self._test_uniqueness(df1[INT_COL + COL_SUFFIX].tolist())

        df2 = pd.concat([df.copy(), df.copy()])
        dataset_anonymization.anonymize_dataframe(df2, {INT_COL: uuid.uuid4})
        self._test_duplicate_preservation_in_doubled_vec(df2[INT_COL + COL_SUFFIX].tolist())

    def test_df_uuid_uniqueness_and_duplicate_preservation_int(self):
        df = pd.DataFrame({INT_COL: [i for i in range(VEC_LENGTH)],
                           STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        df1 = df.copy()
        dataset_anonymization.anonymize_dataframe_uuid(df1, [INT_COL, STR_COL])
        self._test_uniqueness(df1[INT_COL + COL_SUFFIX].tolist())
        self._test_uniqueness(df1[STR_COL + COL_SUFFIX].tolist())

        df2 = pd.concat([df.copy(), df.copy()])
        dataset_anonymization.anonymize_dataframe_uuid(df2, [INT_COL, STR_COL])
        self._test_duplicate_preservation_in_doubled_vec(df2[INT_COL + COL_SUFFIX].tolist())
        self._test_duplicate_preservation_in_doubled_vec(df2[STR_COL + COL_SUFFIX].tolist())

    def test_df_replace(self):
        df = pd.DataFrame({INT_COL: [i for i in range(VEC_LENGTH)],
                           STR_COL: [random_string() for i in range(VEC_LENGTH)]})

        dataset_anonymization.anonymize_dataframe(df, {STR_COL: return_0}, replace=True)
        self.assertEqual(sum(df[STR_COL] == 0), VEC_LENGTH)


if __name__ == '__main__':
    unittest.main()
