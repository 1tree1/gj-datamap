# Urban analysis techniques for data-driven city planning: a technical reference

> 원본 파일명: `compass_artifact_wf-a2cc0c68-96e6-4fee-befa-ab7326064150_text_markdown.md`

**Building an intelligent urban analysis platform requires weaving together at least 14 distinct analytical traditions, each with its own toolchain, academic lineage, and integration challenges.** This reference catalogs these techniques for URBANIS — a platform targeting Daegu city redevelopment that integrates real-time data streams, hybrid AI, knowledge graphs, and 3D visualization. Techniques are ordered by volume of recent peer-reviewed evidence, real-world implementations, and open-source tooling maturity. For each, we provide methods, key references, case studies (Korean where available), tools, and emerging trends through 2025. Daegu — a basin city of 2.3 million people experiencing rapid population loss and aging urban fabric — stands to benefit directly from nearly every technique described here.

---

## 1. Space syntax reveals how street geometry shapes movement and land value

**Space syntax** is a mathematical framework for analyzing spatial configurations and their relationship to social processes. Founded by **Hillier & Hanson (1984)** in *The Social Logic of Space*, it quantifies two core properties: **Integration** (how close a street segment is to all others, predicting "to-movement") and **Choice** (how likely a segment is to appear on shortest paths, predicting "through-movement"). Angular Segment Analysis introduced by Hillier, Yang & Turner (2012) normalized these as NAIN and NACH for cross-city comparison. Visual Graph Analysis (VGA) extends the framework to building interiors and open spaces via visibility graphs.

**Key tools** include **depthmapX** (UCL Bartlett, open-source, handles axial/segment/VGA analysis), **sDNA** (Cardiff University, GPL v3, supports QGIS/ArcGIS/Rhino/Python, handles 3D and curved links natively), and the Space Syntax Toolkit for QGIS. Cooper & Chiaradia (2020) published sDNA's software paper in *SoftwareX*. For Python pipelines, OSMnx + NetworkX can replicate basic network centrality calculations, while sDNA's `sdnapy.py` provides a proper API.

**Daegu case studies** are directly available. Jung & Choi studied pedestrian volumes in downtown Daegu using street integration metrics. Jeong, Lim & Park (2013) applied Angular Segment Analysis to Daegu's Yakryeong traditional medicine market. Most significantly, **Gohaud, Arora & Schuetze (2025)** published a multi-scalar morphological analysis of Daegu in *Sustainability* using QGIS and momepy, identifying **9 tissue categories** and 16 Regeneration New Deal projects. In Seoul, Kim et al. (2020) in *Sustainability* validated space syntax against 10,000 pedestrian count locations.

Recent advances combine space syntax with deep learning. De Sabbata et al. (2024) used a **graph autoencoder with PyTorch Geometric** on 138 UK street networks for unsupervised urban form embeddings. Jin et al. (2024) surveyed spatio-temporal GNNs for urban computing in *IEEE TKDE*. A 2025 study in *GeoJournal* combined CNNs, space syntax metrics, and GIS indices into a composite walkability index for Batna. Limitations include the 2D-centricity of most tools, multicollinearity in regression models, and computational scaling for large networks. The emerging trend is GNN-based real-time prediction using space syntax graph structures as static inputs combined with dynamic sensor data.

---

## 2. Computational urban morphology classifies city fabric at scale

Urban morphology has undergone a computational revolution since 2019. The core innovation is **morphological tessellation** — Voronoi-based partitioning around building footprints that creates consistent spatial units where cadastral data is unavailable. Fleischmann et al. (2020) formalized this in *Computers, Environment and Urban Systems* (CEUS). The **momepy** library (Fleischmann 2019, *JOSS*; now part of PySAL, v0.11.0) computes **six categories of morphometric characters**: dimension, shape, spatial distribution, intensity, connectivity, and diversity.

**Building typology classification** follows Fleischmann et al.'s (2022) numerical taxonomy in *EPB: Urban Analytics and City Science*: generate morphological elements, measure primary and contextual characters, detect clusters via Gaussian Mixture Models, then build hierarchical taxonomies via Ward's algorithm. Tested on Prague, this identified 10 clusters from medieval core to residential suburbs. A 2025 study of Thessaloniki used **UMAP + BIRCH clustering** on 17 morphological indicators to identify 14 urban form types.

**Fractal analysis** traces to Batty & Longley's *Fractal Cities* (1994) and Batty's *The New Science of Cities* (2013). **OSMnx** (Boeing 2017; v2.0 in 2024) remains the essential tool for downloading and analyzing street networks from OpenStreetMap — calculating intersection density, circuity, centrality, and orientation entropy.

The Gohaud et al. (2025) Daegu study is directly applicable: it identified historical fine-grained fabric, 1940–1983 land readjustment grids, and various modern development types, finding that **overly fine urban grain resists regeneration while piecemeal high-rise redevelopment fragments the urban landscape**. A 2024 study of Chinese small towns combined U-Net3+ building extraction with momepy tessellation and hierarchical clustering of 89 towns.

Emerging trends include **national-scale classification** (Fleischmann & Arribas-Bel's Spatial Signatures for all of Great Britain), 3D urban morphology (Labetski et al. 2023, Netherlands), and CNN-based form identification from satellite imagery. The "Urban Grammar AI" project at Liverpool extends momepy for large-scale analysis, and heterogeneous GNNs now combine buildings, streets, and plots into unified graph representations.

---

## 3. Computer vision quantifies how people perceive urban environments

Street-level imagery analysis has matured from MIT's Place Pulse experiments to production-ready tools. The **Place Pulse 2.0** dataset (Dubey et al., ECCV 2016) contains **110,988 images from 56 cities with 1.17 million pairwise comparisons** across six perceptual dimensions: safe, lively, boring, wealthy, depressing, and beautiful. Semantic segmentation with **PSPNet**, **DeepLab V3+**, or **Mask R-CNN** identifies per-pixel urban elements (roads, buildings, vegetation, sky) that correlate with these perceptions.

The **Green View Index** (Li et al. 2015, *Urban Forestry & Urban Greening*) measures the percentage of vegetation visible from street level. The standard pipeline samples points at 20–100m intervals, retrieves multi-directional images, segments vegetation, and averages green pixel ratios. MIT's **Treepedia** project (Seiferling et al. 2017) applied this across 30 global cities. Deep learning versions like **Treepedia 2.0** achieve 0.94 correlation with manual assessments using ResNet-based direct estimation.

**For Daegu and South Korea, Naver Maps is the recommended primary imagery source** — it provides denser, more frequently updated coverage than Google Street View due to national security restrictions on geographic data export. A 2023 Seoul walkability study applied DeepLab V3+ to **233,106 Naver panoramic images**, estimating micro-scale streetscape indicators. A 2025 Seoul study used **Swin Transformer** for predicting Perceived Decline Scores. The Seoul Street-View Database (2026) provides longitudinal coverage from 2010–2023.

Sentiment mapping combines CV with NLP. A 2025 *Frontiers in Computer Science* paper described a two-phase framework: **BERT-based sentiment inference** on 47,107 geotagged social media posts, followed by PSPNet + Mask R-CNN urban context inference. The MIT Sustainable Urbanization Lab (2023, *Scientific Data*) created a BERT-based multilingual sentiment classification dataset from 4.3 billion geotagged tweets. For Korean text, **KoBERT or multilingual BERT** on geotagged data from Naver Blog, KakaoStory, and Twitter/X would be appropriate. Note that Place Pulse 2.0 may overestimate negative perceptions in East Asian cities (Shenzhen study), so local calibration datasets are advisable.

Open-source tools span DeepLab V3+ (TensorFlow), PSPNet (PyTorch), the Treepedia GitHub repositories, and a dedicated QGIS GVI plugin. Emerging trends include foundation models (GPT-4V for automated urban attractiveness assessment, though "geo-hallucination" risks exist per Biljecki 2024), spatiotemporal contrastive learning for street view representations (arXiv 2025), and multi-modal fusion combining SVI + satellite + POI data.

---

## 4. Graph neural networks model cities as interconnected systems

Cities naturally map to graphs: **nodes** represent urban regions, intersections, or parcels; **edges** represent roads, spatial adjacency, or functional connections. GNN architectures — **GCN** (Kipf & Welling 2017), **GAT** (Veličković et al. 2018), **GraphSAGE** (Hamilton et al. 2017) — propagate information through these structures for prediction and optimization.

The flagship work is **Zheng et al. (2023)** in *Nature Computational Science* from Tsinghua University's BNRist lab. They formulated urban planning as a **sequential decision-making MDP on a contiguity graph**, using a GNN-based state encoder with two policy networks for land-use placement and road planning. Tested on two real communities (~4 km² each), the AI model **outperformed plans designed by 8 human planners** in service accessibility, ecology, and traffic metrics. Code is open-source at `github.com/tsinghua-fib-lab/DRL-urban-planning`. The same group published road planning for slums (KDD 2023, improving accessibility by 14.3% in Harare and Cape Town), **MetroGNN** for metro network expansion (WWW 2024, 30%+ OD flow improvement), and large-scale facility location selection achieving **1000× speedup** over commercial solvers (SIGSPATIAL 2024).

For traffic prediction — the most common GNN application with 29+ studies in 2023–2024 alone — key models include **T-GCN** (GCN + GRU), **STGCN** (graph + temporal convolution), **DCRNN** (diffusion convolution), and **Graph WaveNet** (adaptive adjacency). A 2025 model (GNN-GA) combines GNN traffic prediction with genetic algorithm optimization for carbon emission reduction.

**PyTorch Geometric** (13,000+ GitHub stars) is the primary framework, supporting 150+ layer types. **DGL** (Deep Graph Library) offers GPU-accelerated sampling via GraphBolt in v2.1. Domain-specific repositories include Tsinghua's three urban planning repos and the GNN4Traffic collection. Integration with real-time data is feasible through dynamic graph construction with adaptive adjacency matrices (GFAGNN 2024) and DGL's GPU pipeline acceleration for streaming inference.

Limitations include scalability for full-graph training, sensitivity to graph construction choices, sparse sensor coverage in real urban networks (Manhattan has only 21 sensors for 8,156 segments), and the planning gap — AI models reduce planning to spatial optimization, often ignoring zoning, equity, and political dimensions.

---

## 5. Generative AI is shifting from GANs to diffusion models for urban layout synthesis

The field has evolved rapidly from **Pix2Pix** conditional GANs to diffusion-based architectures. **ArchiGAN** (Chaillou 2019, Harvard/NVIDIA) pioneered a 3-step Pix2Pix pipeline for apartment design: building massing → program repartition → furniture layout, with human review between stages. Subsequent work includes **ESGAN** (Jiang et al. 2023, *Automation in Construction*) with site-embedded conditional generation for NYC, and **CAIN-GAN** (2024) adding domain knowledge for context-aware site planning.

**Diffusion models now represent the frontier.** He, Liang et al. (2025, arXiv:2505.24260) from MIT/UC Berkeley proposed the most significant recent framework: a **3-stage human-in-the-loop ControlNet diffusion pipeline** generating (1) road network + land use, (2) building layouts, (3) detailed renderings — all conditioned on text prompts and image constraints, tested on Chicago and NYC. **GenFusion** (2025) integrates diffusion with XGBoost prediction and genetic algorithm optimization for wind comfort and solar access. For road networks specifically, a 2024 ISPRS paper trained conditional diffusion models on geospatial context from 5 US cities. **CityGen** (Deng et al. 2023) and **UrbanWorld** (arXiv:2407.11965) generate 3D city layouts, while **CityCraft** (2024) uses LLM-driven agents for 3D environment design.

VAE-based approaches include **CLUVAE** (Wang et al.) incorporating human guidance for land-use customization and **DSUF** (arXiv 2310.02453) using normalizing flows as a two-stage alternative that outperforms VAE/GAN baselines. **GC-GAN** (2024, *Automation in Construction*) integrates **knowledge graphs encoding domain constraints** directly into GAN generation — a critical advance for regulatory compliance.

Open-source implementations include Pix2Pix (TensorFlow/PyTorch), Pix2PixHD (NVIDIA), CycleGAN, Stable Diffusion, and ControlNet. For URBANIS, **LoRA fine-tuning of Stable Diffusion on Daegu-specific building morphology** is technically feasible with 100–1,000 training examples from NSDI/VWORLD data. Key limitations remain: most models produce pixelized 2D output lacking vector precision for CAD/BIM, cross-city transferability is poor, and zoning compliance is not inherently guaranteed.

---

## 6. Neuro-symbolic AI bridges neural perception with regulatory reasoning

The core architecture combines **neural networks for pattern recognition** (satellite/street imagery classification) with **symbolic AI for logical constraint checking** (ontology-based zoning rules, building codes). Neuhaus & Roxin (2022) published the foundational paper advocating neuro-symbolic AI for smart cities, proposing a Python-based architecture compatible with BIM/GIS standards. **LogiCity** (NeurIPS 2024, Li et al.) created the first first-order logic urban simulator for neuro-symbolic AI, modeling urban elements with semantic/spatial predicates.

**Ontology standards for urban planning** are maturing rapidly. **OntoZoning** (Grisiute et al. 2023, ETH Zurich/Cambridge CARES) encodes Singapore's zoning regulations as OWL ontology, linked to a geospatial knowledge graph in Blazegraph triplestore. **OntoPlanningRegulations** (AGILE 2025) extends this with building regulations for automated 3D master plan generation. The **SMOF framework** (2025, *Smart Cities*) unifies BIM, GIS, and IoT data with five core modules, deployed on **Shenzhen's Spatial Digital Platform** using Apache Jena. CityGML 3.0 (OGC Standard) has been transformed into OWL ontology networks via **CityOWL** (ISPRS Annals 2024).

For Korean planning law, the **OntoZoning model provides the closest template** for encoding Korean 용도지역 (use zone) regulations. A Daegu-specific knowledge graph could integrate building age/condition (from CV analysis), zoning status, FAR/building coverage limits, and redevelopment eligibility criteria. A 2024 Korean study in *Sensors* demonstrated an IFC→CityGML→OWL/RDF pipeline with Neo4j validation targeting South Korean smart city applications.

The tool stack includes **OWL/RDF/SPARQL** with **GeoSPARQL** for spatial queries, **Protégé** for ontology editing, **Apache Jena** for reasoning, **Neo4j** with neosemantics for property graph + OWL reasoning, **Blazegraph** as RDF triplestore, and **PyKEEN** (40+ knowledge graph embedding models). An emerging trend is **LLM + Knowledge Graph integration** — LLMs generating SPARQL queries and extracting entities from regulatory text to populate ontologies automatically.

---

## 7. The 15-minute city framework drives accessibility analysis worldwide

**Carlos Moreno** (Sorbonne University) proposed that residents should access six essential functions — living, working, commerce, healthcare, education, and leisure — within a **15-minute walk or bike ride**. His foundational academic paper appeared in *Smart Cities* (2021). The concept rests on four pillars: proximity, density, diversity, and digitalization.

Quantitative assessment uses **isochrone mapping** — lines connecting points of equal travel time. Key open-source tools include **Valhalla** (Mapbox, MIT License, supports multimodal isochrones via GeoJSON), **OpenRouteService** (University of Heidelberg, Python/R/QGIS clients), **r5py** (Python wrapper for Conveyal's R5 engine integrating GTFS + OSM), **Pandana** (C++ core for fast network accessibility), and **UrbanAccess** (creates multi-modal graphs from GTFS + OSM). The **15min City Score Toolkit** (Transform Transport) uses H3 hexagonal grids with exponential distance decay, tested on 112 EU cities.

**Korea has significant implementations.** Busan launched the **"15-Minute City Busan Vision"** in May 2021 with **150 billion KRW (~$110M) investment** across 62 living areas — the only Asian city invited to Moreno's international conference in Paris (2025). Seoul adopted the concept via the "2040 Seoul Urban Master Plan" (2023) with a "30-Minute Walking Life Zone." Korean **생활SOC (Living Infrastructure)** policy provides community-level facilities within walking distance. Logan et al. (2022) in *Cities* developed the "x-minute city" multi-threshold framework applied in the US and New Zealand. Rhoads et al. (2023) in CEUS introduced sidewalk network analysis for Barcelona.

Real-time transit data integration via **GTFS-RT** significantly improves accuracy. A 2025 framework using real-time GTFS showed that **scheduled data overestimates healthcare accessibility by ~11%** compared to actual service. For Daegu, deploying Valhalla/r5py with the city's OSM network and Korean GTFS transit feeds would enable isochrone generation and accessibility scoring referenced against Busan's precedent.

---

## 8. Land use change detection leverages Sentinel-2 and deep learning advances

**Satellite change detection** identifies land surface differences through multi-temporal observations. Traditional approaches (image differencing, change vector analysis, post-classification comparison) have been largely superseded by deep learning. Key spectral indices for urban analysis include **NDVI** ((B8−B4)/(B8+B4) for vegetation), **NDBI** ((B11−B8)/(B11+B8) for built-up areas), and **UI** ((B12−B8)/(B12+B8) for urban surfaces).

The architecture evolution progressed from **Siamese Networks** (Daudt et al. 2018, foundational Fully Convolutional Siamese Networks) through **U-Net variants** to **transformer-based models**. **BIT** (Chen & Shi 2021, *IEEE TGRS*) introduced the first transformer-based change detection, outperforming prior methods by 2–4.7 F1 points on LEVIR-CD. **ChangeFormer** (Bandara & Patel, IGARSS 2022) uses a pure Siamese transformer with hierarchical encoder. He et al. (2024) in *Remote Sensing of Environment* introduced **temporal semantic segmentation** (TSSCD) capturing where, when, and what changes simultaneously from monthly Sentinel-2 data. However, a sobering "Change Detection Reality Check" at ICLR 2024 showed that a **simple U-Net baseline matches or beats complex architectures** on LEVIR-CD, revealing data leakage in WHU-CD preprocessing.

**Daegu-specific studies** include Kim & Kim (2019), who compared Landsat imagery before and after Sinseo Innovation City development, finding **NDVI decreased 0.07 and LST increased 0.85°C**. A 2021 Daegu study found strong negative NDVI-LST correlation across land use types (forest NDVI=0.447, commercial NDVI=0.150). For urban sprawl, a 2022 Korean XGBoost model with SHAP values found areas adjacent to Seoul, Busan, and Daegu showed highest urbanization probability.

**Sentinel-2** provides 10m resolution across 13 bands with ~5-day revisit. Key tools include **Google Earth Engine** (80+ PB catalog, cloud processing), **TorchGeo** (Microsoft, 126+ dataset loaders including OSCD and LEVIR-CD, pre-trained foundation models DOFA/SoftCon/Panopticon in v0.7), **eo-learn** (Sentinel Hub, full preprocessing pipeline), and standard rasterio/GDAL. Emerging trends include **foundation models for Earth observation** (pre-trained on millions of satellite images, fine-tunable for change detection), SAR+optical fusion for cloud-gap filling, and Google's **Dynamic World** providing near-real-time 10m LULC from Sentinel-2.

---

## 9. Urban digital twins are becoming operational in Korean smart cities

An **Urban Digital Twin (UDT)** is a dynamic virtual replica integrating real-time sensor data, 3D city models, and simulation capabilities. **CityGML 3.0** (OGC Standard) defines the primary open data model with multiple Levels of Detail (LOD0 footprints through LOD4 interiors), while **CityJSON** provides a lighter JSON encoding for web applications. The standard architecture layers static CityGML models (in **3DCityDB**, open-source PostgreSQL/PostGIS database, v5.1.1) with dynamic IoT data via OGC **SensorThings API**, visualized through CesiumJS/3D Tiles.

Global implementations include **Virtual Singapore** (world's first national-scale digital twin on Dassault's 3DEXPERIENCE City platform, 700+ km²), **Helsinki 3D+** (CityGML LOD1/LOD2, 10cm accuracy, reduced bus delays by 15%), and Zurich (noise, pollution, solar, flood simulation as Open Government Data per Schrotter & Hürzeler 2020).

**Korean digital twin initiatives are substantial.** **E8IGHT** built Korea's first smart city digital twin for Sejong 5-1 Living Area using its NDX PRO platform with 3D GIS + BIM integration. **Busan Eco Delta Smart City** ($4.2B, 280ha) uses E8IGHT for its digital twin with IoT monitoring and autonomous EVs. **Seoul S-Map** provides a 3D model of 600,000+ buildings; a "hyper-realistic digital twin" was announced in June 2024 targeting disaster safety. Korea's Smart City Act 2024 formalized national commitment, and the emerging "**Citiverse**" concept moves beyond digital twins toward immersive urban metaverses.

For participatory planning, Dembski et al. (2020) demonstrated VR digital twins for civic engagement in Herrenberg, Germany, using stereoscopic back projection and mobile VR. The **vCity Project** (Barcelona Supercomputing Center) combines simulation, scenario tools, and the Decidim digital democracy platform for Living Labs in Barcelona and Kobe. Open-source tools for the URBANIS pipeline include **3DCityDB**, **Py3DTilers** (Oslandia, converts CityGML to OGC 3D Tiles), **py3dtiles**, and the 3DCityDB-Web-Map-Client for CesiumJS integration.

---

## 10. Climate resilience analytics address Daegu's extreme heat challenge

Daegu is nicknamed **"Daefrica"** for its extreme summer heat — a basin city surrounded by mountains with poor ventilation and record temperatures reaching 40.0°C. It is the **only Korean city with a dedicated heatwave plan**. Surface urban heat island intensity reaches **up to 10°C** between urban core and rural areas (2025 ECOSTRESS/GK-2A study at 70m resolution).

**Sponge city hydrological simulation** uses the **SCS-CN** (Soil Conservation Service Curve Number) method and **InVEST** (Natural Capital Project, Stanford). The InVEST Water Yield model integrates LULC, meteorological, and soil data for spatially-explicit runoff simulation. A 2025 Chengdu study found transportation, commercial, industrial, and residential land account for **74.7% of total surface runoff**. **SWMM** (EPA, open-source with Python wrapper pyswmm) handles coupled 1D-2D sewer/surface modeling with Nash-Sutcliffe efficiency >0.75.

The **InVEST Urban Cooling Model** estimates heat mitigation based on shade, evapotranspiration, albedo, and distance to cooling islands. Bosch et al. (2021) published the spatial approach in *Geoscientific Model Development*; an automated Python calibration library (`invest-ucm-calibration`, PyPI) uses simulated annealing. **ENVI-met** provides commercial 3D microclimate simulation at 1–10m resolution, validated in 3,000+ papers including Seoul studies.

**Wind corridor CFD** uses **OpenFOAM** (open-source C++) with steady-RANS k-ε turbulence models. A multi-scale approach chains WRF (mesoscale, 1km) → OpenFOAM (building-scale, <10m). A 2024 Meccanica review of 289 papers found ~58% relate to wind in built environments. Emerging ML surrogates like **PIGNN-CFD** (physics-informed GNN trained on OpenFOAM data) address computational cost barriers.

**Biophilic urbanism metrics** quantify nature integration: Lefosse et al. (2025) proposed a three-metric approach (quantitative frequency, qualitative benefit types, spatial distribution) tested in Amsterdam. Key benchmarks include 10% increase in tree cover reducing UHI by up to 55%, nature-based solutions reducing flood risk by 20% (World Bank), and biophilic design raising property values 8–20%.

---

## 11. Activity-based models and agent simulations predict urban behavior

**MATSim** (Multi-Agent Transport Simulation, open-source Java, matsim.org) simulates millions of individual agents with full-day activity plans iteratively optimized via co-evolutionary scoring. Applications include Shanghai shared autonomous EV simulation (2024), Fortaleza synthetic population for 4M people, and **Sketch MATSim** (2023) for quick iterative urban design evaluation.

**SUMO** (Simulation of Urban MObility, Eclipse/DLR, open-source) provides microscopic traffic simulation with TraCI for real-time programmatic interaction. **AgentSUMO** (2024) adds LLM-based natural-language control. **Mesa 3** (Python, 2025, *JOSS*) provides a general agent-based modeling framework with Mesa-Geo for GIS integration and synthetic population pipelines using WorldPop data.

**Real-time calibration** is advancing. Pourmoradnasseri et al. (2023) in *IET Smart Cities* demonstrated **near-real-time SUMO calibration using IoT sensors** in Tartu, Estonia, with bounded variable quadratic programming and parallel simulations. A SUMO-based digital twin for motorway dynamics (2022, *Transportation Research Part C*) fused actual traffic data every minute into running simulations. CARLA-SUMO co-simulation (2024) uses YOLO-based camera detection on traffic light poles feeding SUMO for adaptive signal control. For Korean context, **KTDB** (Korea Transport Database) provides household travel surveys and OD matrices usable for MATSim/SUMO calibration.

**Synthetic population generation** follows methods reviewed by Chapuis, Taillandier & Drogoul (2022) in *JASSS*: Iterative Proportional Fitting, combinatorial optimization, Bayesian networks, and microsimulation. **Pedestrian flow simulation** builds on Helbing & Molnár's (1995) Social Force Model, with open-source implementations including **Vadere** (multiple microscopic models + GUI), **JuPedSim** (Python/C++), and **PedSim/libpedsim** (SFM-based, real-time).

---

## 12. Spatial justice analysis quantifies who benefits from redevelopment

Spatial justice theory draws from three intellectual traditions: **Lefebvre's** right to the city (1968) — space is socially produced; every inhabitant has rights of appropriation and participation; **Harvey's** territorial justice (1973) and Marxist critique of gentrification as class-based displacement; and **Soja's** spatial justice (2010) — space is an active medium through which justice is negotiated. **Fainstein's** *The Just City* (2010) operationalizes **three principles: equity, diversity, and democracy**, with equity prevailing when values conflict.

Quantitative operationalization uses **Gini coefficients** for spatial distribution of accessibility (Jang et al. 2017, Seoul), **Two-Step Floating Catchment Area** analysis balancing service supply and demand, and composite **Spatial Justice Indices** via PCA across public goods, services, opportunities, and environments. Santos Cruz & Pinho (2024) in *Planning Practice & Research* operationalized four criteria from social psychology: strict equality, need, merit, and entitlement.

**Green gentrification** has been rigorously modeled by Anguelovski and colleagues. Their landmark 2022 *Nature Communications* study applied **spatially weighted Bayesian regression across 28 cities in 9 countries**, finding strong positive relationships between 1990s–2000s greening and 2000–2016 gentrification in 17 of 28 cities. For Daegu specifically, Jin et al. (2021) in *Urban Forestry & Urban Greening* studied greening using abandoned places. Lim & Kain (2016) in *Cities* documented Daegu's deindustrialization, population decline, and rising socio-spatial inequality, while a 2025 *MDPI Land* study assessed low-income residential segregation impacts of Korean urban redevelopment using dissimilarity and isolation indices — finding **~80% of original residents displaced** in Joint Redevelopment Programme projects.

Tools include **PySAL** (spatial autocorrelation, inequality indices), **ADAPT** (Automatic Dynamic Accessibility Planning Tool), **OpenTripPlanner**, **R5/Conveyal** for large-scale accessibility computation, and **Pandana/OSMnx** for network-based equity analysis.

---

## 13. Urban metabolism tracks material and energy flows through city systems

Urban metabolism quantifies the totality of technical and socioeconomic processes occurring in cities. **Kennedy, Cuddihy & Engel-Yan (2007)** in *Journal of Industrial Ecology* formalized the concept, later defining **seven metabolic flows**: water, energy, waste, people/mobility, goods/materials, climate/emissions, and biota/food (Kennedy et al. 2014, *Ecological Indicators*). The tradition traces to Wolman's 1965 *Scientific American* article.

**Amsterdam** became the first city to commit to 100% circular economy by 2050, based on **Kate Raworth's Doughnut Economics** model. Its Circular Monitor dashboard tracks material flows, CO2 emissions, biodiversity, and water pollution in real-time. Metabolic's spatial analysis categorized neighborhoods into four types with tailored circularity strategies. The **REPAiR Project** built a Geodesign Decision Support Environment for the Amsterdam Metropolitan Area.

**Street-level MFA** addresses the gap between macro-scale metabolism and lived neighborhood reality. Tuffaha & Sallay (2025) in *Scientific Reports* integrated Kennedy's indicator framework with the IABR Rotterdam methodology, evaluating all seven flows at neighborhood level in Amman across four neighborhoods. This approach is directly applicable to Daegu's diverse aging urban fabric.

Korean metabolism studies include water metabolism evaluation across Seoul, Ulsan, and Jeju (Kim et al. 2022, *Resources, Conservation and Recycling*) and Seoul CO2 flux across 9 sites (2022). The **Metabolism of Cities** open database includes extracted data for Seoul-Incheon. Open-source modeling tools include **STAN** (TU Wien, graphical MFA with Sankey diagrams and uncertainty propagation), **ODYM** (Python-based dynamic MFA), and **OMAT** (web-based platform). The emerging trend of coupling digital twins with metabolism dashboards — as Amsterdam's Circular Monitor demonstrates — could be adapted for a Daegu metabolism monitoring module.

---

## 14. Real-time geospatial pipelines connect sensors to interactive maps

The URBANIS data pipeline requires streaming architecture connecting OpenSky aircraft tracking, DOT traffic cameras, and Sentinel satellite imagery to web-based 3D visualization. **WebSocket** (bidirectional, very low latency) is recommended for real-time map updates; **SSE** (server-to-client only) for one-way sensor feeds; **gRPC** (ultra-low latency) for internal microservice communication. A hybrid pattern — WebSocket for frontend, Kafka/Redis for backend — handles most urban platform requirements.

**Pydantic v2** (Rust core) provides the validation layer. **geojson-pydantic** (Development Seed, v2.1.0, RFC 7946 compliant) enables typed validation of GeoJSON features with custom properties — critical for validating AI-generated geospatial outputs:

```python
from geojson_pydantic import Feature, Polygon
from pydantic import BaseModel
class UrbanAnalysis(BaseModel):
    heat_index: float
    green_ratio: float
Feature[Polygon, UrbanAnalysis]  # typed GeoJSON validation
```

**FastAPI** provides native async/await WebSocket support. For message queuing, **Redis Streams** (moderate scale, consumer groups) or **Apache Kafka** (high-throughput, durable retention) serve as coordination layers. The `fastapi-websocket-pubsub` library enables Pub/Sub over WebSocket with multiple backends.

For 3D visualization integration: **CesiumJS** consumes **CZML** (JSON-based time-dynamic format) and OGC **3D Tiles** (streamed via loaders.gl). **deck.gl** renders massive point clouds via Tile3DLayer — Uber demonstrated 355 million data points for Melbourne. The **3DCityDB-Web-Map-Client** connects CityGML models to Cesium, while **pg2b3dm** converts PostGIS 3D geometries to b3dm tiles.

Sentinel data flows through the **STAC API** (pystac-client → Element84 Earth Search or Copernicus Data Space), with **Cloud-Optimized GeoTIFF** enabling efficient partial reads. OpenSky API provides JSON-format aircraft tracking via HTTP polling → Kafka/Redis → WebSocket broadcast. Emerging trends include **HTTP/3 + WebTransport** (lower latency than WebSocket on QUIC), edge computing for sensor-proximate processing, and cloud-native geospatial stacks (STAC + COG + Zarr).

---

## Synthesizing these techniques into the URBANIS platform for Daegu

The 14 techniques described above are not independent modules — they form an interconnected analytical ecosystem. Space syntax graph structures serve as inputs for GNN-based prediction. Morphological tessellation from momepy feeds building typology classification that informs generative AI training data. Computer vision perception scores calibrate against real-time camera feeds through the streaming pipeline. Knowledge graphs encode zoning rules that constrain generative layout proposals. The 15-minute city accessibility engine depends on GTFS-RT data flowing through the WebSocket pipeline, while climate resilience models consume the same Sentinel imagery used for land use change detection.

**Three integration priorities emerge for Daegu specifically.** First, the Gohaud et al. (2025) multi-scalar morphological analysis already provides a validated baseline using exactly the tools (QGIS + momepy) that URBANIS would deploy — extending this with GNN-based prediction and real-time data is the natural next step. Second, Daegu's extreme heat makes the climate resilience stack (InVEST UCM + ENVI-met + OpenFOAM wind corridors) essential, with ECOSTRESS 70m thermal data now available. Third, Korea's advanced smart city infrastructure (E8IGHT digital twins, Busan's 15-minute city program, Seoul S-Map) provides national-level precedent and data ecosystems that Daegu can leverage, while the spatial justice literature documents the displacement risks that the platform should help planners avoid.

The open-source toolchain is remarkably complete: **OSMnx + momepy + PySAL** for morphological analysis, **PyTorch Geometric** for GNN modeling, **Stable Diffusion + ControlNet** for generative design, **Apache Jena + Neo4j** for knowledge graphs, **FastAPI + geojson-pydantic + Redis/Kafka** for streaming pipelines, **CesiumJS + deck.gl** for 3D visualization, **InVEST + SWMM + OpenFOAM** for environmental simulation, **MATSim + SUMO + Mesa** for agent simulation, **TorchGeo + eo-learn** for satellite analysis, and **Valhalla + r5py + Pandana** for accessibility modeling. Nearly every component has a Python API, enabling tight integration within a single platform architecture.
