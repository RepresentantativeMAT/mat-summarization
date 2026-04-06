from model import Feature
from method.MATSummarize import MATSummarize

class MATSGF(MATSummarize):
    def __init__(self, trc, trv, path, features: list[Feature] = None):
        super.__init__(trc, trv, path)

    def load(self, path, ignore_columns=None, force_cat_columns=None, values_null=None):
        return super().load(path, ignore_columns, force_cat_columns, values_null)