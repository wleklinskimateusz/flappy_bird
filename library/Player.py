class Player:
    def __init__(self):
        self.id = 0
        self.nick = ""
        self.best_score = 0
        self.sum_score = 0
        self.games = 0
        self.filename = ""

    def __repr__(self):
        return self.nick

    def get_data(self):
        with open(self.filename, "r") as file:
            data = []
            for x, line in enumerate(file.readlines()):
                data.append(int(line.replace("\n", "")))
            self.id = data[0]
            self.best_score = data[1]
            self.sum_score = data[2]
            self.games = data[3]


    def save_data(self):
        with open(self.filename, "w") as file:
            file.write(str(self.id) + "\n")
            file.write(str(self.best_score) + "\n")
            file.write(str(self.sum_score) + "\n")
            file.write(str(self.games) + "\n")

    def print_data(self):
        print([self.best_score, self.sum_score, self.games])

    def get_average_score(self):
        return self.sum_score / self.games
