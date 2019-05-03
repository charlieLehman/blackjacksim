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


def vis_output_avg(states_sum, output_avg, save_path='./figs/plot1.png'):
    """
    Args:
         states_sum (list): a list for the sum of shoe states (13 ~ 48)
         output_avg (ndarray): The average of model output for each sum of shoe state.
                                (dim: (48 - 13 + 1) x 2 (sgd & adam))
    """
    matplotlib.rcParams.update({'font.size': 14})
    fig, ax = plt.subplots(figsize=[6, 6])

    ax.plot(states_sum, output_avg[:, 0], linestyle='--', marker='o')
    ax.plot(states_sum, output_avg[:, 1], linestyle='--', marker='x')

    plt.xlabel('Sum of Remaining Cards in the Deck', fontsize=16)
    plt.ylabel('Normalized Estimate of Advantage', fontsize=16)
    plt.legend(['SGD', 'ADAM'])

    plt.tight_layout()
    plt.savefig(save_path)
    # plt.show()
