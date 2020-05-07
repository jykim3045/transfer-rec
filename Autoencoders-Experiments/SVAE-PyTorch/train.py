import time
from utils import file_write


def train(model, criterion, reader, optimizer, epoch, hyper_params):
    """
    Function to train the model
    :param model: The model choice
    :param criterion: The loss function choice
    :param reader: The Data Reader class
    :param optimizer: The optimizer choice
    :param epoch: The given epoch
    :param hyper_params: The hyper-parameter dictionary
    """
    # Step into training mode
    model.train()

    total_loss = 0
    start_time = time.time()
    batch = 0
    batch_limit = int(reader.num_b)
    total_anneal_steps = 200000
    anneal = 0.0
    update_count = 0.0
    anneal_cap = 0.2

    for x, y_s in reader.iter():
        batch += 1

        # Empty the gradients
        model.zero_grad()
        optimizer.zero_grad()

        # Forward pass
        decoder_output, z_mean, z_log_sigma = model(x)

        # Backward pass
        loss = criterion(decoder_output, z_mean, z_log_sigma, y_s, anneal)
        loss.backward()
        optimizer.step()

        total_loss += loss.data

        # Anneal logic
        if total_anneal_steps > 0:
            anneal = min(anneal_cap, 1. * update_count / total_anneal_steps)
        else:
            anneal = anneal_cap
        update_count += 1.0

        # Logging mechanism
        if (batch % hyper_params['batch_log_interval'] == 0 and batch > 0) or batch == batch_limit:
            div = hyper_params['batch_log_interval']
            if batch == batch_limit:
                div = (batch_limit % hyper_params['batch_log_interval']) - 1
            if div <= 0:
                div = 1

            cur_loss = (total_loss[0] / div)
            elapsed = time.time() - start_time

            ss = '| epoch {:3d} | {:5d}/{:5d} batches | ms/batch {:5.2f} | loss {:5.4f}'.format(
                epoch, batch, batch_limit, (elapsed * 1000) / div, cur_loss
            )

            file_write(hyper_params['log_file'], ss)

            total_loss = 0
            start_time = time.time()
