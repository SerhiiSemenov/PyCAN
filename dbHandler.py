import cantools
import canToolsWrapper
from PyQt5.QtCore import *
from collections import OrderedDict


class SignalData(QObject):

    def __init__(self, signal_name=None, options=None, update_cb=None):
        super(SignalData, self).__init__()
        self._options = OrderedDict()
        self._options = options
        self._current_val = 0
        self._name = signal_name
        self._update_cb = update_cb

        self._options_list = []
        for key in self._options:
            """Get all signals variants and put to string"""
            self._options_list.append(self._options[key])

        self._options_list.reverse()

    def update(self, value):
        print(self._options_list[value])

        self._current_val = self._options_list[value]

        print("Name {}, InVal {}, Val {}".format(self._name, value, self._current_val))
        self._update_cb()

    def set_current_value(self, value):
        self._current_val = value

    def get_name(self):
        return self._name

    def get_value(self):
        return self._current_val

    def get_options(self):
        return self._options


class DbHandler(QObject):

    msgDataUpdSig = pyqtSignal(str, str)
    loadSigDataToGui = pyqtSignal(set)
    loadCANTrace = pyqtSignal(list, dict)
    loadSignalValsToGui = pyqtSignal(dict)
    loadMsgSigVal = pyqtSignal(dict)
    loadSelectedMsgName = pyqtSignal(str)

    def __init__(self):
        super(DbHandler, self).__init__()
        self._can_db_inst = 0
        self._current_msg = 0
        self._msg_data = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        self._signal_collection = set()
        self._fileData = list()
        self._fileParsedData = dict()
        self._fileParsedMsgName = dict()
        self._fileSignalsData = dict()
        self._signal_name_list = dict()
        self._log_data = dict()

    def load_db(self, path_to_db):
        """Load CAN DB file"""
        print("Path to dbc: {}".format(path_to_db))
        self._can_db_inst = cantools.database.load_file('test_db.dbc')

    @pyqtSlot(set)
    def get_msg_name_list(self):
        msg_name_set = canToolsWrapper.get_all_messages(self._can_db_inst)
        msg_name_id = set()
        for name in msg_name_set:
            message = self._can_db_inst.get_message_by_name(name)
            signals = message.signals
            for signal_name in signals:
                self._signal_name_list[signal_name] = name
            id = message.frame_id
            msg_name_id.add(hex(id) + '   ' + name)
        return msg_name_id

    def get_message_by_name(self, message_name):
        """Return message signals object"""
        self._signal_collection.clear()  # clean collection
        msg_name_str = message_name.split()
        message = self._can_db_inst.get_message_by_name(msg_name_str[1])
        self._current_msg = message
        return message

    def create_signal_updater(self, name, options):
        """Make signal and save default value"""
        signal_obj = SignalData(name, options, self.msg_updated)

        try:
            first_key = list(options.keys())[0]
            signal_obj.set_current_value(options[first_key])
        except TypeError as te:
            print('Skip this signal TypeError {} error: {}'.format(name, str(te)))
            signal_obj.set_current_value('not any options')
        except AttributeError as te:
            print('Skip this signal TypeError {} error: {}'.format(name, str(te)))
            signal_obj.set_current_value(0)

        self._signal_collection.add(signal_obj)
        return signal_obj

    @pyqtSlot(str)
    def load_signals_data(self, msg_name):
        signal_set = set()
        message = self.get_message_by_name(msg_name)

        print(msg_name)

        msg_payload = message.signals

        try:
            for signal in msg_payload:
                """Put signals options into conf widget"""
                if signal is None:
                    print("Catch None!!!!!!!!!!!!!!!!!!!!!!!!!")
                if signal.choices is None:
                    print("Catch choice = None!!!!!!!!!!!!!!!!")
                    print("Min " + str(signal.minimum) + " Max " + str(signal.maximum))
                    if signal.minimum is not None:
                        if signal.maximum is not None:
                            options_range = dict()
                            if signal.maximum > 10000:
                                signal.maximum = 10000
                            for value in range(signal.minimum, signal.maximum):
                                options_range[value] = value

                            signal_set.add(self.create_signal_updater(name=signal.name, options=options_range))
                else:
                    signal_set.add(self.create_signal_updater(name=signal.name, options=signal.choices))

        except:
            print("Catch error at load_signals_data = " + signal.name)
            print(signal.choices)

        self.loadSigDataToGui.emit(signal_set)

    def msg_updated(self):
        """Send msgDataUpdSig signal with msg raw payload"""
        data = {}
        for signal in self._signal_collection:
            data[signal.get_name()] = signal.get_value()

        try:
            self._msg_data = self._current_msg.encode(data=data, strict=False)
        except:
            print("Can not encode data")
            print(data)
        # # generate event
        data_str = ''
        for byte in self._msg_data:
            data_str = data_str + '{:02X}'.format(byte) + ':'

        self.msgDataUpdSig.emit(hex(self._current_msg.frame_id), data_str[:-1])

    @pyqtSlot(str)
    def open_can_trace(self, file_path):
        skipped_str = 0
        message_id = str()
        self._fileData.clear()
        self._fileParsedData.clear()
        self._fileSignalsData.clear()

        with open(file_path, "r") as file:
            self._fileData = file.readlines()
            for file_str in self._fileData:
                try:
                    split_data = file_str.split()
                    time = float(split_data[0])
                    message_id = split_data[2]
                    payload_index = file_str.find('d 8')+4
                    payload = file_str[payload_index:payload_index+23].strip()
                    msg_payload_data = bytearray.fromhex(payload)

                except:
                    # print("No msg here:" + file_str[:20].strip())
                    continue

                try:
                    if len(message_id) < 5:
                        msg = self._can_db_inst.decode_message(int(message_id, 16), msg_payload_data)
                        msg_obj = self._can_db_inst.get_message_by_frame_id(message_id)
                    else:
                        msg = self._can_db_inst.decode_message(message_id.strip(), msg_payload_data)
                        msg_obj = self._can_db_inst.get_message_by_name(message_id)

                    self._fileParsedMsgName[time] = msg_obj.name
                    self._fileParsedData[time] = msg
                    for signal_name in msg:
                        if signal_name in self._fileSignalsData:
                            self._fileSignalsData[signal_name][time] = msg[signal_name]
                        else:
                            self._fileSignalsData[signal_name] = dict()
                            self._fileSignalsData[signal_name][time] = msg[signal_name]

                    if message_id in self._log_data:
                        self._log_data[message_id].append(file_str)
                    else:
                        self._log_data[message_id] = list()
                        self._log_data[message_id].append(file_str)

                except:
                    skipped_str = skipped_str + 1
                    print("msg cat not decoded:" + file_str[:12].strip() + ' id ' + message_id.strip() + ' msg ' + str(msg_payload_data))

            self.loadCANTrace.emit(self._fileData, self._log_data)

            # if 'EmgcyCallFalt_B_Dsply' in self._fileSignalsData:
            #     sig_dat = self._fileSignalsData['EmgcyCallFalt_B_Dsply']
            #     for dat in sig_dat:
            #         print(str(dat) + ';' + str(sig_dat[dat]) + ";")
            #
            # print("SIGNAL DATA")
            # for signal_name_cashed in self._fileSignalsData:
            #     print("Name:" + str(signal_name_cashed) + " val:" + str(self._fileSignalsData[signal_name_cashed]))
            # Used for ticket
            # if 'EmgcyCallFalt_B_Dsply' in self._fileSignalsData:
            #     if 'EmgcyCallHmi_D_Stat' in self._fileSignalsData:
            #         sig_dat = self._fileSignalsData['EmgcyCallHmi_D_Stat']
            #         for dat in sig_dat:
            #             print(str(dat) + ';' + str(sig_dat[dat]) + ";" +
            #                   str(self._fileSignalsData['EmgcyCallFalt_B_Dsply'][dat]) + ';')

    @pyqtSlot(str)
    def show_signal_values(self, signal_name):
        self.loadSignalValsToGui.emit(self._fileSignalsData[signal_name])

    @pyqtSlot(str)
    def parce_can_str(self, can_str):
        try:
            time = float(can_str[:12].strip())
            self.loadMsgSigVal.emit(self._fileParsedData[time])
            self.loadSelectedMsgName.emit(self._fileParsedMsgName[time])
        except:
            print("Failed:" + can_str[:12].strip())
