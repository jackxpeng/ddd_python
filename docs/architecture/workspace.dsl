workspace "Allocation Workspace" "Architecture of the Allocation System" {
    configuration {
        scope softwaresystem
    }
    model {
        user = person "User" "A customer or system wanting to allocate stock."
        emailSystem = softwareSystem "Email System" "External email system for sending notifications." "Existing System"
        warehouseSystem = softwareSystem "Warehouse System" "Manages physical inventory and reports batch damage." "External System"
        
        allocationSystem = softwareSystem "Allocation System" "Allows users to allocate stock against batches of inventory." {
            database = container "Database" "Stores stock, batches, and allocation data." "PostgreSQL" "Database"
            messageBroker = container "Message Broker" "Handles asynchronous event messaging." "Redis"
            eventConsumer = container "Event Consumer" "Consumes events from Redis and triggers domain actions." "Python" {
                redisSubscriber = component "Redis Subscriber" "Listens to Redis channels and translates messages to commands." "Python"
                bootstrapConsumer = component "Bootstrap" "Wires up dependency injection and initializes the Message Bus." "Python"
                messageBusConsumer = component "Message Bus" "Routes commands to their respective handlers." "Python"
                handlersConsumer = component "Service Handlers" "Orchestrates use cases and manages the domain model." "Python"
                uowConsumer = component "Unit of Work" "Manages atomic transactions." "Python"
                domainModelConsumer = component "Domain Model" "Contains core business logic." "Python"
                repositoryConsumer = component "Repository" "Abstracts data access." "Python"
                emailAdapterConsumer = component "Email Adapter" "Sends external emails." "Python"
                redisPublisherConsumer = component "Redis Publisher" "Publishes events to Redis." "Python"

                # Component relationships
                redisSubscriber -> bootstrapConsumer "Initializes" "Method Call"
                bootstrapConsumer -> messageBusConsumer "Injects handlers into" "Method Call"
                redisSubscriber -> messageBusConsumer "Dispatches commands to" "Method Call"
                messageBusConsumer -> handlersConsumer "Routes to" "Method Call"
                handlersConsumer -> uowConsumer "Uses for transactions" "Method Call"
                handlersConsumer -> domainModelConsumer "Mutates" "Method Call"
                messageBusConsumer -> uowConsumer "Collects new events from domain" "Method Call"
                uowConsumer -> repositoryConsumer "Provides access to" "Method Call"
                repositoryConsumer -> domainModelConsumer "Loads and saves" "Method Call"
                handlersConsumer -> emailAdapterConsumer "Dispatches external events to" "Method Call"
                handlersConsumer -> redisPublisherConsumer "Dispatches external events to" "Method Call"
                
                # External connections
                repositoryConsumer -> database "Reads from and writes to" "SQLAlchemy"
                uowConsumer -> database "Commits transactions to" "SQLAlchemy"
                emailAdapterConsumer -> emailSystem "Sends emails using" "SMTP"
                redisPublisherConsumer -> messageBroker "Publishes events to" "Redis Pub/Sub"
            }
            
            webApi = container "Web API" "Provides stock allocation functionality via a JSON/HTTP API." "Python/Flask" {
                api = component "API Entrypoint" "Flask application providing the HTTP interface." "Python/Flask"
                messageBus = component "Message Bus" "Routes commands and events to their respective handlers." "Python"
                handlers = component "Service Handlers" "Orchestrates use cases and manages the domain model." "Python"
                uow = component "Unit of Work" "Manages atomic transactions and provides access to the repository." "Python"
                domainModel = component "Domain Model" "Contains core business logic, aggregates, and entities." "Python"
                repository = component "Repository" "Abstracts data access to the database." "Python"
                readModelViews = component "Read Model Views" "Executes raw SQL queries for fast reads, bypassing the domain model." "Python"
                bootstrap = component "Bootstrap" "Wires up dependency injection and initializes the Message Bus." "Python"
                emailAdapter = component "Email Adapter" "Sends external emails." "Python"
                redisPublisher = component "Redis Publisher" "Publishes events to Redis." "Python"

                # Component relationships
                api -> bootstrap "Initializes" "Method Call"
                bootstrap -> messageBus "Injects handlers into" "Method Call"
                api -> messageBus "Dispatches commands to" "Method Call"
                api -> readModelViews "Queries data from" "Method Call"
                readModelViews -> uow "Uses for database session" "Method Call"
                messageBus -> handlers "Routes to" "Method Call"
                handlers -> uow "Uses for transactions" "Method Call"
                handlers -> domainModel "Mutates" "Method Call"
                messageBus -> uow "Collects new events from domain" "Method Call"
                uow -> repository "Provides access to" "Method Call"
                repository -> domainModel "Loads and saves" "Method Call"
                handlers -> emailAdapter "Dispatches external events to" "Method Call"
                handlers -> redisPublisher "Dispatches external events to" "Method Call"
                
                # External connections from components
                repository -> database "Reads from and writes to" "SQLAlchemy"
                uow -> database "Commits transactions to" "SQLAlchemy"
                emailAdapter -> emailSystem "Sends emails using" "SMTP"
                redisPublisher -> messageBroker "Publishes events to" "Redis Pub/Sub"
            }
        }

        # Relationships
        user -> api "Makes API calls to" "JSON/HTTP"
        redisSubscriber -> messageBroker "Subscribes to events/commands from" "Redis Pub/Sub"
        warehouseSystem -> messageBroker "Publishes inventory change commands to" "Redis Pub/Sub"
    }

    views {
        systemContext allocationSystem "SystemContext" {
            include *
            autoLayout
        }

        container allocationSystem "Containers" {
            include *
            autoLayout
        }

        component webApi "WebApiComponents" {
            include *
            autoLayout
        }

        component eventConsumer "EventConsumerComponents" {
            include *
            autoLayout
        }

        styles {
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Person" {
                shape person
                background #08427b
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
        }
    }

}
