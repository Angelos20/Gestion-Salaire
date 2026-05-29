from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(facecolor="#F4F6F9")
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

        self.bars = []

    def safe(self, v):
        return max(0, v if v is not None else 0)

    def plot_presence(self, present, absent, retard, depart):
        self.ax.clear()

        values = [self.safe(v) for v in [present, absent, retard, depart]]
        labels = ["Présents", "Absents", "Retards", "Départs"]

        self.bars = self.ax.bar(labels, values)

        for bar in self.bars:
            h = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2, h, str(int(h)),
                         ha='center', va='bottom')

        self.ax.set_title("Présence")
        self.draw()

    def plot_salary(self, masse, paye):
        self.ax.clear()

        values = [self.safe(masse), self.safe(paye)]
        labels = ["Masse", "Payé"]

        self.bars = self.ax.bar(labels, values)

        for bar in self.bars:
            h = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2, h, str(int(h)),
                         ha='center', va='bottom')

        self.ax.set_title("Salaire")
        self.draw()

    def plot_pie(self, present, absent, retard, depart):
        self.ax.clear()

        values = [self.safe(v) for v in [present, absent, retard, depart]]
        labels = ["Présents", "Absents", "Retards", "Départs"]

        if sum(values) == 0:
            self.ax.text(0, 0, "Aucune donnée", ha='center')
            self.draw()
            return

        self.ax.pie(values, labels=labels, autopct='%1.1f%%')
        self.ax.set_title("Répartition")
        self.draw()