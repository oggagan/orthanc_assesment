# Component catalog

For run and verify commands, see [Runbook](../operations/runbook.md).

| Component           | Responsibility                                      | Doc |
|---------------------|-----------------------------------------------------|-----|
| Ingestion API       | Receive Orthanc webhook / manual trigger, generate correlation ID, invoke pipeline | [ingestion-api.md](ingestion-api.md) |
| Pipeline            | Orchestrate extract → DB → storage → Kafka; DLQ on failure | [pipeline.md](pipeline.md) |
| Orthanc integration | Fetch studies and DICOM bytes from Orthanc REST     | [orthanc-integration.md](orthanc-integration.md) |
| Persistence         | Canonical DB schema and local raw DICOM storage     | [persistence.md](persistence.md) |
| Messaging           | Kafka topics, event and DLQ payloads, producer config | [messaging.md](messaging.md) |
| Observability       | Correlation ID, logging, health, metrics             | [observability.md](observability.md) |
