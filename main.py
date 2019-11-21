from kivy.app import App
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.graph import Graph, MeshLinePlot
import numpy as np


class WorkGraph(Graph):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.y_ticks_major = 1
		self.y_grid_label = True
		self.x_grid_label = True
		self.padding = 5
		self.x_grid = True
		self.y_grid = True


class WorkSpace(BoxLayout):
	graph = None

	def __init__(self, xlabel, ylabel, xmin, xmax, ymin, ymax, title, **kwargs):
		super().__init__(**kwargs)
		self.orientation = 'vertical'
		self.add_widget(Label(text=title, size_hint_y=0.15))
		self.graph = WorkGraph(xlabel=xlabel, ylabel=ylabel, size_hint_y=0.85, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
		self.add_widget(self.graph)

	def add_plot(self, plot):
		self.graph.add_plot(plot)


t = np.array([i / 100 for i in range(100)])
lt = len(t)
c = np.cos(2 * np.pi * 2 * t).reshape(lt, 1)
s = np.sin(2 * np.pi * 2 * t).reshape(lt, 1)

val = 50

graphInput = WorkSpace(xlabel='X', ylabel='Y', title='input bit stream', xmin=0, xmax=val, ymin=-1.5, ymax=1.5)
plotIn = MeshLinePlot(color=[1, 0, 0, 1])
graphInput.add_plot(plotIn)

graphQPSK = WorkSpace(xlabel='X', ylabel='Y', title='QPSK transmitted signal', xmin=0, xmax=(val // 2) * lt, ymin=-1.5, ymax=1.5)
graphRX = WorkSpace(xlabel='X', ylabel='Y', title='QPSK received signal', xmin=0, xmax=(val // 2) * lt, ymin=-1.5, ymax=1.5)
plotQPSK = MeshLinePlot(color=[1, 0, 0, 1])
plotRX = MeshLinePlot(color=[1, 0, 0, 1])
graphRX.add_plot(plotRX)
graphQPSK.add_plot(plotQPSK)

graphOutput = WorkSpace(xlabel='X', ylabel='Y', title='Output', xmin=0, xmax=val, ymin=-0.5, ymax=1.5)
plotOut = MeshLinePlot(color=[1, 0, 0, 1])
graphOutput.add_plot(plotOut)

ber = Label()

x = np.random.randint(0, 2, size=val).reshape(val, 1)
bip = lambda i: (i * 2) - 1
y = bip(x)
x_diplay = np.matmul(y, np.ones(shape=(1, 20))).flatten()
plotIn.points = [(i / 20, x_diplay[i]) for i in range(len(x_diplay))]

I = np.matmul(np.array(list(y)[0::2]).reshape(val // 2, 1), s.transpose()).flatten()
Q = np.matmul(np.array(list(y)[1::2]).reshape(val // 2, 1), c.transpose()).flatten()
QPSK = I + Q
plotQPSK.points = [(i, QPSK[i]) for i in range(len(QPSK))]


def refresh(sc):
	# Rayleigh channel
	r = np.random.rayleigh(sc, size=len(QPSK))
	tx = QPSK + r

	# Demodulation
	plotRX.points = [(i, tx[i]-sc) for i in range(len(I))]
	rx = []
	for i in range(val // 2):
		rxc = np.multiply((tx[(i) * lt:(i + 1) * lt]).reshape(lt, 1), c)
		rxs = np.multiply((tx[(i) * lt:(i + 1) * lt]).reshape(lt, 1), s)

		rxc_in = np.trapz(rxc.reshape(lt, ), t)
		rxs_in = np.trapz(rxs.reshape(lt, ), t)

		if rxs_in > 0:
			rx.append(1)
		else:
			rx.append(0)

		if rxc_in > 0:
			rx.append(1)
		else:
			rx.append(0)

	y_diplay = np.matmul(np.array(rx).reshape(val, 1), np.ones(shape=(1, 20))).flatten()
	plotOut.points = [(i / 20, y_diplay[i]) for i in range(len(y_diplay))]

	e = 0
	for i in range(val):
		if rx[i] != x[i]:
			e += 1
	ber.text = "BER: {}".format(e/val)


refresh(10)


class Sli(Slider):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.min = 0
		self.max = 20

	def on_touch_up(self, touch):
		refresh(self.value)


class Container(GridLayout):
	cols = 1
	rows = 6

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.add_widget(graphInput)
		self.add_widget(graphQPSK)
		self.add_widget(graphRX)
		self.add_widget(graphOutput)
		self.add_widget(ber)
		self.add_widget(Sli())


class MainPage(ScrollView):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.do_scroll = True
		co = Container()
		co.bind(minimum_height=co.setter('height'))
		self.add_widget(co)


class MyApp(App):
	def build(self):
		self.title = "Grapher"
		return Container()


if __name__ == "__main__":
	MyApp().run()
