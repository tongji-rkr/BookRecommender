import os
import numpy as np

ROOT = "../data/"

def dataset_split(data):
    print("splitting dataset ...")
    test_ratio = 0.2
    n_data = data.shape[0]
    test_indices = np.random.choice(
        list(range(n_data)), size=int(n_data * test_ratio), replace=False
    )
    left = set(range(n_data)) - set(test_indices)
    train_indices = list(left - set(test_indices))
    train_data = data[train_indices]
    test_data = data[test_indices]
    return train_data, test_data

def load_kg():
    print("reading KG file ...")
    # reading kg file
    kg_file = ROOT + "book/kg_final"
    if os.path.exists(kg_file + ".npy"):
        kg = np.load(kg_file + ".npy")
    else:
        kg = np.loadtxt(kg_file + ".txt", dtype=np.int32)
        np.save(kg_file + ".npy", kg)

    n_entity = len(set(kg[:, 0]) | set(kg[:, 2]))
    n_relation = len(set(kg[:, 1]))
    return n_entity, n_relation, kg
