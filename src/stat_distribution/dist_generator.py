from typing import List, Optional


class StartDistribution:
    pass


class PostRecyclingStatsGenerator:
    
    def get_stats(self) -> StartDistribution:
        return StartDistribution()


class EndOfLifeStatsGenerator:
    
    def get_stats(self,
                  plastic_sector_constraint: bool = True,
                  generator_sector_ids: Optional[List[int]] = None,
                  chemical_constraint: bool = False,
                  chemical_ids: Optional[List[str]] = None,
                  generating_condition_of_use_constraint: bool = False,
                  condition_of_use_ids: Optional[List[int]] = None,) -> StartDistribution:
        if not plastic_sector_constraint and generator_sector_ids:
            raise ValueError("Cannot specify generator_sector_ids when plastic_sector_constraint is False.")
        if not chemical_constraint and chemical_ids:
            raise ValueError("Cannot specify chemical_ids when chemical_constraint is False.")
        if not generating_condition_of_use_constraint and condition_of_use_ids:
            raise ValueError("Cannot specify condition_of_use_ids when generating_condition_of_use_constraint is False.")
        return StartDistribution()
