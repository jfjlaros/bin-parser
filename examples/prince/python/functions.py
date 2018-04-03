from bin_parser import BinReadFunctions, BinWriteFunctions


class PrinceReadFunctions(BinReadFunctions):
    def min(self, data):
        return super(PrinceReadFunctions, self).struct(data, '<h') - 1

    def sec(self, data):
        return super(PrinceReadFunctions, self).struct(data, '<h') // 12


class PrinceWriteFunctions(BinWriteFunctions):
    def min(self, minutes):
        return super(PrinceWriteFunctions, self).struct(minutes + 1, '<h')

    def sec(self, seconds):
        return super(PrinceWriteFunctions, self).struct(seconds * 12, '<h')
