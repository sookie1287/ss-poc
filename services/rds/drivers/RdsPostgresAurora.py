
from .RdsCommon import RdsCommon

class RdsPostgresAurora(RdsCommon):
    def __init__(self, db, rdsClient):
        super().__init__(db, rdsClient)
        self.loadParameterInfo()
        