======
Charts
======

ChartView
---------

The ChartView is the base widget to display data series.

.. code-block:: python

    view = ChartView(orientation=ChartView.CARTESIAN)



ChartItems
----------

Line Chart example:

.. code-block:: python

    l = LineChartItem()
    l.abscissa = "Time"
    l.ordinate = "Spam"

    x = np.arange(-30, 300, 0.2, dtype=np.float)
    y = np.sin(2 * np.pi * 3 / float(max(x) - min(x)) * x)

    l.plot(y, x, label="a sinus")
    self.view.addItem(l)
