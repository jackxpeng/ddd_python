# ADR 2: Defer Implementation of Transactional Outbox Pattern

## Status
Accepted

## Context
Our current Message Bus publishes events directly to Redis after a successful database commit. This creates a "reliability gap": if the application crashes after the database commit but before the event is published, the event is lost. This is an "at-most-once" delivery guarantee.

The Transactional Outbox pattern would solve this by saving events to an `outbox` table in the same transaction as the domain changes, then using a separate relay process to publish them.

## Decision
We will defer the implementation of the Transactional Outbox pattern and continue using direct, synchronous event publishing for now.

## Rationale
- **Simplicity:** The current implementation is easier to understand, maintain, and test without requiring additional database tables or background relay processes.
- **Stage of Project:** At the current scale and requirements, the risk of a crash in the millisecond window between commit and publication is acceptable.
- **Infrastructure Overhead:** An outbox pattern requires a separate worker process and monitoring, which adds complexity to the deployment and local development environment.

## Consequences

### Positive (Benefits)
- Lower cognitive load and fewer moving parts in the system.
- Faster development cycle for new features.
- No need to manage the "dual write" problem or idempotency on the consumer side yet.

### Negative (Trade-offs)
- **Lack of Atomicity:** We cannot guarantee that an event will be published if the service fails mid-request.
- **Potential for Inconsistency:** External systems (like the Warehouse or Email system) might fall out of sync with the Allocation system.
- **Future Refactoring:** Transitioning to an Outbox later will require changes to the `UnitOfWork` and the introduction of a new infrastructure component.

## Future Trigger
We should reconsider this decision if:
1.  The system moves to a production environment where high availability is required.
2.  The business cost of a "lost event" becomes significant.
3.  The volume of events grows to a point where synchronous publishing impacts API latency.
