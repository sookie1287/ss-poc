import os
import json

import constants as _C

class Framework():
    def __init__(self, data):
        self.stats = []
        self.data = data
        self.framework = type(self).__name__
        pass
    
    def getFilePath(self):
        filepath = _C.FRAMEWORK_DIR + '/' + self.framework + '/map.json'
        exists = os.path.exists(filepath)
        if not exists:
            return False
            
        return filepath
        
    def readFile(self):
        p = self.getFilePath()
        if p == False:
            print(p + " not exists, skip framework generation")
            return False
        
        self.map = json.loads(open(p).read())
    
    def getMetaData(self):
        self._hookGenerateMetaData()
        return self.map['metadata']
    
    # To be overwrite if needed
    def _hookGenerateMetaData(self):
        pass
    
    # ['Main', 'ARC-003', 0, '[iam,rootMfaActive] Root ID, Admin<br>[iam.passwordPolicy] sss', 'Link 1<br>Link2']
    def generateMappingInformation(self):
        ## Not Available, Comply, Not Comply
        summ = {}
        outp = []
        
        for title, sections in self.map['mapping'].items():
            # outp.append(self.formatTitle(title))
            # [Manual, Compliant, Not Comply]
            if not title in summ:
                summ[title] = [0,0,0]
                
            comp = 1
            for section, maps in sections.items():
                arr = []
                checks = links = ''
                if len(maps) == 0:
                    # outp.append("Framework does not has relevant check, manual intervention required")
                    comp = 0
                
                else: 
                    pre = []
                    for _m in maps:
                        tmp = self.getContent(_m)
                        pre.append(tmp)
                        
                    checks, links, comp = self.formatCheckAndLinks(pre)
                
                outp.append([title, section, comp, checks, links])
                pos = comp
                if(comp==-1):
                    pos = 2
                
                summ[title][pos] += 1    
        
        self.stats = summ
        return outp
    
    def generateGraphInformation(self):
        outp = {}
        _m = 0  # manual
        _c = 0  # compliant
        _n = 0  # not comply
        for _sect, _counter in self.stats.items():
            _m += _counter[0]
            _c += _counter[1]
            _n += _counter[2]
            
        outp['mcn'] = [_m, _c, _n]
        outp['stats'] = self.stats
        return outp
    
    ## <TODO>
    def formatTitle(self, title):
        return '<h3>' + title + '</h3>'
        
    def getContent(self, _m):
        serv, check = _m.split(".")
        if serv in self.data and check in self.data[serv]['summary']:
            tmp = self.data[serv]['summary'][check]
            
            ## <TODO>
            # format affectedResources to have better HTML output
            return {"c": check, "d": tmp['shortDesc'], "r": tmp['__affectedResources'], "l": "<br>".join(tmp['__links'])}
        else:
            return {"c": check}
            
    def formatCheckAndLinks(self, packedData):
        links = []
        comp = 1
        
        checks = ["<dl>"]
        for v in packedData:
            if "r" in v:
                tmp = ['<ul>']
                for _reg, _affected in v['r'].items():
                    tmp.append("<li><b>[" + _reg + "]</b>" + ", ".join(_affected) + "</li>")
                
                tmp.append("</ul>")
                    
                c = "<dt class='text-danger'><i class='fas fa-times'></i> [{}] - {}</dt>{}</dd>".format(v['c'], v['d'], "".join(tmp))
                links.append(v['l'])
                comp = -1
            else:
                c = "<dt class='text-success'><i class='fas fa-check'></i> [{}]</i></dt>".format(v['c'])
                
            checks.append(c)
        checks.append("</dl>")
        
        return ["".join(checks), "<br>".join(links), comp]