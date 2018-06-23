class ProjectorError(Exception):
    """Exception for failures in projector communication"""
    pass

class InvalidCommandError(Exception):
    """Exception for invalid input"""
    pass

class ConfigurationError(Exception):
    """Exception for invalid configuration"""
    pass
