import logging
from dataclasses import dataclass
from enum import Enum

from llama_index.core.node_parser import CodeSplitter, NodeParser
from tree_sitter_languages import get_parser

logger = logging.getLogger("rag.splitters")


# TODO: Possibly change implmentation up as you add more FileSplitters
# instead of having a splitter config but just being inherent values of the enum.
@dataclass
class SplitterConfig:
    splitter: NodeParser
    extensions: set[str]


class FileSplitter(Enum):
    CPP = SplitterConfig(
        splitter=CodeSplitter(
            language="cpp",
            parser=get_parser("cpp"),
            chunk_lines=40,
            chunk_lines_overlap=15,
            max_chars=1500,
        ),
        extensions={".cpp", ".hpp", ".c", ".h"},
    )
