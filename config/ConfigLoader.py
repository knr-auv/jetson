import json
import pathlib
class ConfigLoader:
    @staticmethod
    def LoadPIDs(FileName):
        with open(FileName) as fd:
            data = json.load(fd)
            ret = []
            for key in data:
                data[key]
                for i in data[key]:
                    ret+=[data[key][i]]
            return ret

if __name__=="__main__":
    data = ConfigLoader.LoadPIDs("config/PID_simulation.json")
    print(data)



