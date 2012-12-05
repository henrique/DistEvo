class VM:
    ip = ""
    vmtype = ""
    paraSigma = 0.0
    paraEA = 0.0
    result = 0.0
    
    def __init__(self, ip, vmtype, paraSigma, paraEA, result):
        self.ip = ip
        self.vmtype = vmtype
        self.paraSigma = paraSigma
        self.paraEA = paraEA
        self.result = result
    
    def __str__(self):
        return '\
        VM\r\n\
        ip: '+self.ip+'\r\n\
        vmtype: '+self.vmtype+'\r\n\
        paraSigma '+str(self.paraSigma)+'\r\n\
        paraEA '+str(self.paraEA)+'\r\n\
        result '+str(self.result)
    
    def getJSON(self):
        s = {'ip': self.ip, 'vmtype': self.vmtype, 'paraSigma': self.paraSigma, 'paraEA': self.paraEA, 'result': self.result}
        return s