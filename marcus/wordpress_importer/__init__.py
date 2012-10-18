class BasePipeline(object):
    replaced_data = {}

    def __init__(self, data):
        self.data = data
        self.replaced_data = {}

    def output(self):
        for field in self.data:
            replacer_name = 'replace_{field}'.format(field=field)
            if hasattr(self, replacer_name):
                self.replaced_data[field] = getattr(self, replacer_name)(self.data[field])
            else:
                self.replaced_data[field] = self.data[field]
        return self.replaced_data
