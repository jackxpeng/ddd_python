workspace {

    model {
        user = person "User" "A customer or system wanting to allocate stock."
        emailSystem = softwareSystem "Email System" "External email system for sending notifications." "Existing System"
        warehouseSystem = softwareSystem "Warehouse System" "Manages physical inventory and reports batch damage." "External System"
        
        allocationSystem = softwareSystem "Allocation System" "Allows users to allocate stock against batches of inventory." {
            database = container "Database" "Stores stock, batches, and allocation data." "PostgreSQL" "Database"
            messageBroker = container "Message Broker" "Handles asynchronous event messaging." "Redis"
            eventConsumer = container "Event Consumer" "Consumes events from Redis and triggers domain actions." "Python" {
                redisSubscriber = component "Redis Subscriber" "Listens to Redis channels and translates messages to commands." "Python"
                messageBusConsumer = component "Message Bus" "Routes commands to their respective handlers." "Python"
                handlersConsumer = component "Service Handlers" "Orchestrates use cases and manages the domain model." "Python"
                uowConsumer = component "Unit of Work" "Manages atomic transactions." "Python"
                domainModelConsumer = component "Domain Model" "Contains core business logic." "Python"
                repositoryConsumer = component "Repository" "Abstracts data access." "Python"

                # Component relationships
                redisSubscriber -> messageBusConsumer "Dispatches commands to"
                messageBusConsumer -> handlersConsumer "Routes to"
                handlersConsumer -> uowConsumer "Uses for transactions"
                handlersConsumer -> domainModelConsumer "Mutates"
                uowConsumer -> repositoryConsumer "Provides access to"
                repositoryConsumer -> domainModelConsumer "Loads and saves"
                
                # External connections
                repositoryConsumer -> database "Reads from and writes to" "SQLAlchemy"
                uowConsumer -> database "Commits transactions to" "SQLAlchemy"
            }
            
            webApi = container "Web API" "Provides stock allocation functionality via a JSON/HTTP API." "Python/Flask" {
                api = component "API Entrypoint" "Flask application providing the HTTP interface." "Python/Flask"
                messageBus = component "Message Bus" "Routes commands and events to their respective handlers." "Python"
                handlers = component "Service Handlers" "Orchestrates use cases and manages the domain model." "Python"
                uow = component "Unit of Work" "Manages atomic transactions and provides access to the repository." "Python"
                domainModel = component "Domain Model" "Contains core business logic, aggregates, and entities." "Python"
                repository = component "Repository" "Abstracts data access to the database." "Python"
                readModelViews = component "Read Model Views" "Executes raw SQL queries for fast reads, bypassing the domain model." "Python"
                emailAdapter = component "Email Adapter" "Sends external emails." "Python"
                redisPublisher = component "Redis Publisher" "Publishes events to Redis." "Python"

                # Component relationships
                api -> messageBus "Dispatches commands to"
                api -> readModelViews "Queries data from"
                readModelViews -> uow "Uses for database session"
                messageBus -> handlers "Routes to"
                handlers -> uow "Uses for transactions"
                handlers -> domainModel "Mutates"
                uow -> repository "Provides access to"
                uow -> messageBus "Collects new events from domain and dispatches to"
                repository -> domainModel "Loads and saves"
                messageBus -> emailAdapter "Dispatches external events to"
                messageBus -> redisPublisher "Dispatches external events to"
                
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
