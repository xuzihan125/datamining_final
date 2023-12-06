import os
import time

import numpy as np
from tqdm import tqdm
from gather_data import load_file
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from scipy.sparse.linalg import svds

comment_file_path = "comment/"


def parese():
    files = os.listdir(comment_file_path)
    user = dict()
    result = []
    for file in tqdm(files):
        data = load_file(file, dir=comment_file_path)
        comments = data["comment"]
        for comment in comments:
            user_id = comment["user_id"]
            if user_id not in user:
                user[user_id] = 1
            else:
                user[user_id] += 1
            rate = comment["rating"]
            rate = comment["rating"]
            wine_id = data["id"]
            result.append([user_id, wine_id, rate])
    print("total user:{0}, total wine:{1}, total rate:{2}".format(len(user), len(files), len(result)))
    with open("user_wine_rate.json", "w") as f:
        json.dump(result, f)


def load_data():
    return load_file("user_wine_rate.json", dir="")

def write_json(data, file_name, dir=""):
    with open(dir+file_name, "w") as f:
        json.dump(data, f)

def predict_SVD(data, k_singular_value=2, load=False):
    if not load:
        U, s, Vt = svds(data, k_singular_value)
        np.save("U.npy", U)
        np.save("s.npy", s)
        np.save("Vt.npy", Vt)
    U=np.load("U.npy")
    s=np.load("s.npy")
    Vt=np.load("Vt.npy")
    reconstructed_matrix = U.dot(np.diag(s)).dot(Vt)
    return reconstructed_matrix


def predict(matrix, point, count_wine):
    print("get prediction by SVD")
    predict = []
    actual = []
    for data in tqdm(point):
        predict.append(matrix[user[data[0]], wine[data[1]]] + count_wine[wine[data[1]]])
        actual.append(data[2])
    return predict, actual

def score(predict, label):

    return mean_squared_error(label, predict, squared=False  )

def SVD(train, test, count_wine, size=30, step=1, file_name="svd_score.json", dir="", param_file="./factor/"):
    print("matrix building")
    matrix = np.zeros((number_of_user, number_of_wine))
    train, test = train_test_split(data, test_size=0.1, random_state=0)
    for rate in tqdm(train):
        matrix[user[rate[0]], wine[rate[1]]] = rate[2] - count_wine[wine[rate[1]]]

    result = dict()
    if os.path.exists(file_name):
        result = load_file(file_name, dir=dir)

    for i in range(1, size + 1, step):
        start = time.time()
        if str(i) not in result:
            model = predict_SVD(matrix, k_singular_value=i, load=False)
            predict_value, label = predict(model, test, count_wine)
            SVD_score = score(predict_value, label)
            result[str(i)] = SVD_score
        end = time.time()
        print(
            "RMSE by SCV:{0} with used singular value:{1}, calculation time:{2}".format(result[str(i)], i, end - start))
        write_json(result, file_name)

def decompose(matrix):
    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
    np.savetxt("U.npy", U)
    np.savetxt("s.npy", s)
    np.savetxt("Vt.npy", Vt)
    return U, s, Vt

def load_and_parse(min_size=4):
    data = load_data()
    user = dict()
    wine = dict()
    print("initialization")
    count = dict()
    for rate in tqdm(data):
        if rate[0] not in count:
            count[rate[0]] = 1
        else:
            count[rate[0]] += 1

    filtered_data = []
    count_wine = dict()
    count_w = dict()
    count_display = dict()
    for rate in tqdm(data):
        if count[rate[0]] <= min_size:
            continue
        if count[rate[0]] not in count_display:
            count_display[count[rate[0]]] = 0
        count_display[count[rate[0]]] += 1
        filtered_data.append(rate)
        if rate[0] not in user:
            user[rate[0]] = len(user)
        if rate[1] not in wine:
            wine[rate[1]] = len(wine)
            count_w[wine[rate[1]]] = 0
            count_wine[wine[rate[1]]] = 0
        count_wine[wine[rate[1]]] += rate[2]
        count_w[wine[rate[1]]] += 1

    return filtered_data


if __name__ == "__main__":
    data = load_data()
    user = dict()
    wine = dict()
    print("initialization")
    count = dict()
    for rate in tqdm(data):
        if rate[0] not in count:
            count[rate[0]] = 1
        else:
            count[rate[0]] += 1

    filtered_data = []
    count_wine = dict()
    count_w = dict()
    count_display = dict()
    for rate in tqdm(data):
        if count[rate[0]] <= 2:
            continue
        if count[rate[0]] not in count_display:
            count_display[count[rate[0]]] = 0
        count_display[count[rate[0]]] += 1
        filtered_data.append(rate)
        if rate[0] not in user:
            user[rate[0]] = len(user)
        if rate[1] not in wine:
            wine[rate[1]] = len(wine)
            count_w[wine[rate[1]]] = 0
            count_wine[wine[rate[1]]] = 0
        count_wine[wine[rate[1]]] += rate[2]
        count_w[wine[rate[1]]] += 1

    write_json(count_display, "count_display.json")

    for i in range(len(wine)):
        count_wine[i] = 1.0*count_wine[i]/count_w[i]

    write_json(count_wine, "count_wine_display.json")

    number_of_user = len(user)
    number_of_wine = len(wine)
    number_of_rate = len(filtered_data)
    print("total user:{0}, total wine:{1}, total rate:{2}".format(number_of_user, number_of_wine, number_of_rate))

    matrix = np.zeros((number_of_user, number_of_wine))
    train, test = train_test_split(filtered_data, test_size=0.1, random_state=0)
    for rate in tqdm(filtered_data):
        matrix[user[rate[0]], wine[rate[1]]] = rate[2] - count_wine[wine[rate[1]]]

    # print(matrix)

    test_value = []
    predict_value = []
    for x in test:
        test_value.append(x[2])
        predict_value.append(count_wine[wine[x[1]]])
    # print(test[0])
    # print(score(predict_value, test_value))
    # print(predict_value)

    # SVD(matrix, test, count_wine)

    # U = np.loadtxt("U.npy")
    # s = np.loadtxt("s.npy")
    # Vt = np.loadtxt("Vt.npy")
    # print(s[0:30])


