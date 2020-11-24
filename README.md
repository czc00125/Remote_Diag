# Remote_Diag
Remote diagnostic
Client->Server
data stream format:
'0 0 0 123 456 7df 14FFFFFF'

self.canType + str(self.testerPresentFlag) + self.addrMethod + self.PhysicalID + self.FunctionID + self.ResponseID + message

self.cantype:'0'-CAN, '1'-CANFD
str(self.testerPresentFlag): '0'-no send 3e, '1'-send 3e
self.addrMethod:'0'-physical addressing, '1'-function addressing
message: 14FFFFFF true can data
