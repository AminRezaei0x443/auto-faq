from pandas import DataFrame

from autofaq.clean.cleaner import Cleaner


class ClassicCleaner(Cleaner):
    def clean(self, df: DataFrame):
        selection = df.a.apply(lambda x: type(x) == str and x.strip() != "")
        return selection
