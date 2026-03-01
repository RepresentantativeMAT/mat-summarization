# MAT-data Architecture: Template Method Pattern

This document details the architectural design adopted for the MAT-data library to guarantee extensibility, code reuse, and maintainability. The structure was built applying classic Python inheritance over the **Template Method Pattern**.

## 1. The Duplication Problem

The two main approaches (MAT-SG and MAT-SGT) share the entire scope of data input, spatial *threshold* verification (`trc`), spatial grid allocation, and statistical summarization (median for numerical attributes, frequency ranking for categorical attributes).

Previously, the code had the logic of these operations duplicated across the classes, strictly differing in the intermediate stage where the **Temporal** factor is addressed.

## 2. The Solution: Template Method (`MATSummarize`)

The abstract base class `MATSummarize.py` centralizes all the time-agnostic logic. The 2D matrix infrastructure, dictionary normalization, and CSV file parser all reside in the parent. 

The processing flow in the superclass, encapsulated in the `execute()` method, invokes a "hook" or contract called `process_cell_points()`, which **must obligatorily** be implemented by its subclasses.

### Conceptual Skeleton of the Pattern

```python
# method/MATSummarize.py (Abstract Base)
class MATSummarize(ABC):
    def execute(self):
        self.load()
        self._allocate_points_in_grid()
        self._identify_and_process_cells()

    def _identify_and_process_cells(self):
        for cell_id, point_ids in self._spatial_cell_grid.items():
            if len(point_ids) >= self._trc:
                cell_points = [self._points[pid - 1] for pid in sorted(point_ids)]
                # --- TEMPLATE HOOK ---
                # The base class is unaware of time. It outsources this decision to the children!
                self.process_cell_points(cell_points, cell_id)
                
    @abstractmethod
    def process_cell_points(self, cell_points: List[Point], cell_id: Tuple[int, int]):
        pass
```

## 3. The Concrete Extensions

### Child A: `MATSGT` (Sequential Time)
The subclass fulfills the contract by extracting dynamic time intervals (`STIs`).
- For each valid `STI`, **multiple centroids** are created within a single geographical cell.
- The subclass injects the `.sti` pointer into each representative point and uses the parent's restricted inherited functions `self._fuse_aspects()` to condense the attributes.

### Child B: `MATSG` (Aggregated Time)
The subclass agglomerates the cell ignoring continuous time partitions into intervals.
- **Only a single centroid** is generated per validated cell.
- The raw temporal history is sent to a particular MATSG function (`_define_ranking_temporal()`) which transforms the list of traversed times into a *Synthetic* Categorical Semantic Attribute under the key `"TIME"`.

## 4. The Unified Output Model

Both implementations firmly adhere to the output contracts. At the end of a cell's summarization, the entities push native objects of the `Centroid` type toward the abstract shared variable `self._representative_trajectory`, so that the file extractor routine (Export to `.csv` or DataFrames) deals uniformly with instances of the original topology without needing type checking between methods or unnecessary spaghetti *parsing* routines.
