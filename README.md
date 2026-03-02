# Tab-ViR
Open-domain table retrieval aims to retrieve semantically relevant structured tables from a large-scale corpus in response to natural language queries. Unlike unstructured text, tables store information not only through their textual or numerical content but also through their structural properties, including hierarchical relationships between headers and cells, as well as complex spatial arrangements within the table layout. Existing methods predominantly treat table retrieval as a variant of text retrieval. They struggle to accurately preserve the rich structural semantics of diverse table formats during text serialization. 
Existing methods typically flatten tables into linear text sequences through row-wise or column-wise serialization, inadvertently discarding structural information. The problem becomes particularly acute when processing complex table layouts containing merged cells or irregular alignments, ultimately compromising retrieval performance. Moreover, existing methods struggle to handle embedded images within table cells. Notably, visual representations inherently preserve both structural and content information while being format-agnostic. This insight motivates our exploration of image-based table retrieval, as it can naturally overcome the challenges faced by existing methods. In this paper, we introduce Tab-ViR (Table Retrieval via Visual Representations), a new benchmark that reformulates table retrieval as a multimodal task by treating tables as images. Experiments on Tab-ViR show that this paradigm shift achieved more effective and efficient retrieval performance. Crucially, it eliminates the need for error-prone text conversion, enabling scalable collection and utilization of open-world tables.

## Data
Images can be found[here](https://huggingface.co/datasets/404-not-founds/Tab-ViR)

## Acknowledgements
This project is based on the work of [VLM2Vec](https://github.com/TIGER-AI-Lab/VLM2Vec) and [NQ-Tables](https://github.com/google-research-datasets/natural-questions).  


## License Agreement
All of our open-source models are licensed under the [Apache-2.0](./LICENSE) license.
