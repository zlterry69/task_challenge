class DomainException(Exception):
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(DomainException):
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")


class BusinessRuleError(DomainException):
    def __init__(self, message: str, rule: str = None):
        self.rule = rule
        super().__init__(message, "BUSINESS_RULE_ERROR")


class EntityNotFoundError(DomainException):
    def __init__(self, entity_type: str, entity_id: str = None):
        message = f"{entity_type} not found"
        if entity_id:
            message += f" with id: {entity_id}"
        super().__init__(message, "ENTITY_NOT_FOUND")


class UnauthorizedError(DomainException):
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, "UNAUTHORIZED")


class TaskAssignmentError(BusinessRuleError):
    def __init__(self, message: str = "Cannot assign task"):
        super().__init__(message, "TASK_ASSIGNMENT_ERROR")


class TaskStatusError(BusinessRuleError):
    def __init__(self, message: str = "Invalid task status transition"):
        super().__init__(message, "TASK_STATUS_ERROR")


class TaskListOwnershipError(BusinessRuleError):
    def __init__(self, message: str = "User does not own this task list"):
        super().__init__(message, "TASK_LIST_OWNERSHIP_ERROR")
