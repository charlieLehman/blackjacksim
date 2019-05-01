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
        loss = func.binary_cross_entropy(output[:, 0], label)
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


def test(d, device, data_loader, epoch, print_freq):
    """
    Args:
        d (DataParallel(module)): classifier
        device (Device): CPU or GPU
        data_loader (DataLoader): data loader for shoe states and their labels
        optimizer
        epoch (int)
        print_freq(int): Determine how often to print out progress
    """
    d.eval()
    losses = utils.AverageMeter()
    correct = 0
    nsamples = 0

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

        if batch_idx % print_freq == 0:
            print('Epoch: [{0}][{1}/{2}]\t Loss {loss.val:.4f} ({loss.avg:.4f}) Acc {3:.3f} ({4:.3f})'
                  .format(epoch, batch_idx, len(data_loader), current_correct / states.shape[0], correct / nsamples,
                          loss=losses))

    nsamples = (batch_idx + 1) * states.shape[0]
    accuracy = 100. * correct / nsamples
    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.3f}%)\n'.format(
        losses.val, correct, nsamples, accuracy))

    return losses.avg, accuracy
