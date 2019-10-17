import torch
import torch.nn.functional as func

import utils
import numpy as np


def train(d, device, data_loader, optimizer, epoch, print_freq):
    """
    Args:
        d (DataParallel(module)): classifier
        device (Device): CPU or GPU
        data_loader (DataLoader): data loader for shoe states and their labels
        optimizer
        epoch (int)
        print_freq(int): Determine how often to print out progress
    """
    d.train()
    losses = utils.AverageMeter()
    correct = 0
    nsamples = 0

    for batch_idx, (states, label) in enumerate(data_loader):

        states = states.to(device)
        label = label.to(device)
        optimizer.zero_grad()
        output = d(states)
        label[label == -1] = 0
        loss = func.binary_cross_entropy(output[:, 0], label, reduction='none')
        # loss = func.binary_cross_entropy(output[:, 0], label)
        alpha  = 0.3
        mask = label * (1 + alpha)
        mask[mask == 0] = (1 - alpha)
        loss = loss * mask
        loss = loss.mean()

        losses.update(loss.item(), states.size(0))
        loss.backward()
        optimizer.step()
        pred = output >= 0.5
        current_correct = pred.eq(label.type(torch.uint8).view_as(pred)).sum().item()
        correct += current_correct
        nsamples += states.shape[0]

        if batch_idx % print_freq == 0:
            print('Epoch: [{0}][{1}/{2}]\t Loss {loss.val:.4f} ({loss.avg:.4f}) Acc {3:.3f} ({4:.3f})'
                .format(epoch, batch_idx, len(data_loader), current_correct / states.shape[0], correct / nsamples,
                        loss=losses))

    # nsamples = (batch_idx + 1) * states.shape[0]
    accuracy = 100. * correct / nsamples
    print('\nTrain set: Average loss: {:.4f}, Accuracy: {}/{} ({:.3f}%)\n'.format(
            losses.val, correct, nsamples, accuracy))

    return losses.avg, accuracy


def test(d, device, data_loader, epoch, print_freq, nsamples_per_state_sum):
    """
    Args:
        d (DataParallel(module)): classifier
        device (Device): CPU or GPU
        data_loader (DataLoader): data loader for shoe states and their labels
        optimizer
        epoch (int)
        print_freq(int): Determine how often to print out progress
        nsamples_per_state_sum (int): Number of samples that you want to observe for each sum of shoe state
    """
    d.eval()
    losses = utils.AverageMeter()
    correct = 0
    nsamples = 0

    # states_sum = np.zeros([896,])
    # output_all = np.zeros([896,])
    keys = [i for i in range(13, 49)]

    state_output = dict.fromkeys(keys, 0)
    state_cnt = dict.fromkeys(keys, 0)

    for batch_idx, (states, label) in enumerate(data_loader):

        states = states.to(device)
        label = label.to(device)
        output = d(states)
        label[label == -1] = 0
        loss = func.binary_cross_entropy(output[:, 0], label)
        losses.update(loss.item(), states.size(0))

        pred = output >= 0.5
        current_correct = pred.eq(label.type(torch.uint8).view_as(pred)).sum().item()
        correct += current_correct
        nsamples += states.shape[0]

        # states_sum[cnt:cnt + states.shape[0]] = states.sum(dim=1).cpu()
        # output_all[cnt:cnt + states.shape[0]] = output.cpu().detach().numpy()[:, 0]
        # cnt += states.shape[0]

        states_sum = states.sum(dim=1)

        print('State_cnt values = (%d / %d)' % (sum(state_cnt.values()), nsamples_per_state_sum * (48 - 13  + 1)))
        if sum(state_cnt.values()) == nsamples_per_state_sum * (48 - 13  + 1):
            break

        for idx, s in enumerate(states_sum):
            s = int(s.item())
            if s >= 13 and s <= 48:  # Total number of remaining cards 13 ~ 48
                if state_cnt[s] < nsamples_per_state_sum:
                    state_output[s] += output[idx].item()
                    state_cnt[s]+= 1

        if batch_idx % print_freq == 0:
            print('Epoch: [{0}][{1}/{2}]\t Loss {loss.val:.4f} ({loss.avg:.4f}) Acc {3:.3f} ({4:.3f})'
                  .format(epoch, batch_idx, len(data_loader), current_correct / states.shape[0], correct / nsamples,
                          loss=losses))

    nsamples = (batch_idx + 1) * states.shape[0]
    accuracy = 100. * correct / nsamples
    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.3f}%)\n'.format(
        losses.val, correct, nsamples, accuracy))

    return losses.avg, accuracy, state_output
