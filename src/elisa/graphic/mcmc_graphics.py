import numpy as np

from corner import corner as _corner
import matplotlib.gridspec as gridspec
from matplotlib import pyplot as plt

from elisa.analytics.binary import params


class Plot(object):
    @staticmethod
    def corner(**kwargs):
        """
        Evaluate mcmc corner plot.

        """
        flat_chain = kwargs.pop('flat_chain')
        fit_params = kwargs.pop('fit_params')
        variable_labels = kwargs.pop('variable_labels')
        figure = _corner(flat_chain, **kwargs)

        # Extract the axes
        ndim = flat_chain.shape[1]
        axes = np.array(figure.axes).reshape((ndim, ndim))

        # Loop over the diagonal, adding units
        for ii, label in enumerate(variable_labels):
            ax = axes[ii, ii]
            value = fit_params[label]['value']
            bottom = fit_params[label]['min'] - value
            top = fit_params[label]['max'] - value
            unit = '' if fit_params[label]['unit'] == 'dimensionless' else fit_params[label]['unit']
            title = r'{0}=${1:.2f}^{{{2:+.2f}}}_{{{3:+.2f}}}$ {4}'.format(kwargs['labels'][ii], value, top, bottom,
                                                                          unit)
            ax.set_title(title)

        plt.show()

    @staticmethod
    def paramtrace(**kwargs):
        """
        Show value of parameter in mcmc chain.
        """
        hash_map = {label: idx for idx, label in enumerate(kwargs['variable_labels']) if label in
                    kwargs['traces_to_plot']}

        height = len(kwargs['traces_to_plot'])
        fig = plt.figure(figsize=(8, 2.5*height))

        gs = gridspec.GridSpec(height, 1)
        ax = []
        labels = [params.PARAMS_KEY_TEX_MAP[label] for label in kwargs['traces_to_plot']]
        for idx, label in enumerate(kwargs['traces_to_plot']):
            ax.append(fig.add_subplot(gs[idx]))
            ax[-1].scatter(np.arange(kwargs['flat_chain'].shape[0]), kwargs['flat_chain'][:, hash_map[label]],
                           label=labels[idx], s=0.2)
            ax[-1].legend(loc=1)
            unit = '' if kwargs['fit_params'][label]['unit'] == 'dimensionless' \
                else '/[{0}]'.format(kwargs['fit_params'][label]['unit'])
            ax[-1].set_ylabel(f'{labels[idx]}{unit}')

            if kwargs['truths']:
                ax[-1].axhline(kwargs['fit_params'][label]['value'], linestyle='dashed', color='black')
                ax[-1].axhline(kwargs['fit_params'][label]['min'], linestyle='dotted', color='black')
                ax[-1].axhline(kwargs['fit_params'][label]['max'], linestyle='dotted', color='black')

        ax[-1].set_xlabel('N')

        plt.subplots_adjust(right=1.0, top=1.0, hspace=0)
        plt.show()

    trace = paramtrace
