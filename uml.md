# PawPal+ UML Class Diagram

```mermaid
classDiagram
    class Task {
        -str title
        -str description
        -int duration_minutes
        -str priority
        -str category
        -str frequency
        -bool completed
        +__post_init__() None
        +priority_value() int
        +mark_complete() None
        +reset() None
        +__str__() str
    }

    class Pet {
        -str name
        -str species
        -str special_needs
        -list~Task~ tasks
        +add_task(task) None
        +remove_task(title) None
        +pending_tasks() list~Task~
        +tasks_by_category(category) list~Task~
        +completion_summary() str
        +reset_all_tasks() None
        +__str__() str
    }

    class Owner {
        -str name
        -int available_minutes
        -list~str~ preferences
        -list~Pet~ pets
        +__post_init__() None
        +add_pet(pet) None
        +remove_pet(name) None
        +all_tasks() list~Task~
        +all_pending_tasks() list~Task~
        +__str__() str
    }

    class ScheduleEntry {
        -Task task
        -str pet_name
        -int start_minute
        -str reason
        +end_minute() int
        +__str__() str
    }

    class Scheduler {
        -Owner owner
        -list~ScheduleEntry~ _last_schedule
        +add_task(pet_name, task) None
        +remove_task(pet_name, title) None
        +get_all_pending() list~tuple~
        +generate_schedule() list~ScheduleEntry~
        +mark_scheduled_complete() None
        +explain_schedule(entries) str
        -_find_pet(pet_name) Pet
        -_build_reason(task, scheduled) str
        -_skipped_tasks(entries) list~tuple~
    }

    Owner "1" o-- "1..*" Pet : pets
    Pet "1" o-- "*" Task : tasks
    Scheduler --> Owner : uses
    Scheduler ..> Pet : delegates to
    Scheduler --> ScheduleEntry : produces
    ScheduleEntry --> Task : wraps
```
