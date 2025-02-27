# Aurelian: Agentic Universal Research Engine for Literature, Integration, Annotation, and Navigation

| [Documentation](https://monarch-initiative.github.io/oak_agent) |

```
aurelian --help
```

Most commands will start up a different AI agent.

## Troubleshooting

### Installing linkml-store

Some agents require linkml-store pre-indexed. E.g. a mongodb with gocams for cam agent.
Consult the [linkml-store documentation](https://linkml.io/linkml-store/) for more information.

### Semantic search over ontologies

If an agent requires ontology search it will use the semsql/OAK sqlite database.
The first time querying it will use linkml-store to create an LLM index. Requires OAI key.
This may be slow first iteration. Will be cached until your pystow cache regenerates.