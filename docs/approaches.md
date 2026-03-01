# Trajectory Summarization Approaches: MAT-SG vs MAT-SGT

The core of this project focuses on using a "grid" to cluster geolocated points that carry multiple semantic aspects. This documentation explains how the resolution is divided into two independent algorithmic approaches.

---

## 🌎 1. MAT-SG (Multiple-Aspect Trajectories based on a spatial Grid)

*Reference:* [Access the publication on Springer Link](https://link.springer.com/chapter/10.1007/978-3-031-12423-5_33)

**MAT-SG** primarily prioritizes **Spatial** distribution. 
Its execution aims to suppress noisy trajectory *outliers* by unifying neighboring groups that prove to be predominant through 2D windows defined by cellular scanning (Grid).

**Extraction Characteristics:**
1. The root points that make up the object's path (initial trajectory) are scanned.
2. They are plotted on a 2D plane representation divided into cells (Hash Matrix).
3. If a Cell gathers enough points to pass the Spatial Coverage Relevance Threshold (`TRC`), it acquires the "Representative" *status*.
4. **Unified Semantic Aggregation**: A single mathematically generated representative point — called a `Centroid` — is allocated to symbolize the cluster.
5. **Temporal Synthesis**: Since dozens of original instances collapse under a single centroid, MAT-SG builds a ranking of the time dimension in the form of a **Semantic Attribute**, presenting it proportionally. (E.g., `"10:10 prop: 0.1", "12:20 prop: 0.2"`).

**Use Cases**: MAT-SG is excellent for condensing analytical maps that do not depend on the *exact sequential history* from point to point, making it powerful for identifying activity "Hubs" or gathering poles (such as bus stations, frequent food courts in consumption traces, or fishing spots in vessel trajectories).

---

## ⏱️ 2. MAT-SGT (Multi-Aspect Trajectories Based on Spatio-Temporal Segmentation)

*Reference:* [Access the publication on JIDM](https://journals-sol.sbc.org.br/index.php/jidm/article/view/4110)

**MAT-SGT** evolves the clustering by imposing a strong **Temporal** restriction. 
It solves the narrative problem: an individual might visit the same restaurant 3 separate times during the day, yet MAT-SG would group everything into a single point. **MAT-SGT** preserves the chronological aspect by slicing the spatial cluster into representative contiguous continuous time lapses (`STI`).

**Extraction Characteristics:**
1. It follows exactly the same geographical *TRC* scanning of the spatial grid described above.
2. However, after isolating points within a viable cell, MAT-SGT triggers the **STI Tracker** (*Significant Temporal Intervals*).
3. Points from that cell are evaluated by their proximity on the clock, suppressing bizarre chronological gaps. 
4. Clusters of contiguous times that exceed the minimum percentage time window required by the Time Validation Threshold limit (`TRV`) fund their own Centroid!
5. **Divisive Restriction**: This means that the same 2D cell of a main square can generate multiple Representative Centroids along the listing if the trajectory is cut into sub-departures and sub-arrivals from that location in different windows (e.g., *Breakfast* vs *Night Stroll*).

**Use Cases**: MAT-SGT is the foundation for Smart Cities studies on sequential prediction or sub-routine mining (Sequential Pattern Mining), because it ensures that the computed trajectory can be perfectly "reproduced" on the clock, enabling Markov networks or regression flows over ordered real human activities.
