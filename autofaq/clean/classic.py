from pandas import DataFrame

from autofaq.clean.cleaner import Cleaner
from autofaq.util.out import sprint


class ClassicCleaner(Cleaner):
    def clean(self, df: DataFrame, **kwargs):
        sprint("Filtering data using classic cleaner ...", fg="cyan")
        selection = df.a.apply(lambda x: type(x) == str and x.strip() != "")
        return selection
