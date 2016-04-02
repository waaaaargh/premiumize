class PremiumizeFile:
    """
    Files stored in the Premiumize Cloud
    """

    def __init__(self, data):
        """
        Create an object from a dataset received from the API

        @param data: Dataset from the API
        @type data: C{dict}
        """
        for key in data:
            self.__dict__[key] = data[key]

    def __str__(self):
        return "PremiumizeFile \"%s\"" % self.name
