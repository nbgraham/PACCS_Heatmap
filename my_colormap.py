from matplotlib.colors import LinearSegmentedColormap

cdict = {'red':   ((0.0, 0.0, 0.0),
                   (0.0, 0.0, 1.0),
                   (1.0, 0.0, 0.0)),

         'green': ((0.0, 0.0, 0.0),
                   (0.0, 0.0, 0.0),
                   (1.0, 1.0, 1.0)),

         'blue':  ((0.0, 0.0, 0.0),
                   (0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0))
        }

red_green = LinearSegmentedColormap('RedGreen', cdict)

cdict = {'red':   ((0.0, 1.0, 1.0),
                   (0.4, 0.9, 0.9),
                   (1.0, 0.0, 0.0)),

         'green': ((0.0, 0.0, 0.0),
                   (0.4, 0.1, 0.1),
                   (1.0, 1.0, 1.0)),

         'blue':  ((0.0, 0.0, 0.0),
                   (0.5, 0.0, 0.0),
                   (1.0, 0.0, 0.0))
        }

red_green_high = LinearSegmentedColormap('RedGreenHigh', cdict)