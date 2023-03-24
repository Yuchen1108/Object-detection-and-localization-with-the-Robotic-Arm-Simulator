import numpy as np
from networks.VGG import VGG
from data.data_loader import make_dataset
import torch
from tqdm import tqdm


def train_model(path, dir, n_epochs, model_name, learning_rate=0.0001, batch_size=128, val_ratio=0.05, use_gpu=False):
    print("Making dataset...")
    train_x, train_y, test_x, test_y = make_dataset(path, dir, val_ratio)
    print("DONE")

    model = VGG('MYVGG')
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion_label = torch.nn.MSELoss()
    criterion_position = torch.nn.L1Loss()
    # checking if GPU is available
    # if use_gpu and torch.cuda.is_available():
    #     model = model.cuda()
    #     criterion_label = criterion_label.cuda()
    #     criterion_position = criterion_position.cuda()

    for epoch in tqdm(range(n_epochs)):
        # training mode
        permutation = torch.randperm(train_x.size()[0])
        training_loss = []
        for i in tqdm(range(0, train_x.size()[0], batch_size)):
            indices = permutation[i:i + batch_size]
            batch_x, batch_y = train_x[indices], train_y[indices]
            # if use_gpu and torch.cuda.is_available():
            #     batch_x, batch_y = batch_x.cuda(), batch_y.cuda()

            optimizer.zero_grad()
            outputs = model(batch_x)
            loss_label = criterion_label(outputs[:, 0], batch_y[:, 0])
            loss_x = criterion_position(outputs[:, 1], batch_y[:, 1])
            loss_y = criterion_position(outputs[:, 2], batch_y[:, 2])
            loss = loss_label + loss_x + loss_y
            training_loss.append(loss.item())

            loss.backward()
            optimizer.step()

        training_loss = np.average(training_loss)

        # validation mode
        testing_loss = []
        permutation_val = torch.randperm(test_x.size()[0])
        for i in range(0, test_x.size()[0], batch_size):
            indices_val = permutation_val[i:i + batch_size]
            batch_x_val, batch_y_val = test_x[indices_val], test_y[indices_val]

            # if use_gpu and torch.cuda.is_available():
            #     batch_x_val, batch_y_val = batch_x_val.cuda(), batch_y_val.cuda()

            with torch.no_grad():
                output_val = model(batch_x_val)

            loss_label_val = criterion_label(output_val[:, 0], batch_y_val[:, 0])
            loss_x_val = criterion_position(output_val[:, 1], batch_y_val[:, 1])
            loss_y_val = criterion_position(output_val[:, 2], batch_y_val[:, 2])
            loss_val = loss_label_val + loss_x_val + loss_y_val
            testing_loss.append(loss_val.item())

        testing_loss = np.average(testing_loss)
        print('epoch: \t', epoch, '\t training loss: \t', training_loss, '\t validation loss: \t', testing_loss)
        # save model
        torch.save(model.state_dict(), '/home/zoker/COMP6445/Group_project/collect_data/save_models/' + model_name + '_epoch' + str(epoch) + '.pth.tar')


