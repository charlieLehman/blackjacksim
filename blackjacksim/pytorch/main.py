import torch
import torch.utils.data
from torch import optim

import argparse
import os
import time
import sys
sys.path.append('../../')
from tensorboardX import SummaryWriter
import numpy as np

import models
import dataloader
import utils
import bettingstrat
import vis_tool

parser = argparse.ArgumentParser(description='PyTorch Autoencoder Training')
parser.add_argument('--epochs', default=100, type=int, metavar='N',
                    help='number of total epochs to run')
parser.add_argument('--print-freq', '-pf', default=10, type=int,
                    metavar='N', help='print frequency (default: 10)')
parser.add_argument('--write-freq', '-wf', default=5, type=int,
                    metavar='N', help='write frequency (default: 5)')
parser.add_argument('--write-enable', '-we', action='store_true', help='Write checkpoints and logs')
parser.add_argument('--eval', '-e', action='store_true', help='Evaluation')


def main():
    global args
    args = parser.parse_args()

    timestart = time.time()
    savedir = 'DisFiveLinearReLu_sgd-lr-1e-3_epoch-100_penalizedBCE-alpha0.3'

    checkpointdir = os.path.join('./checkpoints', savedir)
    logdir = os.path.join('./logs', savedir)

    if args.write_enable:
        os.makedirs(checkpointdir)
        writer = SummaryWriter(log_dir=logdir)
        print('log directory: %s' % logdir)
        print('checkpoints directory: %s' % checkpointdir)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    batch_size = 128
    train_loader = dataloader.BlackjackDataset(batch_size=batch_size, max_len=5000)
    eval_loader = dataloader.BlackjackDataset(batch_size=batch_size, max_len=1000000000)


    if args.eval:
        d_sgd = models.DisFiveLinearReLu(10)
        d_sgd = torch.nn.DataParallel(d_sgd).to(device)
        checkpointdir = './checkpoints/DisFiveLinearReLu_sgd-lr-1e-3_epoch-100/model_best.pth.tar'
        if os.path.isfile(checkpointdir):
            print("=> loading checkpoint '{}'".format(checkpointdir))
            d_sgd_ckpt = torch.load(checkpointdir)
            best_acc = d_sgd_ckpt['best_acc']
            d_sgd.load_state_dict(d_sgd_ckpt['state_dict'])
            print("=> loaded checkpoint '{}' (epoch {}, best_loss {})"
                  .format(checkpointdir, d_sgd_ckpt['epoch'], best_acc))
        else:
            print("=> no checkpoint found at '{}'".format(checkpointdir))

        nsamples_per_state_sum = 200
        _, _, state_output_sgd = bettingstrat.test(d_sgd, device, eval_loader, 1, args.print_freq,
                                                   nsamples_per_state_sum)

        d_adam = models.DisFiveLinearReLu(10)
        d_adam = torch.nn.DataParallel(d_adam).to(device)
        checkpointdir = './checkpoints/DisFiveLinearReLu_sgd-lr-1e-3_epoch-100/model_best.pth.tar'
        if os.path.isfile(checkpointdir):
            print("=> loading checkpoint '{}'".format(checkpointdir))
            d_adam_ckpt = torch.load(checkpointdir)
            best_acc = d_adam_ckpt['best_acc']
            d_adam.load_state_dict(d_adam_ckpt['state_dict'])
            print("=> loaded checkpoint '{}' (epoch {}, best_loss {})"
                  .format(checkpointdir, d_adam_ckpt['epoch'], best_acc))
        else:
            print("=> no checkpoint found at '{}'".format(checkpointdir))

        nsamples_per_state_sum = 200
        _, _, state_output_adam = bettingstrat.test(d_adam, device, eval_loader, 1, args.print_freq,
                                                    nsamples_per_state_sum)

        output_avg = np.zeros([48 - 13  + 1, 2]) # Sum of remaining cards 13 ~ 48
        for i in range(13, 49):
            output_avg[i - 13, 0] = state_output_sgd[i] / nsamples_per_state_sum
            output_avg[i - 13, 1] = state_output_adam[i] / nsamples_per_state_sum
        vis_tool.vis_output_avg([i for i in range(13, 49)], output_avg)

        return

    d = models.DisFiveLinearReLu(10)
    d = torch.nn.DataParallel(d).to(device)
    d.apply(models.weights_init)
    optimizer = optim.SGD(d.parameters(), lr=1e-3)
    # optimizer = optim.Adam(d.parameters(), lr=1e-3)


    best_score = 0
    # Start training
    for epoch in range(0, args.epochs):
        print('\n*** Start Training *** Epoch: [%d/%d]\n' % (epoch + 1, args.epochs))
        loss, acc = bettingstrat.train(d, device, train_loader, optimizer, epoch + 1, args.print_freq)


        # print('\n*** Start Testing *** Epoch: [%d/%d]\n' % (epoch + 1, args.epochs))


        is_best = acc > best_score
        best_score = max(acc, best_score)

        if is_best:
            best_epoch = epoch + 1

        if args.write_enable:
            if epoch % 5 == 0 or is_best is True:
                writer.add_scalar('loss', loss, epoch + 1)
                writer.add_scalar('accuracy', acc, epoch + 1)
                utils.save_checkpoint({
                    'epoch': epoch + 1,
                    'state_dict': d.state_dict(),
                    'best_acc': best_score,
                    'last_loss': loss,
                    'optimizer': optimizer.state_dict(),
                }, is_best, checkpointdir)

    if args.write_enable:
        writer.close()

    print('Best Testing Acc: %.3f at epoch %d' % (best_score, best_epoch))
    print('Best epoch: ', best_epoch)
    print('Total processing time: %.4f' % (time.time() - timestart))


if __name__ == '__main__':
    main()
