import abc
from typing import List, Dict, Optional, Set
from pheweb.serve.components.model import ComponentCheck, ComponentStatus


class GeneAliases:
    @abc.abstractmethod
    def get_gene_aliases(self, gene: str) -> Set[str]:
        """
        Return matches
        """
        raise NotImplementedError


class AutocompleterDAO(ComponentCheck):
    @abc.abstractmethod
    def autocomplete(self, query: str) -> List[Dict[str, str]]:
        """
        Return matches
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_best_completion(self, query: str) -> Optional[Dict[str, str]]:
        """
        Return matches
        """
        raise NotImplementedError

    def get_status(
        self,
    ) -> ComponentStatus:
        try:
            self.autocomplete("APOE")
        except Exception as ex:
            return ComponentStatus.from_exception(ex)
        return ComponentStatus(True, [])


# Max number of results to return
QUERY_LIMIT: int = 10
