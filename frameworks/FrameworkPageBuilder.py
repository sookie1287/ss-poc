import json

from services.PageBuilder import PageBuilder
from frameworks.FTR.FTR import FTR

class FrameworkPageBuilder(PageBuilder):
    FRAMEWORK_JS_LIB = [
        "/jquery.dataTables.min.js",
        "-bs4/js/dataTables.bootstrap4.min.js",
        "-responsive/js/dataTables.responsive.min.js",
        "-responsive/js/responsive.bootstrap4.min.js",
        "-buttons/js/dataTables.buttons.min.js",
        "-buttons/js/buttons.bootstrap4.min.js",
        "-buttons/js/buttons.html5.min.js",
        "-buttons/js/buttons.print.min.js",
        "-buttons/js/buttons.colVis.min.js"
    ]
    FRAMEWORK_CSS_LIB = [
        "bs4/css/dataTables.bootstrap4.min.css",
        "responsive/css/responsive.bootstrap4.min.css",
        "buttons/css/buttons.bootstrap4.min.css"
    ]
    
    HTML_TABLE_ID = 'screener-framework'
    
    def __init__(self, service=None, reporter=None):
        framework = service
        super().__init__(framework, reporter)
        
        if framework in globals():
            obj = globals()[framework](reporter)
            
            self.framework = obj
            self.framework.readFile()
            
            self.initCSS()
            self.initJSLib()
            self.populate()
            self.addDataTableJS()
        else:
            exit('[Framework] -{}- not found, script halted'.format(framework))
    
    def populate(self):
        self.headerInfo = self.framework.getMetaData()
    
    def populateFrameworkData(self):
        pass
    
    def setFrameworkTitle(self, titleArr):
        self.fwTitle = titleArr
        
    def setFrameworkDetail(self, detailArr):
        self.fwDetail = detailArr
    
    def initJSLib(self):
        pref = 'plugins/datatables'
        for js in self.FRAMEWORK_JS_LIB:
            self.addJSLib(pref + js)
    
    def initCSS(self):
        pref = "plugins/datatables-"
        for css in self.FRAMEWORK_CSS_LIB:
            self.addCSSLib(pref + css)
        pass

    def buildContentSummary(self):
        outp = []
        self.setFrameworkDetail(self.framework.generateMappingInformation())
        
        outp.append("<h3>{}</h3><h4>{}</h4>".format(self.headerInfo['fullname'], self.headerInfo['description']))
        outp.append("<a href='{}' target=_blank rel='noopener noreferrer'>Read more</a>".format(self.headerInfo['_']))
        return outp
    
    def buildContentDetail(self):
        outp = []
        items = []
        # tabTitle = self.fwTitle
        self._hookPreBuildContentDetail()
        
        item = self.generateCard(pid=self.headerInfo['shortname'], html=self.customBuildTableHTML(), cardClass='warning', title=self.generateTitleWithCategory('Framework', self.headerInfo['fullname'], self.headerInfo['shortname']), titleBadge='', collapse=False, noPadding=False)
        items.append([item, ''])
        
        outp.append(self.generateRowWithCol(size=12, items=items, rowHtmlAttr="data-context=detail"))
        
        return (outp)
        
    # To be overwrite by custom class
    def _hookPreBuildContentDetail(self):
        pass
    
    def customBuildTableHTML(self):
        outp = []
        
        ##Build Header
        s = "<table id='{}' class='table table-bordered table-striped'> <thead><tr>".format(self.HTML_TABLE_ID)
        for _h in ['Category', 'Rule ID', 'Compliance Status', 'Description', 'Reference']:
            s += "<th>" + _h + "</th>"
        s += "</tr></thead>"
        outp.append(s)
        
        s = "<tbody>"
        for rows in self.fwDetail:
            s += "<tr>"
            for i, col in enumerate(rows):
                ## Bad Logic, but works for now
                tmp = col
                if i == 2:
                    s += self.formatComplyCell(col)
                else: 
                    s += "<td>" + col + "</td>"
                
            s+= "</tr>"
        s += "</tbody></table>"
        outp.append(s)
        return "\n".join(outp)
    
    def addDataTableJS(self):
        s = '''
$("#{htmlID}").DataTable({{
      "responsive": true, "lengthChange": true, "autoWidth": false,
      "pageLength": 50,
      "buttons": ["copy", "csv", "colvis"]
    }}).buttons().container().appendTo('#{htmlID}_wrapper .col-md-6:eq(0)');
'''.format(htmlID=self.HTML_TABLE_ID)
        
        self.addJS(s)
        
    def formatComplyCell(self, col):
        # 0 = No Check available
        # 1 = Comply
        #-1 = Not Comply
        palette = "bg-info" 
        s = "Not Available"
        if col == 1:
            palette = "bg-success"
            s = "Compliant"
        elif col == -1:
            palette = "bg-danger"
            s = "Need Attention"
            
        return "<td class='{} color-palette'>{}</td>".format(palette, s)
        
if __name__ == "__main__":
    import constants as _C
    from utils.Config import Config
    
    Config.init()
    Config.set('cli_services', {'ec2': 2, 'iam': 1})
    Config.set('cli_frameworks', ['FTR'])
    Config.set('cli_regions', ['ap-southeast-1'])
    
    samples = [['Main', 'ARC-002', 0, [], []], ['Main', 'ARC-003', -1, "<dl><dt><i class='fas fa-times'></i> [rootMfaActive]</dt><dd>Enable MFA on root user<br><small>{'GLOBAL': ['User::<b>root_id</b>']}</small></dd><dt><i class='fas fa-times'></i> [mfaActive]</dt><dd>Enable MFA on IAM user.<br><small>{'GLOBAL': ['User::ttttt']}</small></dd></dl>", "<a href='https://aws.amazon.com/iam/features/mfa/'>AWS Docs</a><br><a href='https://aws.amazon.com/iam/features/mfa/'>AWS Docs</a>"], ['Main', 'IAM-001', -1, "<dl><dt><i class='fas fa-times'></i> [mfaActive]</dt><dd>Enable MFA on IAM user.<br><small>{'GLOBAL': ['User::ttttt']}</small></dd></dl>", "<a href='https://aws.amazon.com/iam/features/mfa/'>AWS Docs</a>"], ['Main', 'IAM-002', 1, "<dl><dt><i class='fas fa-check'></i> [passwordLastChange90]</i></dt><dt><i class='fas fa-check'></i> [passwordLastChange365]</i></dt></dl>", ''], ['Main', 'IAM-003', -1, "<dl><dt><i class='fas fa-times'></i> [passwordPolicyWeak]</dt><dd>Set a stronger password policy<br><small>{'GLOBAL': ['Account::Config']}</small></dd><dt><i class='fas fa-check'></i> [passwordPolicy]</i></dt></dl>", "<a href='https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#configure-strong-password-policy'>AWS Docs</a>"], ['Main', 'IAM-007', 1, "<dl><dt><i class='fas fa-check'></i> [consoleLastAccess90]</i></dt><dt><i class='fas fa-check'></i> [consoleLastAccess365]</i></dt></dl>", '']]
    
    data = json.loads(open(_C.FRAMEWORK_DIR + '/api.json').read())
    o = FrameworkPageBuilder('FTR', data)
    p = o.buildPage()
    # print(p)