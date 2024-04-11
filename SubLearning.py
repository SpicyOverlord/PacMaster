import pandas as pd
import tensorflow as tf
from pandas import DataFrame
from tensorflow.keras import layers, models, Input
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib



def createNormalizedDataSets(df: DataFrame):
    X = df.iloc[:, :-4].values  # Features: all columns except the last 4
    y = df.iloc[:, -4:].values  # Labels: the last 4 column

    print("\n----- INPUT -----")
    print(X[:3])
    print("\n----- OUTPUT -----")
    print(y[:3])

    # Normalize your features for better performance
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    print("\n----- NORMALIZED INPUT -----")
    print(X[:3])

    # Split the dataset into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test, scaler

def defineModel(df: DataFrame):
    inputShape = df.shape[1] - 4

    model = models.Sequential([
        Input(shape=(inputShape,)),
        layers.Dense(128, activation='relu'),
        layers.Dense(64, activation='relu'),
        layers.Dense(4, activation='softmax')
    ])

    # Compile the model
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    return model


def trainModel(model, X_train, y_train):
    return model.fit(X_train, y_train, epochs=40, batch_size=64, validation_split=0.2)


def testModel(model, X_test, y_test):
    test_loss, test_acc = model.evaluate(X_test, y_test)

    return test_loss, test_acc


if __name__ == '__main__':
    df_raw = pd.read_csv('Data/Over5Levels.csv')
    # shuffle rows
    df_raw = df_raw.sample(frac=1).reset_index(drop=True)

    X_train, X_test, y_train, y_test, scaler = createNormalizedDataSets(df_raw)

    model = defineModel(df_raw)
    model.summary()

    history = trainModel(model, X_train, y_train)

    test_loss, test_acc = testModel(model, X_test, y_test)
    print(f"Test Accuracy: {test_acc * 100:.2f}%")

    model.save('Models/Over5Levels.keras')
    joblib.dump(scaler, 'Models/scalerOver5Levels.save')



