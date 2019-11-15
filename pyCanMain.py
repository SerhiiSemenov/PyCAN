import ics
import sys
import appGUI
import dbHandler
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, QThreadPool

# msg = ics.SpyMessage() # Setup the message
# msg.ArbIDOrHeader = 0x411  # CAN ID
# msg.NetworkID = ics.NETID_HSCAN # Channel 1 on the ValueCAN
# msg.Data = (0x12, 0x34, 0x56, 0x78, 0x0, 0x0, 0x0, 0x0) # CAN Data field

# ics.transmit_messages(device, msg) # Transmit the message

def receive_can(device,db):
    while (1):
        msgs, error_count = ics.get_messages(device)
        # print("Received {} messages with {} errors.".format(len(msgs), error_count))
        if error_count == 0:
            for i, m in enumerate(msgs):
                print('ID:{:>3}'.format(hex(m.ArbIDOrHeader)), end='')
                print('\tName: {}'.format(db.get_msg_by_id(m.ArbIDOrHeader).name), end='')
                print('\t\tData: {}'.format([hex(x) for x in m.Data]))
                #mssage_data = db.decode_message(frame_id_or_name=m.ArbIDOrHeader, data=bytes(m.Data))
                #print(mssage_data)

        else:
            print("Received {} messages with {} errors.".format(len(msgs), error_count))


def main():

    # device = ics.find_devices()[0]
    # ics.open_device(device)
    # load db
    # db = cantools.database.load_file('test_db.dbc')
    #
    # receive_can(device, db)
    #
    # messages_list = db.get_message_by_name('ABS_Signals_HS4')
    # messages_list = canToolsWrapper.get_all_messages(db)

    canDb = dbHandler.DbHandler()
    # canDb.load_db('test_db.dbc')
    canDb.load_db('Y2018_CGEA1.3_CMDB_B_v18.07A_112718_HS4.dbc')

    my_thread = QThread()
    my_thread.start()

    app = QApplication(sys.argv)
    mainWindow = appGUI.GuiWindow()
    mainWindow.load_message_list(canDb.get_msg_name_list())
    mainWindow.requestSignalDataSig.connect(lambda msg_name: canDb.load_signals_data(msg_name))
    mainWindow.openNewFile.connect(lambda file_name: canDb.open_can_trace(file_name))
    mainWindow.requestForMsgDecode.connect(lambda can_str: canDb.parce_can_str(can_str))

    canDb.msgDataUpdSig.connect(lambda msg_id, data_str: mainWindow.update_msg_data(msg_id, data_str))
    canDb.loadSigDataToGui.connect(lambda sig_collection: mainWindow.pop_signals_to_gui(sig_collection))
    canDb.loadCANTrace.connect(lambda data_dict: mainWindow.upload_file_data(data_dict))
    canDb.loadMsgSigVal.connect(lambda sig_dict: mainWindow.show_message_payload(sig_dict))
    canDb.loadSelectedMsgName.connect(lambda msg_name: mainWindow.show_message_name(msg_name))
    canDb.loadSignalsCash.connect(lambda signals_data: mainWindow.load_signals_cash(signals_data))
    canDb.moveToThread(my_thread)
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
