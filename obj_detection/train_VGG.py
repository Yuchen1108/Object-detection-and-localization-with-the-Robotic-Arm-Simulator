from training import train_model


path = '/home/zoker/COMP6445/Group_project/collect_data'
dir = '/random_dataset_V1'
n_epochs = 20
model_name = 'MY_VGG1'
learning_rate = 0.0001
batch_size = 1
val_ratio = 0.05
train_model(path, dir, n_epochs, model_name, learning_rate, batch_size, val_ratio)

