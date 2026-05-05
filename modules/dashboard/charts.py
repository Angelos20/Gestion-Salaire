from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(facecolor="#F4F6F9")
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

        self.setMouseTracking(True)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_hover)

        self.annotation = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white"),
            arrowprops=dict(arrowstyle="->"),
        )
        self.annotation.set_visible(False)

    def on_hover(self, event):
        if event.inaxes == self.ax:
            for bar in getattr(self, "bars", []):
                if bar.contains(event)[0]:
                    self.annotation.xy = (event.xdata, event.ydata)
                    self.annotation.set_text(f"{int(bar.get_height())}")
                    self.annotation.set_visible(True)
                    self.draw_idle()
                    return
        self.annotation.set_visible(False)
        self.draw_idle()

    def plot_presence(self, present, absent, retard, depart):
        self.ax.clear()

        labels = ["Présents", "Absents", "Retards", "Departs précoces"]
        values = [present, absent, retard, depart]

        self.bars = self.ax.bar(labels, values)

        self.ax.set_title("Statut des employés")
        self.draw()

    def plot_salary(self, masse, paye):
        self.ax.clear()

        labels = ["Masse salariale", "Total payé"]
        values = [masse, paye]

        self.bars = self.ax.bar(labels, values)

        self.ax.set_title("Analyse salariale")
        self.draw()

    def plot_pie(self, present, absent, retard, depart):
        self.ax.clear()

        labels = ["Présents", "Absents", "Retards", "Départs précoces"]
        values = [present, absent, retard, depart]

        self.ax.pie(values, labels=labels, autopct="%1.1f%%")

        self.ax.set_title("Répartition")
        self.draw()