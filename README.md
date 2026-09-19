# MAT-data: Multiple Aspect Trajectory Summarization Modeling (MAT-SG & MAT-SGT)

This repository contains the Python implementation for **Multiple Aspect Trajectory Summarization** algorithms. Initially based on Java, the **MAT-SG** (Multiple-Aspect Trajectories based on a spatial Grid) and **MAT-SGT** (Multi-Aspect Trajectories Based on Spatio-Temporal Segmentation) models were rewritten and optimized in object-oriented Python under the **Template Method** design pattern aiming at processing massive data of enriched trajectories.

## 📌 Project Overview

The central goal of this library is to reduce large volumes of trajectory points while maintaining spatial, temporal, and semantic fidelity through the agglomeration and definition of representative points that carry proportional semantics (e.g., Weather, POI locations, Prices, etc.).

The semantic accumulation supports fusion of both **Numerical** variables that generate average scores via median, and **Categorical** variables, preserving the weighted/proportional distribution of values within the consolidated clusters.

### 📍 Available Algorithm Patterns

There are two fundamental variations of spatial analysis applied to this model. For a complete theoretical foundation, access the [Approaches (MAT-SG vs MAT-SGT)](docs/approaches.md) guide.

1. **MAT-SG**: (Multiple-Aspect Trajectories based on a spatial Grid) agglomerates elements limited only to the **Spatial** threshold and grid, and fuses the semantics to generate mathematically calculated representative centroid points, discarding excessive points (`outliers`).
2. **MAT-SGT**: (Multi-Aspect Trajectories Based on Spatio-Temporal Segmentation) also adds the **Temporal** threshold, partitioning sub-cells that besides being spatially close, also co-exist in the same contiguous time interval partition of the day, grouping sub-intervals that compose time and space (`STI - Spatial-Temporal Intervals`).

---

## 🏗 Repository Structure and Architecture

The repository is architected following clean formal patterns focused on the **Template Method**. For a deep dive into the separation technique, refer to the [Architecture and Inheritance](docs/architecture.md) documentation.

### Class Architecture (Template Method)

```mermaid
classDiagram
    %% Core Algorithms (Method)
    class MATSummarize {
        <<abstract>>
        # _trc: float
        # _trv: float
        # _points_in_cell: list
        # _representative_trajectory: MultipleAspectTrajectory
        + load()
        + _compute_min_spatial_threshold()
        + _allocate_points_in_grid()
        + _fuse_aspects()
        + _summarize_numerical_aspects()
        + _summarize_categorical_aspects()
        + execute() final
        # process_cell_points(points, cell_id) *abstract*
    }

    class MATSGT {
        - _compute_stis(times)
        - _filter_outlier_differences()
        - _create_centroids_from_stis()
        # process_cell_points(points, cell_id) *override*
    }

    class MATSG {
        - _define_ranking_temporal()
        # process_cell_points(points, cell_id) *override*
    }

    %% Data Enitites (Model)
    class MultipleAspectTrajectory {
        + str trajectory_id
        + list pointList
    }

    class Centroid {
        + tuple cellReference
        + STI sti
        + addAttrValue()
    }

    class Point {
        + float lat
        + float lon
        + TemporalAspect time
    }
    
    class TemporalAspect {
        + datetime startTime
        + datetime endTime
    }

    class AttributeValue {
        + any value
    }

    class SemanticAspect {
        + str name
        + SemanticType type
    }

    %% Inheritances and Relationships
    MATSummarize <|-- MATSGT
    MATSummarize <|-- MATSG
    
    MATSummarize --> MultipleAspectTrajectory : Populates
    MultipleAspectTrajectory *-- Point : Contains 1..*
    Centroid --|> Point : Extends
    Point --> TemporalAspect : Has
    Centroid *--> TemporalAspect : Has Multiple
    Point *-- AttributeValue : Has Multiple
    AttributeValue --> SemanticAspect : Maps to
```

### Directory Layout

```text
/
├── README.md                       # Entry point project documentation
├── docs/                           # Extended project documentation (approaches and architecture guides)
├── data/                           # Local datasets manipulation
│   ├── input/                      # CSV spreadsheet repository for raw modeling
│   └── output/                     # Representative trajectories extracted by the model (.csv)
├── src/mat_summarize/              # Main package
│   └── method/                     # Contains the clustering and summarization methods logic
│       ├── MATSummarize.py         # Base Abstract Class (Template Method Pattern)
│       ├── MATSG.py                # Subclass applying Spatial heuristics
│       ├── MATSGT.py               # Subclass adding partitioning via Time STIs
│       └── MUITAS.py               # Algorithmic univariate scoring calculations
│   └── model/                      # Structural and Geometric Models
│       ├── AttributeValue.py       # Embedded dictionaries of <Aspect:Value> (e.g., {WEATHER: "CLOUDS"})
│       ├── Centroid.py             # Groups Space-Time cuts
│       ├── Point.py                # Abstract elements of raw Lat/Lon 
│       ├── SemanticAspect.py       # Dimensional treatment
│       ├── TemporalAspect.py       # Datetime utility wrapper 
│       └── Util.py                 # Global Euclidean distances and cKDTree mappings
```

---

## 🚀 How to Install and Run

### Prerequisites
*   Python 3.9 or later
*   NumPy
*   Pandas
*   SciPy

### 1. Installation

Install the package using `pip`:

```bash
pip install mat-summarize
```

### 2. Running MAT-Summarize

#### Step 1: Import a Method

MAT-Summarize provides two main methods: `MATSG` and `MATSGT`. Import the method you want to use:

```python
from mat_summarize.method import MATSGT
```

#### Step 2: Initialize the Method

Create an instance of the selected method:

```python
model_sgt = MATSGT(
    trc=0.25,
    trv=0.25,
    path='test_input.csv'
)
```

The constructor accepts the following parameters:

| Parameter | Description                                                                |
| --------- | -------------------------------------------------------------------------- |
| `trc`     | Threshold for relevant cells (`tauRelevantCell`).                          |
| `trv`     | Threshold for the representativeness value (`tauRepresentativenessValue`). |
| `path`    | Path to the input dataset.                                                 |

#### Step 3: Execute the Method

Run the method using the `execute()` function:

```python
model_sgt.execute(
    lst_categorical_pd=['price'],
    values_null=[-1, -999],
    pattern_date_input='?',
    dir='data/',
    file='test_output',
    ignore_columns=None,
    features=[('poi',), ('price',), ('weather', 'precip')]
)
```

The `execute()` function accepts the following parameters:

| Parameter            | Description                                                                            |
| -------------------- | -------------------------------------------------------------------------------------- |
| `lst_categorical_pd` | List of columns that should always be treated as categorical.                          |
| `values_null`        | List of values that represent missing data.                                            |
| `pattern_date_input` | '?' Flags if trajectory data will be daily and adjusts to hh:mm format.                |
| `dir`                | Path to the output directory.                                                          |
| `file`               | Name of the output file.                                                               |
| `ignore_columns`     | List of dataset columns to exclude from processing. Use `None` to include all columns. |
| `features`           | List of tuples specifying the attributes to be used by the method.                     |

#### Complete Example

```python
from mat_summarize.method import MATSGT

model_sgt = MATSGT(
    trc=0.25,
    trv=0.25,
    path='test_input.csv'
)

model_sgt.execute(
    lst_categorical_pd=['price'],
    values_null=[-1, -999],
    pattern_date_input='?',
    dir='data/',
    file='test_output',
    ignore_columns=None,
    features=[('poi',), ('price',), ('weather', 'precip')]
)
```

### 3. Output

After execution, MAT-Summarize exports the dataset history as a CSV file.

For the example above, the output file will be named:

```text
test_output rc 25 rv 25 - zX.csv
```

The resulting CSV contains a numerical and temporal condensation of the input data. Some attributes may be represented using dictionary-like notation, such as:

```text
{23:20 - 23:30 prop: 0.33}
```

The output header provides information about:

* The method used.
* The coverage achieved.
* The reduction applied to the original dataset.

This allows you to evaluate how the input data was condensed while preserving relevant information.

---

## 🛠️ Recent Refactoring Contributions (Changelog)

-   Architectural migration based purely on base **Classic Python (`snake_case`)** OOP, eliminating legacy Java *camelCase* fragments;
-   Integration of the **Template Method** encapsulation Pattern concentrating inheritance and abstraction in the parent file *`MATSummarize.py`*, reducing redundant code by >50%;
-   Fixed the `Java Skip Indexing` bug, refining the accuracy with what the Outlier Removal Process eliminates (where before they were accidentally spared);
-   100% reliable adherence to probability normalization to yield a real-mathematical `sum = 1.0`.
-   Removal of Dead Code through scanning (`Vulture` specs).

## 📄 Model Authors / Contact
This research was partially funded by SoBigData++ Project - by Transnational Access (TNA),as well as the European Union’s Horizon 2020 research and inno-vation programme under GA N. 777695 (EU Project MASTER -Multiple ASpects TrajEctoRy management and analysis), until 2024. In present, the researcher is referenced in **Análise Avançada de Dados de Trajetórias: Uma ferramenta visual para identificação de padrões em dados de Mobilidade** project. Developed with academic support and adaptation via IFSUL and original MAT-data repository.

For formal and architectural in-depth understanding based on the original research articles, refer to:
- **MAT-SG ([Springer Link](https://link.springer.com/chapter/10.1007/978-3-031-12423-5_33))**: *Multiple-Aspect Trajectory Summarization based on a spatial Grid*
- **MAT-SGT ([JIDM](https://journals-sol.sbc.org.br/index.php/jidm/article/view/4110))**: *Multiple-Aspect Trajectory Summarization via Grid and Time*

## 📞 Contacts
- [Jonathan Roberto Fragoso Bonatto](mailto:jonathanrfbonatto@gmail.com)
- [Vanessa Lago Machado](mailto:vanessalagomachado@gmail.com)