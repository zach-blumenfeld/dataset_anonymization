import unittest
import pandas as pd
import dataset_anonymization
import uuid
import string
import random

VEC_LENGTH = 100
INT_VEC = [i for i in range(VEC_LENGTH)]
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
    def _test_uniqueness(self, v):
        self.assertEqual(len(set(v)), VEC_LENGTH)

    def _test_duplicate_preservation_in_doubled_vec(self, v):
        self.assertEqual(len(set(v)), VEC_LENGTH)
        for i in range(VEC_LENGTH):
            self.assertEqual(v[i], v[i + VEC_LENGTH])
    
    def _test_none_equal(self, v1, v2):
        for i in range(VEC_LENGTH):
            self.assertNotEqual(v1, v2)


class TestHashKey(TestBase):

    def test_uniqueness_int(self):
        self._test_uniqueness(dataset_anonymization.hash_key(INT_VEC, SALT))

    def test_duplicate_preservation_int(self):
        self._test_duplicate_preservation_in_doubled_vec(dataset_anonymization.hash_key(INT_VEC, SALT) +
                                                         dataset_anonymization.hash_key(INT_VEC, SALT))

    def test_uniqueness_str(self):
        self._test_uniqueness(dataset_anonymization.hash_key([random_string() for i in range(VEC_LENGTH)], SALT))

    def test_duplicate_preservation_str(self):
        v = [random_string() for i in range(VEC_LENGTH)]
        self._test_duplicate_preservation_in_doubled_vec(dataset_anonymization.hash_key(v, SALT) +
                                                         dataset_anonymization.hash_key(v, SALT))

    def test_df_uniqueness(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        dataset_anonymization.hash_df_key(df, INT_COL, SALT)
        dataset_anonymization.hash_df_key(df, STR_COL, SALT)
        self._test_uniqueness(df[INT_COL + COL_SUFFIX].tolist())
        self._test_uniqueness(df[STR_COL + COL_SUFFIX].tolist())

    def test_df_duplicate_preservation(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})

        df1 = df.copy()
        dataset_anonymization.hash_df_key(df1, INT_COL, SALT)
        dataset_anonymization.hash_df_key(df1, STR_COL, SALT)
        df2 = df.copy()
        dataset_anonymization.hash_df_key(df2, INT_COL, SALT)
        dataset_anonymization.hash_df_key(df2, STR_COL, SALT)
        df3 = pd.concat([df1, df2])
        self._test_duplicate_preservation_in_doubled_vec(df3[INT_COL + COL_SUFFIX].tolist())
        self._test_duplicate_preservation_in_doubled_vec(df3[STR_COL + COL_SUFFIX].tolist())

    def test_df_replace(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        dataset_anonymization.hash_df_key(df, INT_COL, SALT, replace=True)
        dataset_anonymization.hash_df_key(df, STR_COL, SALT, replace=True)
        self.assertEqual(sum(df[INT_COL].apply(len) == 32), VEC_LENGTH)
        self.assertEqual(sum(df[STR_COL].apply(len) == 32), VEC_LENGTH)


class TestAnonymize(TestBase):

    def test_uniqueness_int(self):
        self._test_uniqueness(dataset_anonymization.anonymize(INT_VEC))

    def test_unrepeatability_int(self):
        self._test_none_equal(dataset_anonymization.anonymize(INT_VEC), dataset_anonymization.anonymize(INT_VEC))

    def test_duplicate_preservation_int(self):
        self._test_duplicate_preservation_in_doubled_vec(dataset_anonymization.anonymize(INT_VEC + INT_VEC))

    def test_uniqueness_str(self):
        self._test_uniqueness(dataset_anonymization.anonymize([random_string() for i in range(VEC_LENGTH)]))

    def test_unrepeatability_str(self):
        v = [random_string() for i in range(VEC_LENGTH)]
        self._test_none_equal(dataset_anonymization.anonymize(v), dataset_anonymization.anonymize(v))

    def test_duplicate_preservation_str(self):
        v = [random_string() for i in range(VEC_LENGTH)]
        self._test_duplicate_preservation_in_doubled_vec(dataset_anonymization.anonymize(v + v))

    def test_df_uniqueness_int(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        dataset_anonymization.anonymize_df_col(df, INT_COL)
        self._test_uniqueness(df[INT_COL + COL_SUFFIX].tolist())

    def test_df_unrepeatability_int(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        df2 = df.copy()
        df3 = df.copy()
        dataset_anonymization.anonymize_df_col(df2, INT_COL)
        dataset_anonymization.anonymize_df_col(df3, INT_COL)
        self._test_none_equal(df2[INT_COL + COL_SUFFIX].tolist(), df3[INT_COL + COL_SUFFIX].tolist())

    def test_df_duplicate_preservation_int(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        df2 = pd.concat([df.copy(), df.copy()])
        dataset_anonymization.anonymize_df_col(df2, INT_COL)
        self._test_duplicate_preservation_in_doubled_vec(df2[INT_COL + COL_SUFFIX].tolist())

    def test_df_replace(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        dataset_anonymization.anonymize_df_col(df, STR_COL, replace=True)
        self.assertEqual(type(df.loc[0, STR_COL]), uuid.UUID)


class TestAnonymizeCategory(TestBase):

    def test_uniqueness_int(self):
        self._test_uniqueness(dataset_anonymization.anonymize_category(INT_VEC))

    def test_unrepeatability_int(self):
        self._test_none_equal(dataset_anonymization.anonymize_category(INT_VEC),
                              dataset_anonymization.anonymize_category(INT_VEC))

    def test_duplicate_preservation_int(self):
        self._test_duplicate_preservation_in_doubled_vec(dataset_anonymization.anonymize_category(INT_VEC + INT_VEC))

    def test_uniqueness_str(self):
        self._test_uniqueness(dataset_anonymization.anonymize_category([random_string() for i in range(VEC_LENGTH)]))

    def test_unrepeatability_str(self):
        v = [random_string() for i in range(VEC_LENGTH)]
        self._test_none_equal(dataset_anonymization.anonymize_category(v), dataset_anonymization.anonymize_category(v))

    def test_duplicate_preservation_str(self):
        v = [random_string() for i in range(VEC_LENGTH)]
        self._test_duplicate_preservation_in_doubled_vec(dataset_anonymization.anonymize_category(v + v))

    def test_df_uniqueness_int(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        dataset_anonymization.anonymize_df_category(df, INT_COL)
        self._test_uniqueness(df[INT_COL + COL_SUFFIX].tolist())

    def test_df_unrepeatability_int(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        df2 = df.copy()
        df3 = df.copy()
        dataset_anonymization.anonymize_df_category(df2, INT_COL)
        dataset_anonymization.anonymize_df_category(df3, INT_COL)
        self._test_none_equal(df2[INT_COL + COL_SUFFIX].tolist(), df3[INT_COL + COL_SUFFIX].tolist())

    def test_df_duplicate_preservation_int(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        df2 = pd.concat([df.copy(), df.copy()])
        dataset_anonymization.anonymize_df_category(df2, INT_COL)
        self._test_duplicate_preservation_in_doubled_vec(df2[INT_COL + COL_SUFFIX].tolist())

    def test_df_replace(self):
        df = pd.DataFrame({INT_COL: INT_VEC, STR_COL: [random_string() for i in range(VEC_LENGTH)]})
        dataset_anonymization.anonymize_df_category(df, INT_COL, replace=True)
        self.assertEqual(type(df.loc[0, STR_COL]), str)


if __name__ == '__main__':
    unittest.main()
