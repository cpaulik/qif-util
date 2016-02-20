
class LedgerWriter:

    def __init__(self, target):
        self.target = target

    def write(self, date, payee, amount, source, target):
        self.target.write("{} * {}\n".format(date.strftime("%Y/%m/%d"),
                                             payee))
        self.target.write("    {:<51}{:>.2f} EUR\n".format(target, -amount))
        self.target.write("    {:<51}{:>.2f} EUR\n\n".format(source, amount))
