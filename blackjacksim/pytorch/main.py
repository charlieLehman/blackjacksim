import torch
import torch.utils.data
from torch import optim

import argparse
import os
import time
import sys
sys.path.append('../../')
from tensorboardX import SummaryWriter

import models
import dataloader
import utils
import bettingstrat

parser = argparse.ArgumentParser(description='PyTorch Autoencoder Training')
parser.add_argument('-e', '--epochs', default=300, type=int, metavar='N',
                    help='number of total epochs to run')
parser.add_argument('--print-freq', '-pf', default=10, type=int,
                    metavar='N', help='print frequency (default: 10)')
parser.add_argument('--write-freq', '-wf', default=5, type=int,
                    metavar='N', help='write frequency (default: 5)')
parser.add_argument('--write-enable', '-we', action='store_true', help='Write checkpoints and logs')


def main():
    global args
    args = parser.parse_args()

    timestart = time.time()
    savedir = 'sgd'

    checkpointdir = os.path.join('./checkpoints', savedir)
    logdir = os.path.join('./logs', savedir)

    if args.write_enable:
        os.makedirs(checkpointdir)
        writer = SummaryWriter(log_dir=logdir)
        print('log directory: %s' % logdir)
        print('checkpoints directory: %s' % checkpointdir)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    batch_size = 64
    train_loader = dataloader.BlackjackDataset(batch_size=batch_size)
    val_loader = dataloader.BlackjackDataset(batch_size=batch_size)

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
        # loss, acc = bettingstrat.test(d, device, val_loader, optimizer, epoch + 1, args.print_freq)

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
