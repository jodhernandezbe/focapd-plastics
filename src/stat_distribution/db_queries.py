
from typing import List, Optional


class TriDatabaseFilter:

    def _filter_by_naics_code(self,
                              generator_sector_ids: Optional[List[str]] = None) -> str:
        return ""
    
    def _filter_by_chemical(self,
                            chemical_ids: List[str]) -> str:
        return ""
    
    def _filter_by_condition_of_use(self,
                                    condition_of_use_ids: List[str]) -> str:
        return ""


class CdrDatabaseQuery:
    pass
