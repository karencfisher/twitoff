import numpy as np
from sklearn.metrics import accuracy_score


class LogRegression():
    def __init__(self, learn_rate, epochs, verbose=10):
        self.learn_rate = learn_rate
        self.epochs = epochs
        self.verbose = verbose

    def fit(self, X, Y):
        self.n = X.shape[0]
        self.m = X.shape[1]

        # Initialize weights, bias
        self.Weights = np.zeros((self.n, 1))
        self.bias = 0

        # Store scores across epochs
        self.train_losses = []
        self.train_accuracy = []
        
        # Iterate through the epochs
        for i in range(1, self.epochs + 1):
            # Forward/Back propagation one epoch
            loss, accuracy = self.__propagate(X, Y)

            # Store training scores
            self.train_losses.append(loss)
            self.train_accuracy.append(accuracy)

            # If verbose > 0, print every verbose epochs
            if self.verbose > 0 and i % self.verbose == 0:
                print(f'Epoch {i} Loss {loss} Accuracy {accuracy}')
                    
        return self
                
    def predict(self, X, y=None):
        m = X.shape[1]
        Y_prediction = np.zeros((1,m))

        A = self.__sigmoid(np.dot(self.Weights.T, X) + self.bias)
        for i in range(m):
            Y_prediction[0, i] = 1 if A[0, i] > 0.5 else 0
        return Y_prediction

    def __propagate(self, X, Y):
        # Forward propagate
        A = self.__sigmoid(np.dot(self.Weights.T, X) + self.bias)

        # Get loss and accuracy
        cost = self.__loss(Y, A)
        Y_prediction = np.zeros((1,self.m))
        for i in range(self.m):
            Y_prediction[0, i] = 1 if A[0, i] > 0.5 else 0
        accuracy = accuracy_score(Y[0], Y_prediction[0])

        # Back propagate
        dw = 1/self.m * np.dot(X, (A - Y).T)
        db = 1/self.m * np.sum(A - Y)

        # Update parameters
        self.Weights = self.Weights - self.learn_rate * dw
        self.bias = self.bias - self.learn_rate * db

        return cost, accuracy

    def __sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def __loss(self, Y, A):
        cost = -1/self.m * np.sum(np.dot(Y, np.log(A).T) + np.dot((1-Y), 
                                  np.log(1 - A).T))
        return np.squeeze(cost)
