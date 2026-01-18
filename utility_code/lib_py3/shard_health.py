"""NetworkRelay ShardHealth Python port"""

class ShardHealth():
    def __init__(self, json_data):
        self._json = json_data


    @staticmethod
    def default_target_health():
        return ShardHealth({
            "gcHealth": {
                "averageConcurrentFreed": 0.0,
                "averageConcurrentTime": 0.0,
                "averageOldGenFreed": 0.0,
                "averageOldGenTime": 0.0,
                "averageOverallFreed": 0.0,
                "averageOverallTime": 0.0,
                "averageYoungGenFreed": 0.0,
                "averageYoungGenTime": 0.0,
                "concurrentCycleInInterval": 0.0,
                "oldGenCycleInInterval": 0.0,
                "overallCyclesInInterval": 0.0,
                "youngGenCycleInInterval": 0.0,
            },
            "healthScore": 0.21,
            "memoryHealth": 0.3,
            "tickHealth": 0.7,
        })


    @staticmethod
    def zero_health():
        return ShardHealth({
            "gcHealth": {
                "averageConcurrentFreed": 0.0,
                "averageConcurrentTime": 0.0,
                "averageOldGenFreed": 0.0,
                "averageOldGenTime": 0.0,
                "averageOverallFreed": 0.0,
                "averageOverallTime": 0.0,
                "averageYoungGenFreed": 0.0,
                "averageYoungGenTime": 0.0,
                "concurrentCycleInInterval": 0.0,
                "oldGenCycleInInterval": 0.0,
                "overallCyclesInInterval": 0.0,
                "youngGenCycleInInterval": 0.0,
            },
            "healthScore": 0.0,
            "memoryHealth": 0.0,
            "tickHealth": 0.0,
        })


    def memory_health(self):
        return self._json.get("memoryHealth", 0.0)


    def tick_health(self):
        return self._json.get("tickHealth", 0.0)


    def health_score(self):
        return self._json.get("healthScore", 0.0)


    def gc_health(self):
        gc_health = self._json.get("gcHealth", None)
        if gc_health:
            return gc_health

        return {
            "averageConcurrentFreed": 0.0,
            "averageConcurrentTime": 0.0,
            "averageOldGenFreed": 0.0,
            "averageOldGenTime": 0.0,
            "averageOverallFreed": 0.0,
            "averageOverallTime": 0.0,
            "averageYoungGenFreed": 0.0,
            "averageYoungGenTime": 0.0,
            "concurrentCycleInInterval": 0.0,
            "oldGenCycleInInterval": 0.0,
            "overallCyclesInInterval": 0.0,
            "youngGenCycleInInterval": 0.0,
        }
