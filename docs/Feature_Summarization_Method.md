# Feature-Based Summarization Method (MATSGF)

## 1. Explanation of the Method

The MATSGF (Multiple Aspect Trajectory Summarization based on Grid and Features) is an extension of the semantic trajectory summarization process. While traditional methods extract and summarize semantic attributes individually (e.g., creating independent probability distributions for "Point of Interest" and "Price"), MATSGF introduces the concept of **Composed Features**.

A **Feature** is defined as an aggregated unit of two or more semantic attributes that possess inherent semantic dependency (e.g., the price of a bill is logically dependent on the location/POI where it occurred). When grouping points geographically (Spatial Grid), MATSGF extracts these features as tuples, e.g., `(Restaurant, 25)` instead of isolating them. 

The pipeline structure is:
1. **Feature Aggregation:** Extract combinations of dependent attributes occurring at each point inside a spatial constraint (cell).
2. **Semantic Compression (Optional):** Merge features that are deemed highly similar based on a predefined distance or semantic measure.
3. **Proportional Distribution:** Calculate the frequency of each unique feature combination relative to the cell's total points and distribute them proportionally, enforcing statistical relevancy thresholds (`trv`).

## 2. Comparison with Current Methods

### MATSG & MATSGT
- **Independence Assumption:** Assume all trajectory attributes are statistically independent.
- **Output:** Individual summaries `POI={Home: 0.5, Restaurant: 0.5}` and `price={10: 0.5, 20: 0.5}`.
- **Problem:** Loses the contextual dependency. It suggests fifty percent of the prices were 10 and 20, but it fails to map *which* POI produced the 20 amount value.

### MATSGF (New Method)
- **Dependency Aware:** Treats dependent attributes as cohesive multidimensional units.
- **Output:** Outputs the specific distribution of combined values: `POI_PRICE={{Home, 10}: 0.5; {Restaurant, 20}: 0.5}`.
- **Advantage:** Preserves realistic data semantics. Can compress redundant variations of continuous parameters inside the same categorical context, inspired by the dimensions association in MUITAS similarity measure.

## 3. Architectural Impact

The MATSGF implementation adheres strictly to the existing **Template Method** architectural pattern defined by the `MATSummarize` abstract class.

**Modified/Added Components:**
1. **`Feature.py` (New Model):** Represents the definition of a semantic feature, carrying its name and the list of related attribute titles.
2. **`FeatureAggregator.py` (New Method Component):** Encapsulates the logic of extraction, counting, and distribution of features to separate combinatorial logic from the pipeline runner.
3. **`MATSummarize.py` (Modified):** Small non-breaking upgrades. 
   - A `process_representative_point()` hook was added, executing after numerical and categorical summaries. By default, it does nothing, guarding existing `MATSG` stability.
   - Enhanced string formatting in `write_representative_trajectory()` to gracefully process Python dictionaries holding Tuples as keys, transforming them into the required `{ {A, B}: value }` syntax without single quotes.
4. **`AttributeValue.py` (Modified):** Enhanced the generic `__hash__` function. Historically, it was hashing `.value` indiscriminately, crashing when given a Dictionary. It now gracefully handles unhashable python objects by falling back to their string representations.

## 4. Pseudocode

```text
ALGORITHM FeatureSummarize(trajectory_dataset, features_definition)
    spatial_grid <- segment_space(trajectory_dataset, similarity_threshold)
    
    FOR EACH cell IN spatial_grid DO
        IF points_in(cell) >= minimum_cell_points THEN
            centroid <- Initialize Centroid at Geometric Center of cell points
            
            // 1. Classical Summarization (Independent Aspects)
            Fuse spatial and standard independent aspects of all points in cell into centroid
            Calculate time aggregation for centroid
            
            // 2. Feature Summarization (Composed Aspects)
            extracted_features <- empty Map
            FOR EACH Point p IN cell DO
                FOR EACH Feature f IN features_definition DO
                    tuple_val <- extract (f.attr1, f.attr2) from p
                    extracted_features[f][tuple_val] += 1
                END FOR
            END FOR
            
            distribution <- calculate_proportion(extracted_features, size(cell))
            compressed_distribution <- compress(distribution, semantic_similarity)
            
            Attach compressed_distribution to centroid as pseudo-Attribute
        END IF
    END FOR
    
    RETURN generated centroids
END ALGORITHM
```

## 5. Complete Execution Example

**Initial Dataset (Mock Test Data):**
```csv
tid,time,lat_lon,label,POI,price,weather,precip
1,480,10.0 10.0,car,Home,-1,clear,10
1,495,10.0 10.0,car,Home,-1,clear,9
1,510,10.1 10.1,car,Restaurant,25,clear,10
1,540,10.2 10.2,car,Restaurant,35,cloudy,15
1,570,10.2 10.2,car,Restaurant,25,cloudy,15
```

**Executing Python code:**
```python
feat_poi_price = Feature("POI_PRICE", ["POI", "price"])
feat_weather_precip = Feature("WEATHER_PRECIP", ["weather", "precip"])

matsgf = MATSGF(
    trc=0.0, trv=0.1, path="data/test_dataset_feat.csv",
    features=[feat_poi_price, feat_weather_precip]
)
matsgf.execute(...)
```

**Resulting Centroids Extracted (Truncated CSV View):**
| lat_lon | TIME | POI | POI_PRICE | WEATHER_PRECIP |
| --- | --- | --- | --- | --- |
| 10.03 10.03 | {08:00-08:30: 1.0} | {HOME: 0.66; RESTAURANT: 0.33} | **{{HOME, -1}: 0.66; {RESTAURANT, 25}: 0.33}** | **{{CLEAR, 10}: 0.66; {CLEAR, 9}: 0.33}** |
| 10.20 10.20 | {09:00-09:30: 1.0} | {RESTAURANT: 1.0} | **{{RESTAURANT, 35}: 0.50; {RESTAURANT, 25}: 0.50}** | **{{CLOUDY, 15}: 1.0}** |

As demonstrated, the algorithm correctly fuses the trajectory points that fell inside the same spatial block, while maintaining the contextual distribution of `{HOME, -1}` separate from `{RESTAURANT, 25}`.
