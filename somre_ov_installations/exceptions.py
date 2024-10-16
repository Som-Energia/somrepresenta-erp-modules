class SomInstallationsException(Exception):
    def __init__(self, text):
        self.exc_type = 'error'
        self.text = text
        super(SomInstallationsException, self).__init__(self.text)

    @property
    def code(self):
        return self.__class__.__name__

    def to_dict(self):
        return dict(
            code=self.code,
            error=self.text,
        )


class ContractWithoutInstallation(SomInstallationsException):
    def __init__(self, contract_number):
        super(ContractWithoutInstallation, self).__init__(
            text="No installation found for contract '{}'".format(contract_number))
        self.contract_number = contract_number

    def to_dict(self):
        return dict(
            super(ContractWithoutInstallation, self).to_dict(),
            contract_number=self.contract_number,
        )

class ContractNotExists(SomInstallationsException):
    def __init__(self):
        super(ContractNotExists, self).__init__(
            text="Contract does not exist")

class UnauthorizedAccess(SomInstallationsException):
    def __init__(self, username, resource_type, resource_name):
        super(UnauthorizedAccess, self).__init__(
            text="User {username} cannot access the {resource_type} '{resource_name}'".format(
                username=username,
                resource_type=resource_type,
                resource_name=resource_name,
            ))
        self.username = username
        self.resource_type = resource_type
        self.resource_name = resource_name

    def to_dict(self):
        return dict(
            super(UnauthorizedAccess, self).to_dict(),
            username=self.username,
            resource_type=self.resource_type,
            resource_name=self.resource_name,
        )
