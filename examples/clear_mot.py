import functools
import logging
import timeit
import signal
import scipy
import scipy.optimize
import pandas as pd
import os
import sys
import numpy as np

from qplotutils.chart.utils import makePen

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)


from qplotutils.bench import Dock, Bench, Placement
from qplotutils.chart.view import ChartView
from qplotutils.chart.items import LineChartItem

from qplotutils.chart.items import ChartItem, ChartItemFlags
from qtpy.QtCore import Qt, QPointF, QRectF, QLineF, QSizeF
from qtpy.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath, QFont, QStaticText
from qtpy.QtWidgets import (
    QGraphicsItem,
    QStyleOptionGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsWidget,
)

from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication, QAction, QMenu


np.random.seed(27)

_log = logging.getLogger("clearmot")


class ObjItem(ChartItem):
    """ Item to add a string to the view.

    :param pos: Top-left position of the text
    :param text: Content
    :param parent: Parent item.
    """

    def __init__(self, pos, width=1.0, length=1.0, link=None, parent=None):
        super(ObjItem, self).__init__(parent)
        # self.setFlags(QGraphicsItem.ItemIgnoresTransformations)
        self.chartItemFlags = ChartItemFlags.FLAG_NO_LABEL

        # self._topLeft = QPointF(0,0) # topLeftPosition
        # self._text = QStaticText(text)
        self._bRectF = QRectF(0, -width / 2, length, width)
        # self.font = QFont("Helvetica [Cronyx]", 12, QFont.Normal)
        # self.font_flags = Qt.TextDontClip | Qt.AlignRight | Qt.AlignVCenter

        self.link = link

        self.setPos(pos)

    def boundingRect(self):
        return self._bRectF

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        if self.link:
            p.setPen(makePen(Qt.red))
            p.setBrush(Qt.transparent)
        else:
            p.setPen(makePen(Qt.white))
            p.setBrush(Qt.white)
        # p.drawRect(self._bRect)
        p.drawRect(self._bRectF)

        if self.link:
            c = self.link.pos() - self.pos()
            p.drawLine(QPointF(0, 0), c)

            r = np.sqrt(c.x() ** 2 + c.y() ** 2)
            p.drawEllipse(QPointF(0, 0), r, r)


def mahalonobis_distance(df1, df2, covariance, cols):
    """ Mahalonobis distance the better way

    :param df1:
    :param df2:
    :param covariance:
    :param cols:
    :return:
    """
    cov_inv = np.linalg.inv(covariance)
    u = df1[cols].values
    v = df2[cols].values

    number_of_observations = u.shape[0]
    number_of_references = v.shape[0]
    column_count = len(cols)

    # compute the deltas
    d = (
        (u[:, np.newaxis] - v)
        .reshape(number_of_observations * number_of_references, column_count)
        .T
    )

    A = np.dot(d.T, cov_inv)
    distances = np.sqrt(np.einsum("ij,ji->i", A, d))
    # distances[np.where(distances > 5)] = np.nan
    assigned_distances = distances.reshape(number_of_observations, number_of_references)
    # print(assigned_distances.shape)

    r, c = scipy.optimize.linear_sum_assignment(assigned_distances)
    df1["assigned_ref"] = np.nan
    df2["assigned_obs"] = np.nan
    df1["assigned_ref"].iloc[r] = c
    df2["assigned_obs"].iloc[c] = r
    return assigned_distances


def calc_distance_02(df1, df2, covariance_matrix, cols):
    """ Mahalonobis distance the inefficient way

    :param df1:
    :param df2:
    :param covariance_matrix:
    :param cols:
    :return:
    """
    cov_inv = np.linalg.inv(covariance_matrix)
    distances = np.zeros((len(df1), len(df2)), dtype=np.float)

    for m in range(len(df1)):
        u = df1[cols].iloc[m].values.T
        for n in range(len(df2)):
            v = df2[cols].iloc[n].values.T

            d = u - v
            D = np.sqrt(np.dot(np.dot(d.T, cov_inv), d))

            distances[m, n] = D

    return distances


def calc_distance_01(df1, df2, cols):
    """ Euclidian distance, the inefficient way

    :param df1:
    :param df2:
    :param c:
    :param cols:
    :return:
    """
    distances = np.zeros((len(df1), len(df2)), dtype=np.float)

    for m in range(len(df1)):
        u = df1[cols].iloc[m].values.T
        for n in range(len(df2)):
            v = df2[cols].iloc[n].values.T

            e = np.sqrt(np.sum((u - v) ** 2))
            distances[m, n] = e

    return distances


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    size_obs_list = 200
    size_ref_list = 20

    columns = ["track_id", "rel_dist_x", "rel_dist_y", "abs_v_x", "abs_v_y"]
    ids = np.arange(0, size_obs_list, 1, dtype=np.int)
    x = np.random.rand(size_obs_list) * 200
    y = np.random.rand(size_obs_list) * 80 - 40
    vx = np.random.rand(size_obs_list) * 50 - 10
    vy = np.random.rand(size_obs_list) * 10 - 5

    f = np.array([ids, x, y, vx, vy]).T
    f[0:5] = np.array(
        [
            [0, 10.4, 0.2, 11.3, 0.04],
            [1, 2, -7.4, 0.003, 0.01],
            [2, 6, -7.7, 0.0002, 0.03],
            [3, 7.8, -7.2, 0.003, 0.01],
            [4, 18.0, -7.1, 0.003, 0.01],
        ]
    )

    obj_obs = pd.DataFrame(f, columns=columns)
    ids = np.arange(0, size_ref_list, 1, dtype=np.int)
    x = np.random.rand(size_ref_list) * 200
    y = np.random.rand(size_ref_list) * 80 - 40
    vx = np.random.rand(size_ref_list) * 50 - 10
    vy = np.random.rand(size_ref_list) * 10 - 5

    f = np.array([ids, x, y, vx, vy]).T
    f[0:3] = np.array(
        [
            [0, 6.8, -7.9, 0.001, 0],
            [1, 18.0, -7.1, 0.002, 0],
            [2, 10.3, 0.1, 10.3, 0.04],
        ]
    )
    obj_ref = pd.DataFrame(f, columns=columns)

    # cov_columns = columns[1:]
    # cov = np.array([[1.0, 0, 0, 0], [0, 1.9, 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 3.0]])

    cov_columns = columns[1:3]
    cov = np.array([[1.0, 0], [0, 4.0]])

    cov_inv = np.linalg.inv(cov)

    # # reference implementation
    # K = np.zeros((len(obj_obs), len(obj_ref)), dtype=np.float)
    # E = K.copy()
    #
    # left = np.zeros((len(obj_obs), len(obj_ref), len(cov_columns)), dtype=np.float)
    # right = K.copy()
    #
    # for m in range(len(obj_obs)):
    #     u = obj_obs[cov_columns].iloc[m].values.T
    #     for n in range(len(obj_ref)):
    #         v = obj_ref[cov_columns].iloc[n].values.T
    #
    #         left[m, n] = np.dot((u - v).T, cov_inv)
    #         right[m, n] = np.dot(left[m, n], (u - v))
    #         # D = np.sqrt(np.sum((u - v).T * cov_inv * (u - v)))
    #         D = np.sqrt(np.dot(np.dot((u - v).T, cov_inv), (u - v)))
    #         D_e = np.sqrt(np.sum((u - v) ** 2))
    #         # print(D)
    #         K[m, n] = D
    #         E[m, n] = D_e
    #
    # print(left)
    # print(right)
    # print(K)
    # print(E)

    # m01 = mahalonobis_distance(obj_obs, obj_ref, cov, ["rel_dist_x", "rel_dist_y"])
    # m02 = calc_distance_02(obj_obs, obj_ref, cov, ["rel_dist_x", "rel_dist_y"])
    #
    # print(m01)
    # print(m02)
    #
    # t = timeit.Timer(
    #     functools.partial(
    #         calc_distance_02, obj_obs, obj_ref, cov, ["rel_dist_x", "rel_dist_y"]
    #     )
    # )
    # print("Maholnobis for loop", t.timeit(1))
    #
    # t = timeit.Timer(
    #     functools.partial(
    #         calc_distance_01, obj_obs, obj_ref, ["rel_dist_x", "rel_dist_y"]
    #     )
    # )
    # print("Euler for loop", t.timeit(1))

    # t = timeit.Timer(
    #     functools.partial(
    #         mahalonobis_distance, obj_obs, obj_ref, cov, cov_columns
    #     )
    # )
    # print("Maholnobis vectorized", t.timeit(1))

    m01 = mahalonobis_distance(obj_obs, obj_ref, cov, cov_columns)
    # m02 = calc_distance_02(obj_obs, obj_ref, cov, cov_columns)
    # delta = m01 - m02
    # print(delta.shape, delta.min(), delta.max())

    # # do munkres
    # r, c = scipy.optimize.linear_sum_assignment(m01)
    # print(r,c)

    def sigint_handler(signum, frame):
        """ Install handler for the SIGINT signal. To kill app through shell.

        :param signum:
        :param frame:
        :return:
        """
        # sys.stderr.write('\r')
        QApplication.exit()

    signal.signal(signal.SIGINT, sigint_handler)

    qapp = QApplication([])

    # call the python loop periodically to catch interrupts from shell
    timer = QTimer()
    timer.start(1000)
    timer.timeout.connect(lambda: None)

    view = ChartView(orientation=ChartView.AUTOSAR)
    view.setAspectRatio(1)

    # columns = ["track_id", "rel_dist_x", "rel_dist_y", "abs_v_x", "abs_v_y"]
    for index, obj in obj_obs.iterrows():
        p = QPointF(obj["rel_dist_x"], obj["rel_dist_y"])

        oi = ObjItem(p)
        view.addItem(oi)

        ref_id = obj["assigned_ref"]
        if not np.isnan(ref_id):
            ref = obj_ref.loc[ref_id]
            p = QPointF(ref["rel_dist_x"], ref["rel_dist_y"])
            ri = ObjItem(p, link=oi)
            view.addItem(ri)

    view.show()
    qapp.exec_()
