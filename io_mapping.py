import numpy as np
import pandas as pd
import sklearn.metrics


class InOutMapping:

    def __init__(self):
        self.binary_vars = {}
        self.expand_colnames = []

    def map_input(self, features, dummies):
        expand_features = pd.get_dummies(features, columns=dummies)
        for c in dummies:
            if features[c].nunique() == 2:
                self.binary_vars[c] = features[c].unique()
                # deleting one of the binary feature columns
                new_col = c + '_' + self.binary_vars[c][1]
                expand_features = expand_features.drop(columns=[new_col])

        # features = features.drop(columns=['sex_Male', 'Y_<=50K'])
        print(expand_features.shape)
        self.expand_colnames = expand_features.columns
        scaler = sklearn.preprocessing.StandardScaler()
        X_scaled = scaler.fit_transform(expand_features)
        X = X_scaled.astype(np.float32)
        print(X.shape)
        return X

    def map_output(self, X, dummies, threshold=1):
        # TODO have the threshold
        onehot_cols = []
        noncat_cols_idx = []
        noncat_cols = []
        for idx, c in enumerate(self.expand_colnames):
            if any(map(c.startswith, dummies)):
                onehot_cols.append(c) #TODO maybe I don't need this
            else:
                noncat_cols_idx.append(idx)
                noncat_cols.append(c)

        revert_df = pd.DataFrame(columns=dummies)
        for c in dummies:
            dummy_idx = [idx for idx, val in enumerate(self.expand_colnames) if val.startswith(c)]
            corresponding = X[:, dummy_idx]
            if c in self.binary_vars.keys():
                b0 = self.binary_vars[c][0]
                b1 = self.binary_vars[c][1]
                values = [b1 if val < 0.5 else b0 for val in corresponding]  # TODO we don't have 0 and 1
            else:
                m = np.zeros_like(corresponding)
                m[np.arange(len(corresponding)), corresponding.argmax(1)] = 1
                max_col = np.argmax(m, axis=1)
                values = [self.expand_colnames[i].replace(c + '_', '') for i in max_col]
            revert_df[c] = values

        res = pd.DataFrame(X[:, noncat_cols_idx], columns=noncat_cols)
        for c in dummies:
            res[c] = revert_df[c]
        return res
        # TODO assert values are close
        # TODO fix the binary values
        # TODO tartibe sotuna moheme?

        # columns = expanded_X.columns
        # for dummy in list_dummies:
        #     get the columns startring with that-
        #     get the max of those columns
