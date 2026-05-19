# ADR 1: Use Message Bus for Reactive Side Effects and Small Transaction Boundaries

## Status
Accepted

## Context
In our domain, certain actions (like changing a batch quantity) trigger side effects (like reallocating order lines). We need to decide how to handle these side effects while maintaining domain integrity and system decoupling.

The "One Aggregate per Transaction" rule suggests that a single transaction should only modify one aggregate instance. However, a single business request might require updates to the same aggregate or multiple related aggregates.

## Decision
We will use a Message Bus to handle side effects reactively. When an aggregate is modified, it records domain events. The Message Bus picks up these events and dispatches them to handlers. Each handler is responsible for its own Unit of Work (transaction).

This means a single user request may result in multiple sequential transactions on the same aggregate:
1.  **Transaction 1:** Primary command (e.g., `ChangeBatchQuantity`).
2.  **Transaction 2:** Reaction to event (e.g., `Deallocated` handler initiating a `reallocate`).
3.  **Transaction 3:** Execution of resulting command (e.g., `Allocate`).

## Consequences

### Positive (Benefits)
- **Strict Decoupling:** The primary command handler doesn't need to know about subsequent side effects (e.g., updating read models, sending notifications, or triggering reallocations).
- **Adherence to DDD Principles:** Each transaction strictly modifies only one aggregate instance, keeping the consistency boundary small.
- **Extensibility:** New side effects can be added by creating new event handlers without modifying existing service or domain logic.
- **Optimistic Concurrency:** By using versioning on the aggregate, we ensure that sequential transactions in the same request don't overwrite each other's changes.

### Negative (Trade-offs)
- **Loss of Atomicity:** The entire request is no longer atomic. If Transaction 1 succeeds but Transaction 3 fails, the system is in an "eventually consistent" intermediate state.
- **Complexity:** The flow of a single request is harder to trace as it hops back and forth through the Message Bus.
- **Performance:** Multiple transactions incur more database overhead (commits, locks, connections) than a single large transaction.
- **Requires Resilience:** We must implement retry logic (e.g., using `tenacity`) on the Message Bus to handle transient failures or concurrency conflicts between sequential steps.
