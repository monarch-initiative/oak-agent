from dataclasses import dataclass
from typing import List

from pydantic_ai import AgentRunError

from aurelian.dependencies.workdir import HasWorkdir


@dataclass
class LinkMLDependencies(HasWorkdir):
    #workdir: WorkDir = field(default_factory=lambda: WorkDir())

    def parse_objects_from_file(self, data_file: str) -> List[dict]:
        """
        Parse objects from a file in the working directory.

        Args:
            data_file:

        Returns:

        """
        from linkml_store.utils.format_utils import load_objects
        path_to_file = self.workdir.get_file_path(data_file)
        if not path_to_file.exists():
            raise AgentRunError(f"Data file {data_file} does not exist")
        return load_objects(path_to_file)
