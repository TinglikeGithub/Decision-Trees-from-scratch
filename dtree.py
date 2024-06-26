import numpy as np
from scipy import stats
from sklearn.metrics import r2_score, accuracy_score

class DecisionNode:
    def __init__(self, col, split, lchild, rchild):
        self.col = col
        self.split = split
        self.lchild = lchild
        self.rchild = rchild

    def predict(self, x_test):
        # Make decision based upon x_test[col] and split
        if x_test[self.col] < self.split:
            return self.lchild.predict(x_test)
        else:
            return self.rchild.predict(x_test)


class LeafNode:
    def __init__(self, y, prediction):
        "Create leaf node from y values and prediction; prediction is mean(y) or mode(y)"
        self.n = len(y)
        self.prediction = prediction

    def predict(self, x_test):
        return self.prediction


def gini(x):
    """
    Return the gini impurity score for values in y
    Assume y can be any number of classes >= 2
    Gini = 1 - sum_i p_i^2 where p_i is the proportion of class i in y
    """
    counts, bins = np.histogram(x)
    p = counts / len(x)
    return 1 - np.sum(p**2)


    
def find_best_split(X, y, loss, min_samples_leaf):
    n, p = X.shape
    k=11
    best_feature = -1
    best_split = -1
    best_loss = loss(y)

    for i in range(p): # loop through all features
        candidates = np.random.choice(n, k)  # choose k split points from all points 
        
        for split_i in candidates:
            split = X[split_i, i]
            yl = y[X[:, i] < split]
            yr = y[X[:, i] >= split]
            
            if len(yl) < min_samples_leaf or len(yr) < min_samples_leaf:
                continue
            
            # weighted loss of 2 child nodes
            l = (len(yl) * loss(yl) + len(yr) * loss(yr))/(len(yl)+len(yr)) 
            
            if l == 0:
                return i, split
            # choose the min loss as split point
            if l < best_loss: 
                best_feature = i
                best_split = split
                best_loss = l
                
    return best_feature, best_split    
    
    
class DecisionTree:
    def __init__(self, min_samples_leaf=1, loss=None):
        self.min_samples_leaf = min_samples_leaf
        self.loss = loss # loss function
        
    def fit(self, X, y):
        """
        Create a decision tree fit to (X,y) and save as self.root, the root of
        our decision tree, for  either a classifier or regression.  Leaf nodes for classifiers
        predict the most common class (the mode) and regressions predict the average y
        for observations in that leaf.

        This function is a wrapper around fit_() that just stores the tree in self.root.
        """
        self.root = self.fit_(X, y)


    def fit_(self, X, y):
        """
        Recursively create and return a decision tree fit to (X,y) for
        either a classification or regression.  This function should call self.create_leaf(X,y)
        to create the appropriate leaf node, which will invoke either
        RegressionTree621.create_leaf() or ClassifierTree621.create_leaf() depending
        on the type of self.

        This function is not part of the class "interface" and is for internal use, but it
        embodies the decision tree fitting algorithm.

        (Make sure to call fit_() not fit() recursively.)
        """
        if len(y) <= self.min_samples_leaf or len(np.unique(y))==1: # if one x value, make leaf node
            return self.create_leaf(y)
        
        col,split = find_best_split(X, y, self.loss, self.min_samples_leaf)
        
        if col == -1:
            return self.create_leaf(y)
        
        lchild = self.fit_(X[X[:, col] < split], y[X[:, col] < split])
        rchild = self.fit_(X[X[:, col] >= split], y[X[:, col] >= split]) 

        return DecisionNode(col, split, lchild, rchild)

    def predict(self, X_test):
        """
        Make a prediction for each record in X_test and return as array.
        This method is inherited by RegressionTree621 and ClassifierTree621 and
        works for both without modification!
        """
        predictions = list()

        for item in X_test:
            pred = self.root.predict(item)
            predictions.append(pred)

        return predictions


class RegressionTree(DecisionTree):
    def __init__(self, min_samples_leaf=1):
        super().__init__(min_samples_leaf, loss=np.var)

    def score(self, X_test, y_test):
        # Return the R^2 of y_test vs predictions for each record in X_test
        predictions = self.predict(X_test)
        return r2_score(y_test, predictions)

    def create_leaf(self, y):
        """
        Return a new LeafNode for regression, passing y and mean(y) to
        the LeafNode constructor.
        """
        return LeafNode(y, np.mean(y))


class ClassifierTree(DecisionTree):
    def __init__(self, min_samples_leaf=1):
        super().__init__(min_samples_leaf, loss=gini)

    def score(self, X_test, y_test):
        # Return the accuracy_score() of y_test vs predictions for each record in X_test
        predictions = self.predict(X_test)
        return accuracy_score(y_test, predictions)
        

    def create_leaf(self, y):
        """
        Return a new LeafNode for classification, passing y and mode(y) to
        the LeafNode constructor. Feel free to use scipy.stats to use the mode function.
        """
        mode_value = stats.mode(y, keepdims=True)[0][0]
        return LeafNode(y, mode_value)
