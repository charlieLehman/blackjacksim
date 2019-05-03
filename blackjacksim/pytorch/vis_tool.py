import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Comment this line, if you are not running the code using ssh.


def vis_shoe_output(output, states):
    fig, ax = plt.subplots(figsize=[6, 6])
    ax.scatter(output, states, marker='o')
    plt.xlim((0.4225, 0.427))
    plt.xlabel('Normalized Estimate of Advantage', fontsize=16)
    plt.ylabel('Sum of Remaining Cards in the Deck', fontsize=16)
    plt.tight_layout()
    plt.show()


def vis_output_avg(states_sum, output_avg, save_path='./figs/plot2.png'):
    """
    Args:
        states_sum (list): a list for the sum of shoe states (13 ~ 48)
        output_avg (ndarray): The average of model output for each sum of shoe state.
                                (dim: (48 - 13 + 1) x 2 (sgd & adam))
        save_path (str): path to save a figure
    """
    matplotlib.rcParams.update({'font.size': 14})
    fig, ax = plt.subplots(figsize=[6.5, 6.5])

    ax.plot(states_sum, output_avg[:, 0], linestyle='--', marker='o')
    ax.plot(states_sum, output_avg[:, 1], linestyle='--', marker='x')

    plt.xlabel('Number of Remaining Cards in a Deck', fontsize=16)
    plt.ylabel('The Estimate of Normalized Advantage', fontsize=16)
    plt.legend(['SGD', 'ADAM'])

    plt.tight_layout()
    # plt.savefig('./figs/EstAdvantage2.png')
    plt.savefig(save_path)
    # plt.show()

def vis_output_avg_multiaxis(states_sum, output_avg, save_path='./figs/EstAdvantage3.png'):
    """
    Args:
         states_sum (list): a list for the sum of shoe states (13 ~ 48)
         output_avg (ndarray): The average of model output for each sum of shoe state.
                                (dim: (48 - 13 + 1) x 2 (sgd & adam))
        save_path (str): path to save a figure
    """

    fig, ax1 = plt.subplots(figsize=[6.5, 6.5])

    color = 'tab:blue'
    ax1.set_xlabel('Number of Remaining Cards in a Deck', fontsize=16)
    ax1.set_ylabel('The Estimate of Normalized Advantage (SGD)', color=color, fontsize=16)
    p1 = ax1.plot(states_sum, output_avg[:, 0], linestyle='--', marker='o', color=color, label='SGD')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:orange'
    ax2.set_ylabel('The Estimate of Normalized Advantage (Adam)', color=color, fontsize=16)  # we already handled the x-label with ax1
    p2 = ax2.plot(states_sum, output_avg[:, 1], linestyle='--', marker='x', color=color, label='Adam')
    ax2.tick_params(axis='y', labelcolor=color)

    lines = p1 + p2
    plt.legend(lines, [l.get_label() for l in lines], fontsize=16)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    # plt.savefig('./figs/EstAdvantage3.png')
    plt.savefig(save_path)