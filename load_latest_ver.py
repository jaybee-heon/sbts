import pickle

with open('./data/newest_versions.pkl', 'rb') as file:
    data_loaded = pickle.load(file)

print(data_loaded)
