class SomUsersException(Exception):
    def __init__(self, text):
        self.exc_type = 'error'
        self.text = text
        super(SomUsersException, self).__init__(self.text)

    @property
    def code(self):
        return self.__class__.__name__

    def to_dict(self):
        return dict(
            code=self.code,
            error=self.text,
        )


class NoSuchUser(SomUsersException):
    def __init__(self):
        super(NoSuchUser, self).__init__(
            text="User does not exist"
        )

class NoDocumentVersions(SomUsersException):
    def __init__(self, document):
        super(NoDocumentVersions, self).__init__(
            text="Document {} has no version available to sign".format(document)
        )

class FailSendEmail(SomUsersException):
    def __init__(self, message):
        super(FailSendEmail, self).__init__(
            text=message or "Error sending email",
        )

