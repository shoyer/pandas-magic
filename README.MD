pandas-magic
############

pandas-magic introduces argumentless `lambda` function ("thunks") to copy the chaining magic of R's dplyr with pandas.

Example
-------

    import pandas as pd
    import pandas_magic.monkeypatched

    (df.magic[lambda: sepal_length > 3]
             .groupby(lambda: pd.cut(sepal_width, 5))
             .apply(lambda: petal_width.mean()))

    isinstance(df.magic, pd.DataFrame) # True

License
-------

MIT
