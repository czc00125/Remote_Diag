from Client import Ui_MainWindow
from Settings import Ui_Form
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QMessageBox, QFileDialog
from PyQt5 import QtCore
import sys
import socket
from PyQt5.QtNetwork import QTcpSocket
import os
import time
import datetime


class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.actionSettings.triggered.connect(self.pop_settings_window)
        self.pushButton_Connect.clicked.connect(self.tcp_connect)
        self.pushButton_Disconnect.clicked.connect(self.tcp_disconnect)
        self.pushButton_Send.clicked.connect(self.send_socket)
        self.pushButton_DefaultSession.clicked.connect(self.send_1001)
        self.pushButton_ProgramSession.clicked.connect(self.send_1002)
        self.pushButton_ExtendedSession.clicked.connect(self.send_1003)
        self.pushButton_BoschSession.clicked.connect(self.send_1060)
        self.pushButton_UnlockLevel1.clicked.connect(self.send_2701)
        self.pushButton_UnlockLevel2.clicked.connect(self.send_2703)
        self.pushButton_BoschUnlock.clicked.connect(self.send_2760)
        self.pushButton_ClearDTCs.clicked.connect(self.send_14FFFFFF)
        self.pushButton_ReadDTCs.clicked.connect(self.send_190209)
        self.checkBox_CANFD.toggled.connect(self.set_canfd)
        self.checkBox_CAN.toggled.connect(self.set_can)
        self.checkBox_PhysicalAddr.toggled.connect(self.set_physicaladdr)
        self.checkBox_FunctionAddr.toggled.connect(self.set_functionaddr)
        self.radioButton_TesterPresent.toggled.connect(self.set_tester_present)
        self.pushButton_ClearLog.clicked.connect(self.clear_log)
        self.pushButton_SaveLog.clicked.connect(self.save_log)
        #self.pushButton.clicked.connect(self.receive_data_parse)

        self.serverIP = ''
        self.port = 1
        self.PhysicalID = ''
        self.FunctionID = ''
        self.ResponseID = ''
        self.DTC_excel_path = ''
        self.save_config_path = ''
        self.save_log_path = ''
        self.security_dll_path = ''
        self.canType = '0'
        self.testerPresentFlag = 0
        self.checkBox_CAN.setChecked(True)
        self.addrMethod = '0'
        self.checkBox_PhysicalAddr.setChecked(True)
        self.showTitleFlag = 0
        self.isConnectedToServer = 0

        self.lineEdit_InputData.setEnabled(False)
        self.pushButton_Send.setEnabled(False)
        self.pushButton_DefaultSession.setEnabled(False)
        self.pushButton_ProgramSession.setEnabled(False)
        self.pushButton_ExtendedSession.setEnabled(False)
        self.pushButton_BoschSession.setEnabled(False)
        self.radioButton_TesterPresent.setEnabled(False)
        self.pushButton_UnlockLevel1.setEnabled(False)
        self.pushButton_UnlockLevel2.setEnabled(False)
        self.pushButton_BoschUnlock.setEnabled(False)

        self.pushButton_Connect.setEnabled(False)
        self.pushButton_Disconnect.setEnabled(False)
        self.pushButton_ReadDTCs.setEnabled(False)
        self.pushButton_ClearDTCs.setEnabled(False)

        # self.form1 = QWidget()
        # self.ui1 = Ui_Form()
        # self.ui1.setupUi(self.form1)

    def tcp_disconnect(self):
        if not self.isConnectedToServer:
            return

        self.sock.connected.disconnect()
        # try:
        #     self.sock.connected.disconnect()
        # except:
        #     pass
        #
        # try:
        #     self.sock.disconnected.disconncet()
        # except:
        #     pass
        #
        # try:
        #     self.sock.readyRead.disconncet()
        # except:
        #     pass
        #
        # try:
        #     self.sock.bytesWritten.disconncet()
        # except:
        #     pass
        self.sock.close()
        self.pushButton_Connect.setEnabled(True)
        self.pushButton_Disconnect.setEnabled(False)

        self.lineEdit_InputData.setEnabled(False)
        self.pushButton_Send.setEnabled(False)
        self.pushButton_DefaultSession.setEnabled(False)
        self.pushButton_ProgramSession.setEnabled(False)
        self.pushButton_ExtendedSession.setEnabled(False)
        self.pushButton_BoschSession.setEnabled(False)
        self.radioButton_TesterPresent.setEnabled(False)
        self.pushButton_UnlockLevel1.setEnabled(False)
        self.pushButton_UnlockLevel2.setEnabled(False)
        self.pushButton_BoschUnlock.setEnabled(False)
        self.pushButton_ReadDTCs.setEnabled(False)
        self.pushButton_ClearDTCs.setEnabled(False)
        self.isConnectedToServer = False

    def tcp_connect(self):
        if self.serverIP == '' or self.port == 1:
            QMessageBox.information(self, 'Message', 'Please config IP and Port of server first', QMessageBox.Ok,
                                    QMessageBox.Ok)
            return False
        self.sock = QTcpSocket(self)
        host_ip_addr = self.serverIP
        port = self.port
        #self.textBrowser_Log.append('Connecting to {} on port {}'.format(host_ip_addr, port))
        self.update_event_log('Connecting to {} on port {}'.format(host_ip_addr, port))
        self.sock.connectToHost(host_ip_addr, port)
        if not self.sock.waitForConnected(2500):
            msg = self.sock.errorString()
            #self.textBrowser_Log.append(msg)
            self.update_event_log(msg)
            QMessageBox.critical(self, "Error", msg)
            return False

        self.sock.connected.connect(self.on_socket_connected)
        self.sock.disconnected.connect(self.on_socket_disconnected)
        self.sock.readyRead.connect(self.on_socket_receive)
        self.sock.bytesWritten.connect(self.on_socket_transmit)
        self.update_event_log('Connect success !')
        self.isConnectedToServer = 1
        self.pushButton_Connect.setEnabled(False)
        self.pushButton_Disconnect.setEnabled(True)

        self.lineEdit_InputData.setEnabled(True)
        self.pushButton_Send.setEnabled(True)
        self.pushButton_DefaultSession.setEnabled(True)
        self.pushButton_ProgramSession.setEnabled(True)
        self.pushButton_ExtendedSession.setEnabled(True)
        self.pushButton_BoschSession.setEnabled(True)
        self.radioButton_TesterPresent.setEnabled(True)
        self.pushButton_UnlockLevel1.setEnabled(True)
        self.pushButton_UnlockLevel2.setEnabled(True)
        self.pushButton_BoschUnlock.setEnabled(True)
        self.pushButton_ReadDTCs.setEnabled(True)
        self.pushButton_ClearDTCs.setEnabled(True)

    def on_socket_connected(self):
        pass

    def on_socket_disconnected(self):
        #self.textBrowser_Log.append('Disconnected from server')
        self.update_event_log('Disconnected from server')
        self.pushButton_Connect.setEnabled(True)
        self.pushButton_Disconnect.setEnabled(False)

    def on_socket_receive(self):
        rxData = self.sock.readAll()
        print('type(rxData)', type(rxData))  # QByteArray
        data_string = rxData.data().decode('gbk')  # utf-8
        print('data_string:', data_string)
        #data_string = 'Timestamp: 1606098797.167605        ID: 079b    S                DLC:  8    03 7f 10 7e aa aa aa aa     Channel: can0'
        id, dlc, rx_data_str = self.rx_data_parse(data_string)
        if self.showTitleFlag == 0:
            self.textBrowser_Log.append('        Time      ' + '    Dir   ' + '  ID   ' + ' Data')
        runtime = time.perf_counter()
        runtime = datetime.timedelta(seconds=runtime)
        self.textBrowser_Log.append(str(runtime) + '   Rx   ' + id + '    ' + rx_data_str)
        self.showTitleFlag = 1

    def rx_data_parse(self, data_string):
        print(data_string.split())
        print(type(data_string.split()))

        data_list = data_string.split()
        id = data_list[3].lstrip('0')
        dlc = data_list[6]
        can_data_list = data_list[-10:-2]

        print('Rx ID: ', data_list[3])
        print('RX DLC: ', data_list[6])
        print('RX Data: ', data_list[-10:-2])
        temp = ''
        for i in range(int(dlc)):
            temp = temp + can_data_list[i]

        rx_data_str = temp
        print('rx_data_str: ', rx_data_str)

        return id, dlc, rx_data_str


    def on_socket_transmit(self):  # After buff bytes writen
        pass
        #self.textBrowser_Log.append('1')

    def send_socket(self):
        input_data = self.lineEdit_InputData.text()
        self.sendMessage(input_data)


    def receive_data_parse(self, data_string):
        data_string = '5902091008708'
        #data_int = int(data_string)
        hex = self.str_to_hex(data_string)
        print(hex)
        # if '590209' in data_string:
        #     print(1)

    def str_to_int(s):
        print(s)
        return ' '.join([hex(ord(c)).replace('0x', '') for c in s])


    def send_1001(self):
        self.sendMessage('1001')

    def send_1002(self):
        self.sendMessage('1002')

    def send_1003(self):
        self.sendMessage('1003')

    def send_1060(self):
        self.sendMessage('1060')

    def send_2701(self):
        self.sendMessage('2701')

    def send_2703(self):
        self.sendMessage('2703')

    def send_2760(self):
        self.sendMessage('2760')

    def send_190209(self):
        self.sendMessage('190209')

    def send_14FFFFFF(self):
        self.sendMessage('14FFFFFF')

    def update_event_log(self, message):
        self.textBrowser_Log.append(message)
        self.showTitleFlag = 0

    def clear_log(self):
        self.textBrowser_Log.clear()
        self.showTitleFlag = 0

    def save_log(self):
        text = self.textBrowser_Log.toPlainText()
        text_string = str(text)
        home_dir = os.getcwd()
        save_log_path, _ = QFileDialog.getSaveFileName(self,
                                                          'Save log file',
                                                          home_dir,
                                                          'TXT Files (*.txt);;All Files (*)')
        print('save_log_path: ', save_log_path)

        if save_log_path != '':
            self.save_log_path = save_log_path
            with open(save_log_path, 'w') as cf:  # 'w' - overwrite and new create, 'a' - append
                cf.write('{}'.format(text_string))
            self.update_event_log('Log is saved, path: ' + save_log_path)
        else:
            pass  # cancel and do nothing

    def sendMessage(self, message):
        if message != '':
            if self.showTitleFlag == 0:
                self.textBrowser_Log.append('        Time      ' + '    Dir   ' + '  ID   ' + ' Data')
            print('self.testerPresentFlag:', self.testerPresentFlag)
            valid_data_length = int(len(message)/2)
            str_valid_data_lenth = '0' + str(valid_data_length)
            whole_message = self.canType + str(self.testerPresentFlag) + self.addrMethod + self.PhysicalID + self.FunctionID + self.ResponseID + str_valid_data_lenth + message
            message_coded = whole_message.encode('gbk')
            runtime = time.perf_counter()
            runtime = datetime.timedelta(seconds=runtime)
            if self.addrMethod == '0':
                tx_id = self.PhysicalID
            else:
                tx_id =self.FunctionID
            self.sock.write(message_coded)
            print('Actual send: ', message_coded)
            message = str_valid_data_lenth + message
            self.textBrowser_Log.append(str(runtime) + '   Tx   ' + tx_id + '    ' + message)
            self.showTitleFlag = 1
        else:
            pass

    def set_canfd(self):
        if self.checkBox_CANFD.isChecked() == 1:
            self.canType = '1'
            self.checkBox_CAN.setChecked(False)
        else:
            if self.canType == '1':
                self.checkBox_CANFD.setChecked(True)

    def set_can(self):
        if self.checkBox_CAN.isChecked() == 1:
            self.canType = '0'
            self.checkBox_CANFD.setChecked(False)
        else:
            if self.canType == 0:
                self.checkBox_CAN.setChecked(True)

    def set_functionaddr(self):
        if self.checkBox_FunctionAddr.isChecked() == 1:
            self.addrMethod = '1'
            self.checkBox_PhysicalAddr.setChecked(False)
        else:
            if self.addrMethod == '1':
                self.checkBox_FunctionAddr.setChecked(True)

    def set_physicaladdr(self):
        if self.checkBox_PhysicalAddr.isChecked() == 1:
            self.addrMethod = '0'
            self.checkBox_FunctionAddr.setChecked(False)
        else:
            if self.addrMethod == '0':
                self.checkBox_PhysicalAddr.setChecked(True)

    def set_tester_present(self):
        if self.radioButton_TesterPresent.isChecked() == 1:
            print('set tester_present: 1')
            self.testerPresentFlag = 1
        else:
            print('set tester_present: 0')
            self.testerPresentFlag = 0

    def pop_settings_window(self):  # no show anything in second click
        self.form1 = QWidget()
        self.ui1 = Ui_Form()
        self.ui1.setupUi(self.form1)
        self.form1.show()
        self.ui1.lineEdit_IP.setInputMask('000.000.000.000;_')  # TODO
        if self.serverIP != '':
            self.ui1.lineEdit_IP.setText(self.serverIP)
            self.ui1.lineEdit_Port.setText(str(self.port))
            self.ui1.lineEdit_PhysicalID.setText(self.PhysicalID)
            self.ui1.lineEdit_FunctionID.setText(self.FunctionID)
            self.ui1.lineEdit_ResponseID.setText(self.ResponseID)
            self.ui1.lineEdit_Dispaly_DTCExcel_Path.setText(self.DTC_excel_path)
            self.ui1.lineEdit_Display_SecurityDll_Path.setText(self.security_dll_path)

        self.ui1.lineEdit_IP.editingFinished.connect(self.save_serverIP)
        self.ui1.lineEdit_Port.editingFinished.connect(self.save_port)
        self.ui1.lineEdit_PhysicalID.editingFinished.connect(self.save_physicalid)
        self.ui1.lineEdit_FunctionID.editingFinished.connect(self.save_functionid)
        self.ui1.lineEdit_ResponseID.editingFinished.connect(self.save_responseid)
        self.ui1.toolButton_Load_DTCExcel.clicked.connect(self.load_dtc_excel)
        self.ui1.pushButton_Load_ConfigFie.clicked.connect(self.load_config_file)
        self.ui1.pushButton_Save_ConfigFile.clicked.connect(self.save_config_file)
        self.ui1.toolButton_Load_Security_Dll.clicked.connect(self.load_security_dll)

    def save_serverIP(self):
        text = self.ui1.lineEdit_IP.text()
        self.serverIP = self.ui1.lineEdit_IP.text()
        print('self.serverIP:', self.serverIP)
        if self.port != 1 and self.serverIP != '':
            self.pushButton_Connect.setEnabled(True)
            self.pushButton_Disconnect.setEnabled(False)
        else:
            pass

    def save_port(self):
        port = self.ui1.lineEdit_Port.text()
        if port != '':
            self.port = int(port)
            print('self.port:', self.port)
            if self.port != 1 and self.serverIP != '':
                self.pushButton_Connect.setEnabled(True)
                self.pushButton_Disconnect.setEnabled(False)
            else:
                pass
        else:
            pass

    def save_physicalid(self):
        text = self.ui1.lineEdit_PhysicalID.text()
        if text != '':
            self.PhysicalID = text
            print('self.PhysicalID:', self.PhysicalID)
        else:
            pass

    def save_functionid(self):
        text = self.ui1.lineEdit_FunctionID.text()
        if text != '':
            self.FunctionID = text
            print('self.FunctionID:', self.FunctionID)
        else:
            pass

    def save_responseid(self):
        text = self.ui1.lineEdit_ResponseID.text()
        if text != '':
            self.ResponseID = text
            print('self.FunctionID:', self.ResponseID)
        else:
            pass

    def load_dtc_excel(self):
        home_dir = os.getcwd()
        dtc_excel_path, _ = QFileDialog.getOpenFileName(
            self.form1,  # parent window is settings windows
            'Select the DTC list excel',
            home_dir,
            'All Files (*.*);;XLSX File (*.xlsx);;XLS File (*.xls)'
        )
        if dtc_excel_path != '':
            self.DTC_excel_path = dtc_excel_path
            self.ui1.lineEdit_Dispaly_DTCExcel_Path.setText(self.DTC_excel_path)
            #self.textBrowser_Log.append('DTC name excel is loaded, path: \n{}'.format(self.DTC_excel_path))
            self.update_event_log('DTC name excel is loaded, path: \n{}'.format(self.DTC_excel_path))
            # create a new thread to parse excel and generate dtc name, TODO

        else:
            pass

    def load_security_dll(self):
        home_dir = os.getcwd()
        security_dll_path, _ = QFileDialog.getOpenFileName(
            self.form1,  # parent window is settings windows
            'Select the DTC list excel',
            home_dir,
            'DLL File (*.dll);;All Files (*.*)'
        )
        if security_dll_path != '':
            self.security_dll_path = security_dll_path
            self.ui1.lineEdit_Display_SecurityDll_Path.setText(self.security_dll_path)
            #self.textBrowser_Log.append('Security dll is loaded, path: \n{}'.format(self.security_dll_path))
            self.update_event_log('Security dll is loaded, path: \n{}'.format(self.security_dll_path))
            # create a new thread to parse dll and generate key, TODO

        else:
            pass

    def load_config_file(self):
        home_dir = os.getcwd()
        config_path, status = QFileDialog.getOpenFileName(
            self.form1,  # parent window is settings windows
            'Select config file',
            home_dir,
            'TEXT File (*.txt);;All Files (*.*)'
        )
        print('config_path: ', config_path)
        print('status: ', status)
        if config_path != '':
            with open(config_path, 'r') as file_object:
                all_lines = file_object.readlines()
                print('all_lines: ', all_lines)
            for line in all_lines:
                if line == '\n':
                    continue
                line_string_list = line.split(': ')
                before_string = line_string_list[0]
                content = line_string_list[1].split('\n')[0]
                if 'Server IP' in before_string:
                    print('content:', content)
                    self.serverIP = content
                    self.ui1.lineEdit_IP.setText(content)

                    if self.port != 1 and self.serverIP != '':
                        self.pushButton_Connect.setEnabled(True)
                        self.pushButton_Disconnect.setEnabled(False)
                    else:
                        pass

                elif 'Port' in before_string:
                    self.port = int(content)
                    print('content:', content)
                    self.ui1.lineEdit_Port.setText(content)

                    if self.port != 1 and self.serverIP != '':
                        self.pushButton_Connect.setEnabled(True)
                        self.pushButton_Disconnect.setEnabled(False)
                    else:
                        pass

                elif 'Physical ID' in before_string:
                    self.PhysicalID = content
                    print('content:', content)
                    self.ui1.lineEdit_PhysicalID.setText(content)

                elif 'Function ID' in before_string:
                    self.FunctionID = content
                    print('content:', content)
                    self.ui1.lineEdit_FunctionID.setText(content)

                elif 'Response ID' in before_string:
                    self.ResponseID = content
                    print('content:', content)
                    self.ui1.lineEdit_ResponseID.setText(content)

                elif 'Security Dll path' in before_string:  # TODO
                    self.security_dll_path = content
                    self.ui1.lineEdit_Display_SecurityDll_Path.setText(content)

                elif 'DTC name excel path' in before_string:
                    self.DTC_excel_path = content
                    print('content:', content)
                    self.ui1.lineEdit_Dispaly_DTCExcel_Path.setText(content)

                else:
                    QMessageBox.information(self.form1, 'Message', 'Please load correct config txt', QMessageBox.Ok,
                                            QMessageBox.Ok)
                    break
            self.update_event_log('Loaded config file: ' + config_path)

    def save_config_file(self):
        if self.serverIP == '' or self.port == 1 or self.PhysicalID == '' or self.FunctionID == '' or self.ResponseID == '' or self.security_dll_path == '' or self.DTC_excel_path == '':
            QMessageBox.information(self.form1, 'Message', 'Please check blank in content', QMessageBox.Ok, QMessageBox.Ok)
            return
        home_dir = os.getcwd()
        save_config_path, _ = QFileDialog.getSaveFileName(self.form1,
                                                       'Save config file',
                                                       home_dir,
                                                       'TXT Files (*.txt);;All Files (*)')
        print('save_config_path: ', save_config_path)
        if save_config_path != '':
            self.save_config_path = save_config_path
            with open(save_config_path, 'w') as cf:  # 'w' - overwrite and new create, 'a' - append
                cf.write('Server IP: ' + self.serverIP + '\n' +
                         '       Port: ' + str(self.port) + '\n' +
                         'Physical ID: ' + self.PhysicalID + '\n' +
                         'Function ID: ' + self.FunctionID + '\n' +
                         'Response ID: ' + self.ResponseID + '\n' +
                         'Security Dll path: ' + self.security_dll_path + '\n' +
                         'DTC name excel path: ' + self.DTC_excel_path + '\n'
                         )
            #self.textBrowser_Log.append('Config file is saved, path:\n' + str(save_config_path))
            self.update_event_log('Config file is saved, path:\n' + str(save_config_path))
        else:
            pass  # cancel and do nothing


# class SocketThreads(QtCore.QThread):
#
#     trigger = QtCore.pyqtSignal(str)
#
#     def __init__(self, ip_string, port_string, input_data, parent=None):
#         super(SocketThreads, self).__init__(parent)
#         self.ip_string = ip_string
#         self.port_string = port_string
#         self.input_data = input_data
#         self.Rx_message = ''
#
#     def run(self):
#         if (self.ip_string != '') and (self.port_string != ''):  # TODO,ip_string and Port_string format check
#             port_int = int(self.port_string)
#             s = socket.socket()
#             self.Rx_message = 'Start to connect Server: IP - ' + self.ip_string + ' Port - ' + self.port_string + '...'
#             self.trigger.emit(self.Rx_message)
#             try:
#                 s.connect((self.ip_string, port_int))  # connect server
#                 self.Rx_message = '......Success......'
#                 self.trigger.emit(self.Rx_message)
#             except:
#                 print('Failed')  # TODO, or pop a warning window
#                 self.Rx_message = 'Failed, please check the config of IP and Port or network connection'
#                 self.trigger.emit(self.Rx_message)
#                 return
#             while True:
#                 #data = input('data: ')
#                 data = self.input_data  # first frame is empty,TODO
#                 if data != '':
#                     s.send(data.encode())  # send information
#                     recv = s.recv(1024).decode()
#                     print(recv)
#                     print('type of recv: ', type(recv))
#                     self.Rx_message = recv
#                     self.trigger.emit(self.Rx_message)
#                 else:
#                     pass  # no send, only connect
#                 if data == 'close':
#                     break
#             s.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainform = MainForm()
    mainform.show()
    sys.exit(app.exec_())
