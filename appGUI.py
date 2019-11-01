from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from timeit import default_timer as timer
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import arange, sin, pi
import sys
import os


class IGLayout(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self._window = parent

        self.mainLayout = QHBoxLayout(self._window)
        # self.mainLayout.setAlignment()
        # Create right
        self.rightFrame = QFrame(self._window)
        self.rightFrame.setMaximumWidth(300)
        #self.rightFrame.setMaximumHeight(500)
        self.rightFrame.setFrameShape(QFrame.StyledPanel)
        self.rightFrame.setFrameShadow(QFrame.Raised)
        self.rightFrame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.rightFrame.setLineWidth(2)
        self.rightFrame.setMidLineWidth(2)
        self.mainLayout.addWidget(self.rightFrame)

        # Create middle frame
        self.midFrame = QFrame(self._window)
        self.midFrame.setMaximumWidth(500)
        self.midFrame.setFrameShape(QFrame.StyledPanel)
        self.midFrame.setFrameShadow(QFrame.Raised)
        self.midLayout = QVBoxLayout(self.midFrame)

        self.msgDataFrame = QFrame(self.midFrame)
        self.msgDataFrame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.msgDataFrame.setLineWidth(2)
        self.msgDataFrame.setMidLineWidth(2)
        self.msgDataFrame.setFixedHeight(60)

        self.sigDataFrame = QFrame(self.midFrame)
        self.sigDataFrame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.sigDataFrame.setLineWidth(2)
        self.sigDataFrame.setMidLineWidth(2)

        self.midLayout.addWidget(self.msgDataFrame)
        self.midLayout.addWidget(self.sigDataFrame)
        self.mainLayout.addWidget(self.midFrame)

        # Create left frame
        self.leftFrame = QFrame(self._window)
        # self.leftFrame.setStyleSheet("background-color: yellow;")
        self.leftFrame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.leftFrame.setLineWidth(2)
        self.leftFrame.setMidLineWidth(2)
        self.leftFrame.setFrameShape(QFrame.StyledPanel)
        self.leftFrame.setFrameShadow(QFrame.Raised)
        #self.leftFrame.setMaximumWidth(300)
        self.mainLayout.addWidget(self.leftFrame)

    def getRightFrame(self):
        return self.rightFrame

    def get_left_frame(self):
        return self.leftFrame

    def get_sig_frame(self):
        return self.sigDataFrame

    def get_data_msg_frame(self):
        return self.msgDataFrame

    def get_main_layout(self):
        return self.mainLayout


class SearchWidget(QObject):

    msg_selected = pyqtSignal()

    def __init__(self, parent_frame=None):
        super(SearchWidget, self).__init__()

        self._frame = parent_frame
        self._verticalLayout = QVBoxLayout(self._frame)
        self._search_by_name = QLineEdit()
        self._msg_name_list = QListWidget()

        self._messages_cash = {}
        self._search_res = {}

        self._search_by_name.textChanged.connect(self.update_list)
        self._verticalLayout.addWidget(self._search_by_name)
        self._verticalLayout.addWidget(self._msg_name_list)
        self._msg_name_list.itemDoubleClicked.connect(self.msg_selected)

    def update_list(self, serch_key):
        search_term = serch_key
        self._msg_name_list.clear()

        for item in self._messages_cash:
            if search_term.lower() in item.lower():
                self._msg_name_list.addItem(item)

    def update(self):
        for item in self._messages_cash:
            self._msg_name_list.addItem(item)

    def load_message_list(self, ms_list):
        self._messages_cash = ms_list

    def get_message_name(self):
        return self._msg_name_list.currentItem().text()


class SignalConfigWidget:

    def __init__(self, parent_frame):
        self._frame = parent_frame
        self._tempWidget = QWidget()
        self._scroll_area = QScrollArea(self._frame)
        self._scroll_area.setWidget(self._tempWidget)
        self._scroll_area.setFixedWidth(450)
        self._scroll_area.setWidgetResizable(True)

        self._verticalLayout = QVBoxLayout(self._tempWidget)
        self._mainVerticalLayout = QVBoxLayout(self._frame)
        self._mainVerticalLayout.addWidget(self._scroll_area)

        self._row = 0

    def clean_frame(self):
        for i in reversed(range(self._verticalLayout.count())):
            self._verticalLayout.itemAt(i).widget().deleteLater()

    def load_msg_signals(self, sig_update_msg):
        print("load_msg_signals")
        options = []
        sig_options = sig_update_msg.get_options()

        try:
            for key in sig_options:
                """Get all signals variants and put to string"""
                options.append(str(sig_options[key]) + ' = ' + str(key))
            """Make widget"""
            options.reverse()
            print(options)
            s_frame = QFrame()
            # s_frame.setFixedHeight(50)
            hor_layout = QHBoxLayout(s_frame)
            # hor_layout.setMaximumHeight(20)

            sig_name = QLabel(s_frame, text=str(sig_update_msg.get_name()))
            sig_name.setFixedWidth(150)
            option_menu = QComboBox(s_frame)
            option_menu.setCurrentIndex(0)
            option_menu.addItems(options)
            option_menu.currentIndexChanged.connect(lambda data: sig_update_msg.update(data))
            option_menu.setFixedWidth(150)

            hor_layout.addWidget(sig_name)
            hor_layout.addWidget(option_menu)

            self._verticalLayout.addWidget(s_frame, stretch=1, alignment=Qt.AlignTop)
            self._mainVerticalLayout.addWidget(self._scroll_area)

        except TypeError as te:
            print("Error: {}, sig name: {}".format(str(te), str(sig_options)))


class GenerateMsgWidget(QWidget):

    def __init__(self, parent_frame):
        super(GenerateMsgWidget, self).__init__()
        self._frame = parent_frame
        self._payload_bytes = set()

        self._layout = QHBoxLayout(self._frame)
        self._info = QLabel(self._frame, text='Message:')

        self._msg_id = QLineEdit(self._frame, text='000')
        self._msg_id.setFixedWidth(50)

        self._msg_payload = QLineEdit(self._frame)
        self._msg_payload.setFixedWidth(200)

        self._layout.addWidget(self._info)
        self._layout.addWidget(self._msg_id)
        self._layout.addWidget(self._msg_payload)

        self._msg_id.setText('000')
        self._msg_payload.setText('00:00:00:00:00:00:00:00')

    def update_signals_field(self, msg_id, data):
        print("Update signals")
        self._msg_id.setText(msg_id)
        self._msg_payload.setText(data)


class TabsWidget(QWidget):

    def __init__(self, parent):
        super(TabsWidget, self).__init__(parent)
        self._layout = QVBoxLayout(self)
        self._tabsArray = dict()
        self._tabs = QTabWidget()
        self._tabs.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

    def create_new_tab(self, tab_name, widget):
        """
        :param tab_name: string with tab name
        :param widget:
        :return:
        """
        self._tabsArray[tab_name] = widget
        self._tabs.addTab(self._tabsArray[tab_name], tab_name)

    def final_tabs_setup(self):
        # Add tabs to widget
        self._layout.addWidget(self._tabs)
        self.setLayout(self._layout)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


class ThumbListWidget(QListWidget):
    file_path_updated = pyqtSignal(str)

    def __init__(self, type, parent=None):
        super(ThumbListWidget, self).__init__(parent)
        self.setIconSize(QSize(124, 124))
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(ThumbListWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            super(ThumbListWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        print('dropEvent', event)
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            filepath = str(urls[0].path())[1:]
            print(filepath[-4:])
            # any file type here
            if filepath[-4:] == '.asc':
                print(filepath)
                self.file_path_updated.emit(filepath)
                # self.clear()
            else:
                dialog = QMessageBox()
                dialog.setWindowTitle("Error: Invalid File")
                dialog.setText("Only .txt files are accepted")
                dialog.setIcon(QMessageBox.Warning)
                dialog.exec_()

    def up_data_to_view(self, payload_list):
        start = timer()
        for item in payload_list:
            self.addItem(item)
        end = timer()
        print("up_data_to_view" + str(end-start))


class AnalyzerWidget(QWidget):
    str_selected = pyqtSignal()
    make_graph = pyqtSignal(dict)
    clean = pyqtSignal()

    def __init__(self, parent=None):
        super(AnalyzerWidget, self).__init__(parent=parent)

        self._fileExplorerWidget = QListWidget()
        self._fileExplorerWidget.setMinimumWidth(900)
        self._fileExplorer = ThumbListWidget(self)
        self._messages_cash = dict()
        self._log_cash = list()
        self._search_key = str()
        self._search_key_sig = str()
        self._filtered_msg = list()
        self._signals_cash = dict()

        self._msgFrame = QFrame()
        self._searchBoxFrame = QFrame()
        self._searchSigFrame = QFrame()
        self._layoutDetailArea = QVBoxLayout(self._msgFrame)
        self._searchBox = QHBoxLayout(self._searchBoxFrame)
        self._searchSigBox = QHBoxLayout(self._searchSigFrame)
        self._layout = QHBoxLayout(self)
        self._mainArea = QListWidget()
        self._msgName = QListWidget()
        self._searchByExpr = QLineEdit()
        self._searchBySignal = QLineEdit()
        self._msgDetailArea = QListWidget()
        self._searchButton = QPushButton("find")
        self._cleanButton = QPushButton("clean")
        self._mkGraphButton = QPushButton("make graph")
        self._cleanGraphButton = QPushButton("clean")
        self._mainArea.setMinimumWidth(900)
        # self._msgDetailArea.setMaximumWidth(400)
        # self._msgName.setMaximumWidth(400)
        self._msgFrame.setMaximumWidth(400)
        self._msgName.setMaximumHeight(40)

        self._layout.addWidget(self._fileExplorer)
        self._layout.addWidget(self._msgFrame)
        self._searchBox.addWidget(self._searchButton)
        self._searchBox.addWidget(self._cleanButton)
        self._searchSigBox.addWidget(self._mkGraphButton)
        self._searchSigBox.addWidget(self._cleanGraphButton)
        self._layoutDetailArea.addWidget(self._searchByExpr)
        self._layoutDetailArea.addWidget(self._searchBoxFrame)
        self._layoutDetailArea.addWidget(self._searchBySignal)
        self._layoutDetailArea.addWidget(self._searchSigFrame)
        self._layoutDetailArea.addWidget(self._msgName)
        self._layoutDetailArea.addWidget(self._msgDetailArea)

        self._fileExplorer.itemDoubleClicked.connect(self.str_selected)
        self._searchByExpr.textChanged.connect(self.update_key)
        self._searchBySignal.textChanged.connect(self.update_sig_key)
        self._searchButton.clicked.connect(self.update_list)
        self._cleanButton.clicked.connect(self.clean_search_res)
        self._msgName.doubleClicked.connect(self.push_name_to_search)
        self._msgDetailArea.doubleClicked.connect(self.get_signal_name)
        self._mkGraphButton.clicked.connect(self.push_data_to_graph)
        self._cleanGraphButton.clicked.connect(self.clean_graph)

    def get_signal_name(self):
        if self._searchBySignal.cursorPosition() == 0:
            self._searchBySignal.insert(self._msgDetailArea.currentItem().text().split('=')[0])
        else:
            self._searchBySignal.insert('|' + self._msgDetailArea.currentItem().text().split('=')[0])

    def clean_graph(self):
        self.clean.emit()
        self._searchBySignal.clear()

    def update_sig_key(self, search_sig):
        self._search_key_sig = search_sig

    def push_data_to_graph(self):
        try:
            search_keys = self._search_key_sig.split('|')
            for item_key in search_keys:
                if item_key in self._signals_cash:
                    self.make_graph.emit(self._signals_cash[item_key])
        except:
            print("PANIC push_data_to_graph")

    def clean_search_res(self):
        self._filtered_msg.clear()
        self._fileExplorer.clear()
        self._searchByExpr.clear()
        self._fileExplorer.up_data_to_view(self._log_cash)

    def push_name_to_search(self):
        print("Cursor " + str(self._searchByExpr.cursorPosition()))
        if self._searchByExpr.cursorPosition() == 0:
            self._searchByExpr.insert(self._msgName.currentItem().text())
        else:
            self._searchByExpr.insert('|' + self._msgName.currentItem().text())

    def update_key(self, search_key):
        self._search_key = search_key

    def update_list(self):
        self._filtered_msg.clear()
        self._fileExplorer.clear()

        search_keys = self._search_key.split('|')
        for item_key in search_keys:
            for item in self._messages_cash:
                if item_key.lower() in item.lower():
                    self._filtered_msg.extend(self._messages_cash[item.strip()])

        self._filtered_msg.sort()
        try:
            for str_item in self._filtered_msg:
                self._fileExplorer.addItem(str_item)
        except:
            print("PANIC!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! " + item)

    def connect_drop_event(self, handler):
        self._fileExplorer.file_path_updated.connect(lambda file_path: handler(file_path))

    def upload_file_data(self, data_list, data_dict):
        start = timer()
        self._fileExplorer.clear()
        self._messages_cash = data_dict
        self._log_cash = data_list
        end = timer()
        print("upload_file_data" + str(end-start))
        self._fileExplorer.up_data_to_view(self._log_cash)

    def get_selected_str(self):
        print(self._fileExplorer.currentItem().text())
        return self._fileExplorer.currentItem().text()

    def upload_msg_data(self, signal_data):
        self._msgDetailArea.clear()
        for sig_name in signal_data:
            self._msgDetailArea.addItem(str(sig_name) + "=" + str(signal_data[sig_name]))

    def upload_msg_name(self, name):
        self._msgName.clear()
        self._msgName.addItem(name)

    def upload_file_signals(self, signals_dict):
        print("upload_file_signals")
        self._signals_cash = signals_dict


class PlotCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        # self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MsgCanvas(PlotCanvas):
    """Simple canvas with a sine plot."""

    def __init__(self, *args, **kwargs):
        PlotCanvas.__init__(self, *args, **kwargs)
        self._data = dict()

    def upload_data(self, data):
        self._data = data

    def compute_initial_figure(self):
        pass

    def make_it(self):
        print(self._data)
        x = list(self._data.keys())
        y = list(self._data.values())
        self.axes.plot(x, y)
        self.draw()


class MyStaticMplCanvas(PlotCanvas):
    """Simple canvas with a sine plot."""
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)


class GraphWidget(QWidget):

    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent=parent)
        self._pool = list()
        self._layout = QVBoxLayout(self)

    def show(self, data):
        msg_graph = MsgCanvas()
        msg_graph.upload_data(data)
        self._layout.addWidget(msg_graph)
        msg_graph.make_it()

    def clean(self):
        for i in reversed(range(self._layout.count())):
            self._layout.itemAt(i).widget().deleteLater()

        print("clean graph")

    def test(self):
        msg_graph = MyStaticMplCanvas()
        self._layout.addWidget(msg_graph)
        print("show test graph")


class GuiWindow(QMainWindow):
    requestSignalDataSig = pyqtSignal(str)
    openNewFile = pyqtSignal(str)
    requestForMsgDecode = pyqtSignal(str)
    findMessageInLog = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._title = 'PyCAN'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200
        self.setWindowTitle(self._title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self._tabWidget = TabsWidget(self)

        self._graph = GraphWidget(self)

        self._analyser = AnalyzerWidget(self)
        self._analyser.connect_drop_event(lambda file_path: self.openNewFile.emit(file_path))
        self._analyser.str_selected.connect(self.request_for_decode_msg)
        self._analyser.make_graph.connect(self._graph.show)
        self._analyser.clean.connect(self._graph.clean)

        self._ig = QWidget()
        self._layoutIg = IGLayout(self._ig)
        self._searchWidget = SearchWidget(self._layoutIg.getRightFrame())
        self._signalConfigWidget = SignalConfigWidget(self._layoutIg.get_sig_frame())
        self._searchWidget.msg_selected.connect(self.show_message_struct)
        self._msgResult = GenerateMsgWidget(self._layoutIg.get_data_msg_frame())

        self._tabWidget.create_new_tab("IG", self._ig)
        self._tabWidget.create_new_tab("Analyzer", self._analyser)
        self._tabWidget.create_new_tab("Graph", self._graph)
        self._tabWidget.final_tabs_setup()

        self.setCentralWidget(self._tabWidget)
        self.show()

    @pyqtSlot(dict)
    def load_signals_cash(self, signals_data):
        self._analyser.upload_file_signals(signals_data)

    @pyqtSlot(str)
    def show_message_name(self, msg_name):
        print("show_message_name" + msg_name)
        self._analyser.upload_msg_name(msg_name)

    @pyqtSlot(dict)
    def show_message_payload(self, sig_dict):
        print("show_message_payload")
        self._analyser.upload_msg_data(sig_dict)

    @pyqtSlot()
    def request_for_decode_msg(self):
        self.requestForMsgDecode.emit(self._analyser.get_selected_str())

    @pyqtSlot(list, dict)
    def upload_file_data(self, data_list, data_dict):
        self._analyser.upload_file_data(data_list, data_dict)

    @pyqtSlot()
    def show_message_struct(self):
        print("show_message_struct MSG Name {}".format(self._searchWidget.get_message_name()))
        self.requestSignalDataSig.emit(self._searchWidget.get_message_name())

    @pyqtSlot(set)
    def pop_signals_to_gui(self, sig_collection):
        print("pop_signals_to_gui")
        self._signalConfigWidget.clean_frame()
        for signal_updater in sig_collection:
            """Put signals options into conf widget"""
            try:
                self._signalConfigWidget.load_msg_signals(sig_update_msg=signal_updater)
            except:
                print("Catch error")

    @pyqtSlot(str, str)
    def update_msg_data(self, msg_id, data):
        print("update_msg_data")
        self._msgResult.update_signals_field(msg_id, data)

    def load_message_list(self, message_list):
        print("load_message_list")
        self._searchWidget.load_message_list(message_list)
        self._searchWidget.update()

