from _global import global_logger


class PronounTool:
    """
    找出不同种类的pro
    """

    def __init__(self):
        self._pronoun_word = {
            "city": [line.strip() for line in open("./assets/pronoun/city.txt", "r", encoding="utf-8")],
            "food": [line.strip() for line in open("./assets/pronoun/food.txt", "r", encoding="utf-8")],
            "medical": [line.strip() for line in open("./assets/pronoun/medical.txt", "r", encoding="utf-8")],
            "sport": [line.strip() for line in open("./assets/pronoun/medical.txt", "r", encoding="utf-8")],
            "people_name": [line.strip() for line in open("./assets/pronoun/star.txt", "r", encoding="utf-8")],
            "weather": [line.strip() for line in open("./assets/pronoun/weather.txt", "r", encoding="utf-8")],
            "animal": [line.strip() for line in open("./assets/pronoun/animal.txt", "r", encoding="utf-8")],
            "movie": [line.strip() for line in open("./assets/pronoun/movie.txt", "r", encoding="utf-8")],
        }

    def extract(self, query):
        result = []
        for type_, value in self._pronoun_word.items():
            words = value
            for word in words:
                if word in query:
                    result.append({"type": type_, "pronoun": word})
        global_logger.info("query:{} pronoun:{}".format(query, result))
        return result
