# Feature-Based Summarization Method

## 1. Formal Analysis of the Problem

### Definition of Attribute Dependency
In the context of Multiple Aspect Trajectories (MAT), **attribute dependency** occurs when the semantic value of an aspect $A$ is strongly associated with or conditioned by the value of an aspect $B$. Originally, the fusion matrix in `MATSummarize` (`_fuse_aspects()`) dismembered all attributes: it calculated the isolated **median** for numerical data and the **proportional frequency** for categorical data. This isolated ("naive") treatment destroys intrinsic data correlations. 
For instance, if in a cluster the majority of visited POIs is "Restaurant" (high price) and a minority is "Park" (zero price), individual summarization could result in a bizarre Centroid: `POI=Restaurant` with `price=zero` (due to a bias in the general median calculation).

### Classification of Dependencies
1. **Functional**: One attribute uniquely determines another (e.g., `Zip Code` -> `City`).
2. **Statistical**: High conditional probability (e.g., `Weather=Rainy` -> `Speed=Low`).
3. **Hierarchical**: Granularity relationship (e.g., `Country` -> `State` -> `City`).
4. **Contextual**: Depends on application domain semantics (e.g., `rating` makes sense attached to `establishment_type`, but not in isolation).

## 2. Explanation of the Method

In this package we have the Feature Based Summarization Method, it is one  extension of the semantic trajectory summarization process. While traditional methods extract and summarize semantic attributes individually (e.g., creating independent probability distributions for "Point of Interest" and "Price"), this method introduces the concept of **Composed Features**.

A **Feature** is explicitly defined by the user as an aggregated unit of two or more semantic attributes that possess inherent semantic dependency (e.g., the price of a bill is logically dependent on the location/POI where it occurred). The framework does not automatically discover these relationships; instead, it relies on the domain knowledge provided by the user during the method's execution. When grouping points geographically (Spatial Grid), the framework extracts the values for these user-defined features as tuples, e.g., `(Restaurant, 25)` instead of isolating them. 

The pipeline structure is:
1. **Feature Aggregation:** Extract combinations of the user-defined dependent attributes occurring at each point inside a spatial constraint (cell).
2. **Proportional Distribution:** Calculate the frequency of each unique feature combination relative to the cell's total points and distribute them proportionally, enforcing statistical relevancy thresholds (`trv`) -- considering the similarity between these attributes.

## 3. Comparison with Current Methods

### MATSG & MATSGT
- **Independence Assumption:** Assume all trajectory attributes are statistically independent.
- **Output:** Individual summaries `POI={Home: 0.5, Restaurant: 0.5}` and `price={10: 0.5, 20: 0.5}`.
- **Problem:** Loses the contextual dependency. It suggests fifty percent of the prices were 10 and 20, but it fails to map *which* POI produced the 20 amount value.

### Feature-Based Extension
- **Dependency Aware:** Treats dependent attributes as cohesive multidimensional units.
- **Output:** Outputs the specific distribution of combined values: `POI_PRICE={{Home, 10}: 0.5; {Restaurant, 20}: 0.5}`.
- **Advantage:** Preserves realistic data semantics. Can compress redundant variations of continuous parameters inside the same categorical context, inspired by the dimensions association in MUITAS similarity measure.

## 4. Architectural Impact

This extension adheres strictly to the existing **Template Method** architectural pattern defined by the `MATSummarize` abstract class.

**Modified/Added Components:**
1. **`Feature.py` (New Model):** Represents the definition of a semantic feature, carrying its name and the list of related attribute titles.
2. **`FeatureAggregator.py` (New Method Component):** Encapsulates the logic of extraction, counting, and distribution of features to separate combinatorial logic from the pipeline runner.
3. **`MATSummarize.py` (Modified):** Small non-breaking upgrades. 
   - A `process_representative_point()` hook was added, executing after numerical and categorical summaries. By default, it does nothing, guarding existing `MATSG` stability.
   - Enhanced string formatting in `write_representative_trajectory()` to gracefully process Python dictionaries holding Tuples as keys, transforming them into the required `{ {A, B}: value }` syntax without single quotes.
4. **`Point.py` (Modified):** Instead of relying on a custom `AttributeValue` wrapper for semantic values, the `Point` class was refactored to use native Python structures (`dict[tuple[SemanticAspect, ...], list[object]]`), allowing graceful and direct storage of the extracted multi-dimensional features (tuples) without complex hashing issues.

## 5. Pseudocode

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

## 6. Complete Execution Example

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

# You can use this with MATSG or MATSGT
matsg = MATSG(
    trc=0.0, trv=0.1, path="data/test_dataset_feat.csv"
)
matsg.execute(
    features=[feat_poi_price, feat_weather_precip]
)
```

**Resulting Centroids Extracted (Truncated CSV View):**
| lat_lon | TIME | POI | POI_PRICE | WEATHER_PRECIP |
| --- | --- | --- | --- | --- |
| 10.03 10.03 | {08:00-08:30: 1.0} | {HOME: 0.66; RESTAURANT: 0.33} | **{{HOME, -1}: 0.66; {RESTAURANT, 25}: 0.33}** | **{{CLEAR, 10}: 0.66; {CLEAR, 9}: 0.33}** |
| 10.20 10.20 | {09:00-09:30: 1.0} | {RESTAURANT: 1.0} | **{{RESTAURANT, 35}: 0.50; {RESTAURANT, 25}: 0.50}** | **{{CLOUDY, 15}: 1.0}** |

As demonstrated, the algorithm correctly fuses the trajectory points that fell inside the same spatial block, while maintaining the contextual distribution of `{HOME, -1}` separate from `{RESTAURANT, 25}`.
