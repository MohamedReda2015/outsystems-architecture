# Audit trail

Source: OutSystems 11 docs *Audit Trail*.

## Two kinds
- **Business audit**: who did what, when, and the values before and after. Driven by compliance (SOX, HIPAA, GLBA, FISMA, local law) and business needs (financial transactions, customer communications, access to sensitive data, sessions from login to logout).
- **Platform audit**: OutSystems' built-in technical logs (errors, integrations, screen requests, slow queries) in Service Center → Monitoring. Logging must be enabled per module. Logs are kept for about 4 weeks by default, so export them with an ETL process if they need to be kept longer.

Start with the minimum, then evolve. Decide the content to log, data integrity (no duplicates), a universal format, consistent timestamps, the retention period, and encryption plus Auditor roles for sensitive data.

## Patterns (simple → advanced)
1. **LogMessage wrapper**: `Audit_Lib` with a public `MyLogMessage` that calls the system `LogMessage`. View the logs in Service Center under General, by module.
2. **Centralized audit (recommended)**:
   - own log levels and typed messages;
   - logging switched on or off per app through site properties or a scaffolded back office, with no redeploy;
   - writes go fast into a **`QuickLog`** staging entity, and a timer moves them into **`AuditLog`**.
3. **Extended centralized audit**: a Foundation app `Audit_Lib` with an **async** public API:
   - `Audit_Create`, `Audit_Update`, `Audit_Delete`: one record created, changed or deleted;
   - `Audit_OperationLog`: an operation done by a user or the system;
   - `Audit_GenericLog`: any other information, including debug messages;
   - `Audit_ListFilterLog`: query the logs.

   Each call is routed by message type, either to `LogMessage_IS` (the platform log) or to `ExternalAudit_IS` (staging table, then a timer sends it to the external system).
4. **Advanced, NoSQL**: for very high volumes, schema-less records or long retention, store the audit in a NoSQL database (e.g. DynamoDB through a Forge connector). Use generic records: `ObjectName`, `Operation`, `JsonObject`, `UserId`, `CreatedOn`, `EntityId1..3`. Audit records have no foreign keys to the source data and carry their own retention policy.

## Entity read-only pattern
Expose entities read-only, so every create, update and delete goes through the owning module's CRUD actions, which log the change. Bulk SQL updates can only be logged as one operation.

## House conventions
- Audit columns on business entities: `CreatedBy`, `CreatedOn`, `UpdatedBy`, `UpdatedOn`, set only inside the CRUD wrappers.
- Use a `<Entity>History` entity for business status trails (status, actor, timestamp, comment), written by the BL's state-transition actions.
- For external users with no platform user, use the actor format `<Provider>:<ExternalId>`.
